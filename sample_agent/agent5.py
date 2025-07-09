from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import (
    AgentState,
    AgentStateWithStructuredResponse,
)
from langchain.chat_models import init_chat_model
from typing import Annotated
from langgraph.types import interrupt
from langchain_core.tools import InjectedToolCallId
import os
from langgraph.graph import StateGraph
from langgraph.constants import END
from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import (
    create_handoff_tool,
    SwarmState,
    add_active_agent_router,
)
from sample_agent.utils import (
    create_handoff_tool_with_state_propagation,
    create_handoff_tool_with_task
)


model = init_chat_model("openai:gpt-4o-mini", temperature=0)
model_groq = model  # init_chat_model("groq:llama-3.1-8b-instant", temperature=0)

MAIN_AGENT_PROMPT = """You are the Main Coordination Agent responsible for task orchestration and completion.

CORE RESPONSIBILITIES:
1. Analyze incoming tasks and develop a strategic execution plan
2. Gather necessary information from users when requirements are unclear
3. Delegate specialized tasks to appropriate expert agents
4. Coordinate between agents to ensure seamless task completion

WORKFLOW PROCESS:
1. ANALYZE: Break down the user's request and identify required expertise
2. PLAN: Structure a clear strategy outlining steps and agent assignments
3. GATHER: Use `ask_user` tool to collect missing information before proceeding
4. DELEGATE: Hand off specific, well-defined subtasks to specialized agents
5. COORDINATE: Monitor progress and facilitate inter-agent communication

HANDOFF PROTOCOL:
- Always provide clear, specific instructions when transferring tasks
- Include relevant context and expected deliverables
- Ensure each agent receives the exact information needed for their specialization

Remember: Strategic planning before action ensures optimal task completion."""


