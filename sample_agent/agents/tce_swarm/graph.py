"""
Swarm Architecture Graph
Production-grade multi-agent system for institutional processes
"""

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph
from langgraph_swarm import add_active_agent_router
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
from sample_agent.agents.tce_swarm.configuration import ChatContasConfiguration
from langgraph_swarm import SwarmState

# Import agents
from sample_agent.agents.tce_swarm.main_agent import build_main_agent
from sample_agent.agents.tce_swarm.search_agent import build_search_agent

# Import RAG pipeline (replaces RAG agent)
from sample_agent.agents.tce_swarm.rag.graph import build_rag_agent

# Import state
from sample_agent.agents.tce_swarm.states import (
    ChatContasStateOutput,
    ChatContasInputState,
)

# Import utils
from sample_agent.utils import (
    compile_workflow,
    create_handoff_tool_with_state_propagation,
    create_handoff_tool_with_task
)


@traceable(
    name="Institutional_Swarm_System",
    tags=["institutional", "multi-agent", "swarm", "production"],
)
def create_swarm_system():
    """
    Create the production-grade institutional swarm system.

    **Swarm Architecture Principles:**
    - Any agent can respond directly to the user
    - Handoffs are optional and based on specific needs
    - No mandatory consolidation through Main Agent
    - Each agent is autonomous and specialized
    - Routing is intelligent and context-aware

    Returns:
        Compiled workflow graph with full instrumentation
    """

    # =====  INSTRUMENTATION SETUP =====
    print("🔧 Initializing Institutional Swarm System...")
    print("📊 Setting up instrumentation and monitoring...")

    # ===== MODEL CONFIGURATION =====
    llm_model = "openai:gpt-4o-mini"
    # llm_model = "groq:llama-3.3-70b-versatile"
    model_config = {
        "temperature": 0.1,  # Low temperature for consistent responses
        "max_tokens": 2000,
        "top_p": 0.95,
    }

    print(f"🤖 Using model: {llm_model}")
    print(f"⚙️  Model config: {model_config}")

    # ===== HANDOFF TOOLS =====
    print("🔄 Creating handoff tools...")

    # Main Agent handoff tool - Optional coordination
    main_agent_handoff = create_handoff_tool_with_state_propagation(
        agent_name="Main_Agent",
        description="Use this to handoff to the main agent for complex coordination or general institutional queries or explanation about capabilities of the system.",
    )

    # RAG Agent handoff tool - Complete document processing pipeline
    rag_agent_handoff = create_handoff_tool_with_task(
        agent_name="RAG_Agent",
        description="Use this to handoff to the RAG agent for institutional document retrieval and analysis. Specializes in TCE-PA official documents including legislation, resolutions, administrative acts, and jurisprudence.  Returns structured responses with query context and formatted content ready for institutional use.",
    )

    # Search Agent handoff tool - Optional system/web search
    search_agent_handoff = create_handoff_tool_with_state_propagation(
        agent_name="Search_Agent",
        description="Use this to handoff to the search agent for expediente, process, and web search queries.",
    )

    # ===== AGENT INITIALIZATION =====
    print("🤖 Initializing agents...")

    # Main Agent - Initial Coordinator (can respond directly)
    main_agent = build_main_agent(
        init_chat_model(llm_model, **model_config),
        [rag_agent_handoff, search_agent_handoff],
    )

    # Search Agent - System/Web Specialist (can respond directly)
    search_agent = build_search_agent(
        init_chat_model(llm_model, **model_config),
        [main_agent_handoff, rag_agent_handoff],
    )

    rag_agent = build_rag_agent()

    print("✅ All agents initialized successfully")
    print("🔄 RAG Agent is now the complete RAG pipeline (simplified architecture)")

    # ===== WORKFLOW GRAPH CONSTRUCTION =====
    print("🔗 Building workflow graph...")

    workflow = (
        StateGraph(
            state_schema=SwarmState,
            input_schema=ChatContasInputState,
            output_schema=ChatContasStateOutput,
            config_schema=ChatContasConfiguration,
        )
        .add_node(
            main_agent,
            destinations=("RAG_Agent", "Search_Agent"),
            metadata={
                "agent_type": "coordinator",
                "tags": ["main", "coordinator", "institutional", "autonomous"],
            },
        )
        .add_node(
            rag_agent,
            destinations=("Main_Agent", "Search_Agent"),
            metadata={
                "agent_type": "pipeline",
                "tags": [
                    "rag",
                    "pipeline",
                    "documents",
                    "processing",
                    "institutional",
                    "autonomous",
                ],
            },
        )
        .add_node(
            search_agent,
            destinations=("Main_Agent", "RAG_Agent"),
            metadata={
                "agent_type": "specialist",
                "tags": [
                    "search",
                    "system",
                    "web",
                    "processes",
                    "institutional",
                    "autonomous",
                ],
            },
        )
    )

    # ===== ROUTING CONFIGURATION =====
    print("🎯 Configuring routing...")

    workflow = add_active_agent_router(
        builder=workflow,
        route_to=["Main_Agent", "RAG_Agent", "Search_Agent"],
        default_active_agent="Main_Agent",
    )

    # ===== INSTRUMENTATION HOOKS =====
    print("📊 Instrumentation hooks integrated into agent pre-processing pipeline...")

    # ===== COMPILATION WITH CHECKPOINTING =====
    print("📦 Compiling workflow with checkpointing...")
    print("🔄 Swarm Architecture: Any agent can respond directly to users")

    checkpointer = MemorySaver()

    # Compile with all configurations
    graph = compile_workflow(workflow, checkpointer=checkpointer)

    print("✅ Institutional Swarm System successfully created!")
    print("🎯 Architecture: Autonomous agents with optional handoffs")

    return graph


# ===== MAIN SYSTEM CREATION =====
print("🚀 Creating Institutional Swarm System...")
swarm_graph = create_swarm_system()


# Export the graph for external use
__all__ = ["swarm_graph", "create_swarm_system"]
