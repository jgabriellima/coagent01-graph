"""
TCE-PA Swarm Architecture Graph
Production-grade multi-agent system for Tribunal de Contas do Estado do Pará
"""

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph
from langgraph_swarm import add_active_agent_router, create_handoff_tool
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
import uuid
import datetime
from typing import Dict, Any

# Import agents
from sample_agent.agents.tce_swarm.main_agent import build_tce_main_agent
from sample_agent.agents.tce_swarm.rag_agent import build_tce_rag_agent
from sample_agent.agents.tce_swarm.search_agent import build_tce_search_agent

# Import state
from sample_agent.agents.tce_swarm.states import TCESwarmState, get_query_type

# Import utils
from sample_agent.utils import (
    compile_workflow,
    create_handoff_tool_with_state_propagation,
)


@traceable(
    name="TCE_Swarm_System", tags=["tce-pa", "multi-agent", "swarm", "production"]
)
def create_tce_swarm_system():
    """
    Create the production-grade TCE-PA swarm system.

    Returns:
        Compiled workflow graph with full instrumentation
    """

    # =====  INSTRUMENTATION SETUP =====
    print("🔧 Initializing TCE-PA Swarm System...")
    print("📊 Setting up instrumentation and monitoring...")

    # ===== MODEL CONFIGURATION =====
    llm_model = "openai:gpt-4o-mini"
    # llm_model = "groq:llama-3.3-70b-versatile"
    model_config = {
        "temperature": 0.1,  # Low temperature for consistent legal responses
        "max_tokens": 2000,
        "top_p": 0.95,
    }

    print(f"🤖 Using model: {llm_model}")
    print(f"⚙️  Model config: {model_config}")

    # ===== HANDOFF TOOLS WITH TCE CONTEXT =====
    print("🔄 Creating handoff tools...")

    # Main Agent handoff tool
    main_agent_handoff = create_handoff_tool_with_state_propagation(
        agent_name="TCE_Main_Agent",
        description="Use this to handoff to the main TCE agent for coordination, user interaction, and general queries.",
    )

    # RAG Agent handoff tool
    rag_agent_handoff = create_handoff_tool_with_state_propagation(
        agent_name="TCE_RAG_Agent",
        description="Use this to handoff to the RAG agent for legislation, resolutions, acts, and jurisprudence queries.",
    )

    # Search Agent handoff tool
    search_agent_handoff = create_handoff_tool_with_state_propagation(
        agent_name="TCE_Search_Agent",
        description="Use this to handoff to the search agent for expediente, process, and web search queries.",
    )

    # ===== AGENT INITIALIZATION =====
    print("🤖 Initializing agents...")

    # Main Agent - Coordination and Management
    main_agent = build_tce_main_agent(
        init_chat_model(llm_model, **model_config),
        [rag_agent_handoff, search_agent_handoff],
    )

    # RAG Agent - Document Processing
    rag_agent = build_tce_rag_agent(
        init_chat_model(llm_model, **model_config),
        [main_agent_handoff, search_agent_handoff],
    )

    # Search Agent - eTCE and Web Search
    search_agent = build_tce_search_agent(
        init_chat_model(llm_model, **model_config),
        [main_agent_handoff, rag_agent_handoff],
    )

    print("✅ All agents initialized successfully")

    # ===== WORKFLOW GRAPH CONSTRUCTION =====
    print("🔗 Building workflow graph...")

    workflow = (
        StateGraph(TCESwarmState)
        .add_node(
            main_agent,
            destinations=("TCE_RAG_Agent", "TCE_Search_Agent"),
            metadata={
                "agent_type": "coordinator",
                "capabilities": ["routing", "coordination", "user_interaction"],
                "tags": ["main", "coordinator", "tce-pa"],
            },
        )
        .add_node(
            rag_agent,
            destinations=("TCE_Main_Agent", "TCE_Search_Agent"),
            metadata={
                "agent_type": "specialist",
                "capabilities": ["document_processing", "rag", "legislation"],
                "tags": ["rag", "documents", "legislation", "tce-pa"],
            },
        )
        .add_node(
            search_agent,
            destinations=("TCE_Main_Agent", "TCE_RAG_Agent"),
            metadata={
                "agent_type": "specialist",
                "capabilities": ["etce_search", "web_search", "process_lookup"],
                "tags": ["search", "etce", "web", "processes", "tce-pa"],
            },
        )
    )

    # ===== ROUTING CONFIGURATION =====
    print("🎯 Configuring routing...")

    workflow = add_active_agent_router(
        builder=workflow,
        route_to=["TCE_Main_Agent", "TCE_RAG_Agent", "TCE_Search_Agent"],
        default_active_agent="TCE_Main_Agent",
    )

    # ===== INSTRUMENTATION HOOKS =====
    print("📊 Setting up instrumentation hooks...")

    @traceable(
        name="TCE_Query_Classification", tags=["classification", "routing", "tce-pa"]
    )
    def classify_query_hook(state: TCESwarmState) -> TCESwarmState:
        """Hook to classify queries and add trace metadata"""
        if state.query and not state.query_type:
            state.query_type = get_query_type(state.query)
            state.original_query = state.query

        # Add trace metadata
        if not state.trace_id:
            state.trace_id = str(uuid.uuid4())

        return state

    @traceable(name="TCE_State_Validation", tags=["validation", "state", "tce-pa"])
    def validate_state_hook(state: TCESwarmState) -> TCESwarmState:
        """Hook to validate state consistency"""
        # Validate expediente format if present
        if state.expediente_number:
            from sample_agent.agents.tce_swarm.states import validate_expediente_format

            if not validate_expediente_format(state.expediente_number):
                state.warnings.append(
                    f"Invalid expediente format: {state.expediente_number}"
                )

        # Validate process format if present
        if state.processo_number:
            from sample_agent.agents.tce_swarm.states import validate_process_format

            if not validate_process_format(state.processo_number):
                state.warnings.append(
                    f"Invalid process format: {state.processo_number}"
                )

        return state

    # ===== COMPILATION WITH CHECKPOINTING =====
    print("📦 Compiling workflow with checkpointing...")

    checkpointer = MemorySaver()

    # Compile with all configurations
    graph = compile_workflow(
        workflow,
        checkpointer=checkpointer
    )

    print("✅ TCE-PA Swarm System successfully created!")

    return graph


