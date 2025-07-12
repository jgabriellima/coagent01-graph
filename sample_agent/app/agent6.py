from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph
from langgraph_swarm import SwarmState, add_active_agent_router, create_handoff_tool
from sample_agent.utils import (
    create_handoff_tool_with_task,
    compile_workflow,
    create_handoff_tool_with_state_propagation,
)
from sample_agent.agents.main_agent import build_main_agent, MainAgentState
from sample_agent.agents.alice_agent import build_alice_agent
from sample_agent.agents.bob_agent import build_bob_agent
from langsmith import traceable

def create_multi_agent_system_swarm_mode():
    """Create the multi-agent system with supervisor"""

    # Setup LLM
    llm_model = "openai:gpt-4o-mini"

    # Create handoff tools
    main_agent_handoff_tool = create_handoff_tool_with_task(
        agent_name="main_agent",
        description="Use this to handoff to the main agent, responsible for managing the conversation, the tasks and main interactions with the user.",
    )
    alice_handoff_tool = create_handoff_tool_with_task(
        agent_name="Alice",
        description="Use this to handoff to Alice, a math expert agent capable of handling calculations.",
    )
    bob_handoff_tool = create_handoff_tool_with_task(
        agent_name="Bob",
        description="Use this to handoff to Bob, a weather specialist agent who speaks like a pirate.",
    )

    # Create Main Agent - Coordination and Planning
    main_agent = build_main_agent(
        init_chat_model(llm_model, temperature=0),
        [alice_handoff_tool, bob_handoff_tool],
    )
    alice = build_alice_agent(
        init_chat_model(llm_model, temperature=0),
        [main_agent_handoff_tool, bob_handoff_tool],
    )
    bob = build_bob_agent(
        init_chat_model(llm_model, temperature=0),
        [main_agent_handoff_tool, alice_handoff_tool],
    )

    class FullSwarmState(SwarmState, MainAgentState):
        temperature: float
        location: str
        weather: str
        math_expression: str
        math_result: str

    # Build the workflow graph
    print("> Building workflow graph...")
    workflow = (
        StateGraph(FullSwarmState)
        .add_node(
            main_agent,
            destinations=(
                "Alice",
                "Bob",
            ),
        )
        .add_node(alice, destinations=("Main_Agent", "Bob"))
        .add_node(bob, destinations=("Main_Agent", "Alice"))
    )
    workflow = add_active_agent_router(
        builder=workflow,
        route_to=["Main_Agent", "Alice", "Bob"],
        default_active_agent="Main_Agent",
    )

    # Compile the workflow with memory checkpointer
    print("> Compiling workflow...")
    graph = compile_workflow(workflow)

    return graph


# Create the multi-agent system
graph = create_multi_agent_system_swarm_mode()