def get_weather(location: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """
    Get the weather for a given location.
    """
    print(f"Getting weather for {location}")

    return Command(
        update={
            "location": location,
            "temperature": "70 degrees",
            "date": "2025-01-01",
            "time": "12:00:00",
            "tool_call_id": tool_call_id,
            "messages": [
                ToolMessage(
                    f"The weather for {location} is 70 degrees.",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def calculate_math(expression: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """
    Calculate a simple math expression.
    Example: "2 + 3" or "10 * 5"
    """
    print(f"Calculating math for {expression}")
    try:
        if "+" in expression:
            parts = expression.split("+")
            result = sum(float(part.strip()) for part in parts)
        elif "*" in expression:
            parts = expression.split("*")
            result = 1
            for part in parts:
                result *= float(part.strip())
        elif "-" in expression:
            parts = expression.split("-")
            result = float(parts[0].strip()) - float(parts[1].strip())
        elif "/" in expression:
            parts = expression.split("/")
            result = float(parts[0].strip()) / float(parts[1].strip())
        else:
            result = float(expression.strip())

        return Command(
            update={
                "math_expression": expression,
                "math_result": result,
                "messages": [
                    ToolMessage(
                        f"The result of {expression} is {result}",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )
    except:
        return f"Could not calculate {expression}. Please use format like '2 + 3' or '10 * 5'"


def pre_hook_supervisor_node(state, config: RunnableConfig):
    print(f"Pre-hook supervisor: {state}")

    return state


def post_hook_supervisor_node(state, config: RunnableConfig):
    print(f"Post-hook supervisor: {state}")

    return state


def compile_workflow(workflow: StateGraph):
    is_langgraph_api = (
        os.environ.get("LANGGRAPH_API", "false").lower() == "true"
        or os.environ.get("LANGGRAPH_API_DIR") is not None
    )

    if is_langgraph_api:
        return workflow.compile()
    else:
        from langgraph.checkpoint.memory import MemorySaver

        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)


def ask_user(question_to_user: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    "This tool is used to ask the user any question. Its important always ask for things to make sure you're using the right information."
    user_response = interrupt(
        {
            "type": "question",
            "question": question_to_user,
            "tool_call_id": tool_call_id,
        }
    )
    print(f"User response: {user_response}")

    return f"The user answered with: {user_response.values()}"


def strip_tool_messages_node(state: dict) -> Command:
    from langchain_core.messages import ToolMessage, AIMessage, HumanMessage

    def is_valid_message(m):
        return not isinstance(m, ToolMessage)

    cleaned = [m for m in state["messages"] if is_valid_message(m)]
    return Command(update={"messages": cleaned})


def create_multi_agent_system_swarm_mode():
    """Create the multi-agent system with supervisor"""

    # State definitions for tracking data across agents
    class FullState(AgentState):
        temperature: float
        location: str
        weather: str
        math_expression: str
        math_result: str

    class AliceState(AgentStateWithStructuredResponse):
        math_expression: str
        math_result: str

    class AliceOutput(BaseModel):
        math_expression: str
        math_result: str

    class BobState(AgentStateWithStructuredResponse):
        location: str
        weather: str
        temperature: float

    class BobOutput(BaseModel):
        location: str
        weather: str
        temperature: float

    # Create Main Agent - Coordination and Planning
    print("> Creating Main Agent...")
    main_agent_model = init_chat_model("openai:gpt-4o-mini", temperature=0)
    main_agent_tools = [
        ask_user,
        create_handoff_tool(
            agent_name="Alice",
            description="Transfer to Alice, she can help with any math",
        ),
        create_handoff_tool_with_task(
            agent_name="Bob", description="Transfer to Bob, he can help with weather"
        ),
    ]
    main_agent_model_bind_tools = main_agent_model.bind_tools(
        main_agent_tools,
        parallel_tool_calls=False,
    )

    main_agent = create_react_agent(
        main_agent_model_bind_tools,
        main_agent_tools,
        prompt=MAIN_AGENT_PROMPT,
        name="main_agent",
        state_schema=FullState,
    )

    # Create Alice - Math Specialist
    print("> Creating Alice (Math Specialist)...")
    alice_model = init_chat_model("openai:gpt-4o-mini", temperature=0)
    alice_tools = [
        calculate_math,
        create_handoff_tool(
            agent_name="Bob", description="Transfer to Bob, he can help with weather"
        ),
        create_handoff_tool(
            agent_name="main_agent",
            description="Use this tool to send or ask the user for information to complete the task.",
        ),
    ]
    alice_model_bind_tools = alice_model.bind_tools(
        alice_tools,
        parallel_tool_calls=False,
    )

    alice = create_react_agent(
        alice_model_bind_tools,
        alice_tools,
        prompt="You are Alice, a calculator expert. You are given a math expression and you need to calculate the result. If you need to ask the user for information, handoff to the main_agent.",
        name="Alice",
        state_schema=AliceState,
        response_format=AliceOutput,
    )

    # Create Bob - Weather Specialist
    print("> Creating Bob (Weather Specialist)...")
    bob_model = init_chat_model("openai:gpt-4o-mini", temperature=0)
    bob_tools = [
        ask_user,
        get_weather,
        create_handoff_tool_with_state_propagation(
            agent_name="Alice",
            description="Transfer to Alice, she can help with any math or any calculation",
            propagate_keys=["location", "weather", "temperature"],
        ),
        create_handoff_tool(
            agent_name="main_agent",
            description="Use this tool to send or ask the user for information to complete the task.",
        ),
    ]
    bob_model_bind_tools = bob_model.bind_tools(
        bob_tools,
        parallel_tool_calls=False,
    )

    bob = create_react_agent(
        bob_model_bind_tools,
        bob_tools,
        prompt="You are Bob, you speak like a pirate and you are a weather specialist only. You are given a location and you need to return the weather for that location using the `get_weather` tool. If you need any user information, handoff back to the main_agent. To get any information that the user is thinking, handoff back to the main_agent. Never make anything out of your capabilities. You ",
        name="Bob",
        state_schema=BobState,
        response_format=BobOutput,
    )

    # Create Swarm State that combines SwarmState with our custom state
    class FullSwarmState(SwarmState, FullState):
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
        .add_node(alice, destinations=("main_agent", "Bob"))
        .add_node(bob, destinations=("main_agent", "Alice"))
        .add_node("cleanup_messages", strip_tool_messages_node)
        .add_edge("cleanup_messages", "main_agent")
    )
    # workflow = workflow.set_finish_point("cleanup_messages")
    # Add the router that enables tracking of the last active agent
    workflow = add_active_agent_router(
        builder=workflow,
        route_to=["main_agent", "Alice", "Bob"],
        default_active_agent="main_agent",
    )

    # Compile the workflow with memory checkpointer
    print("> Compiling workflow...")
    graph = compile_workflow(workflow)

    return graph


# Create the multi-agent system
graph = create_multi_agent_system_swarm_mode()