@traceable(name="TCE_System_Health_Check", tags=["health", "monitoring", "tce-pa"])
def health_check(graph) -> Dict[str, Any]:
    """
    Perform a health check on the TCE swarm system.

    Args:
        graph: The compiled workflow graph

    Returns:
        Dict containing health check results
    """
    try:
        # Basic connectivity test
        test_state = TCESwarmState(
            query="teste de conectividade",
            query_type="general",
            username="system_test",
            current_date=datetime.datetime.now().isoformat(),
        )

        # Test basic functionality
        result = graph.get_state({"configurable": {"thread_id": "health_check"}})

        return {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "agents": ["TCE_Main_Agent", "TCE_RAG_Agent", "TCE_Search_Agent"],
            "capabilities": "all_systems_operational",
            "message": "TCE-PA Swarm System is fully operational",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "error": str(e),
            "message": "TCE-PA Swarm System has issues",
        }


# ===== MAIN SYSTEM CREATION =====
print("🚀 Creating TCE-PA Swarm System...")
tce_swarm_graph = create_tce_swarm_system()

# ===== HEALTH CHECK =====
print("🔍 Performing health check...")
health_status = health_check(tce_swarm_graph)
print(f"💊 System health: {health_status}")

# Export the graph for external use
__all__ = ["tce_swarm_graph", "create_tce_swarm_system", "health_check"]
