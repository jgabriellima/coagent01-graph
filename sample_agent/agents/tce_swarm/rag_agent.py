from typing import Callable, List
from langgraph.prebuilt.chat_agent_executor import AgentState, AgentStateWithStructuredResponse
from sample_agent.agents.swarm.builder import AgentBuilder
from pydantic import BaseModel
import os

# Tools
from sample_agent.agents.tce_swarm.tools import (
    tce_documents_database_tool,
    document_ingestion_tool,
    document_summarization_tool,
    human_in_the_loop
)

# RAG Pipeline
from sample_agent.agents.tce_swarm.rag import tce_rag_subgraph
from sample_agent.agents.tce_swarm.rag.models.state import TCE_RAG_State


class TCERagAgentState(AgentStateWithStructuredResponse):
    """Estado do RAG Agent TCE-PA"""
    # User context
    username: str = ""
    user_id: str = ""
    current_date: str = ""
    
    # Query context
    query: str = ""
    query_type: str = ""  # "legislacao", "acordao", "resolucao", "ato", "jurisprudencia"
    
    # Document context
    document_type: str = ""
    document_number: str = ""
    document_year: str = ""
    document_content: str = ""
    
    # RAG processing
    chunks: list[str] = []
    retrieval_results: list[str] = []
    rag_response: str = ""
    
    # Processing metadata
    chunk_strategy: str = "recursive"  # "token", "sentence", "recursive", "semantic"
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # System state
    thread_mode: str = "production"
    task_type: str = "document_processing"
    tce_databases: list[str] = ["atos", "arquivos-tce", "legislacao", "acordaos"]
    
    # Agent context
    constraints: list[str] = []
    metadata: dict = {}


class TCERagAgentOutput(AgentState):
    """Formato de saída estruturado do RAG Agent"""
    query: str
    query_type: str
    document_type: str
    rag_response: str
    sources: list[str] = []
    confidence: float = 0.0
    
    messages: List[str] = []


def execute_rag_pipeline_tool(query: str, user_id: str = "default", session_id: str = "default") -> dict:
    """
    Executa o pipeline RAG completo usando o subgrafo especializado
    """
    
    # Criar estado inicial do RAG
    initial_state = TCE_RAG_State(
        original_query=query,
        user_id=user_id,
        session_id=session_id,
        document_scope="global",  # Pode ser configurado
        needs_ingestion=False,  # Por padrão não precisa ingestão
        vector_db_type="chroma",
        target_databases=["atos", "legislacao", "acordaos", "arquivos-tce"]
    )
    
    try:
        # Executar pipeline RAG completo
        final_state = tce_rag_subgraph.invoke(initial_state)
        
        # Retornar resultado estruturado
        return {
            "success": True,
            "response": final_state.generated_response,
            "citations": [citation.model_dump() for citation in final_state.citations],
            "quality_score": final_state.quality_score,
            "processing_time": final_state.processing_time,
            "chunks_processed": len(final_state.retrieved_chunks),
            "query_type": final_state.query_type,
            "selected_chunker": final_state.selected_chunker,
            "vector_db_queries": final_state.vector_db_queries,
            "validation_passed": final_state.validation_passed
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": f"Erro no pipeline RAG: {str(e)}",
            "citations": [],
            "quality_score": 0.0
        }


def build_tce_rag_agent(model, handoff_tools: list[Callable] | None = None):
    """Builds the RAG agent for TCE-PA document processing"""
    
    tools = [
        tce_documents_database_tool,
        document_ingestion_tool,
        document_summarization_tool,
        human_in_the_loop,
        execute_rag_pipeline_tool
    ]
    
    if handoff_tools:
        tools.extend(handoff_tools)
    
    # Resolve prompt paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    prompt_template_path = os.path.join(
        base_dir, "prompts", "base_agent_prompt.jinja2"
    )
    dynamic_block_template_path = os.path.join(
        base_dir, "prompts", "tce_fragments", "rag_agent.jinja2"
    )
    
    builder = AgentBuilder(
        name="TCE_RAG_Agent",
        model=model,
        tools=tools,
        agent_identity="""Agente especializado em RAG (Retrieval-Augmented Generation) para documentos do TCE-PA.
        Expert em processamento de documentos jurídicos, legislação, acordãos, resoluções e atos normativos.""",
        responsibilities=[
            "Processar consultas sobre legislação, acordãos, resoluções e atos do TCE-PA",
            "Executar pipeline RAG completo usando execute_rag_pipeline_tool para consultas complexas",
            "Realizar busca semântica inteligente na base de conhecimento do TCE-PA",
            "Aplicar estratégias de chunking otimizadas para documentos jurídicos",
            "Executar ingestion de documentos com metadados temporais e contextuais",
            "Fornecer respostas precisas baseadas em retrieval augmented generation",
            "Citar fontes e referências específicas dos documentos consultados",
            "Manter contexto jurídico e formal nas respostas",
            "Processar documentos com influência temporal (exercícios, vigência, etc.)",
            "Usar o pipeline RAG agentico para consultas que requerem processamento avançado"
        ],
        constraints=[
            "Sempre responder em português brasileiro formal e técnico",
            "Citar fontes específicas usando formato [documento.tipo]",
            "Não inventar informações não encontradas na base de conhecimento",
            "Manter precisão jurídica em todas as respostas",
            "Processar apenas documentos relacionados ao TCE-PA",
            "Aplicar chunking apropriado para documentos longos",
            "Preservar metadados temporais e contextuais dos documentos",
            "Solicitar esclarecimentos quando consultas forem ambíguas"
        ],
        state_schema=TCERagAgentState,
        # response_format=TCERagAgentOutput,
        prompt_template_path=prompt_template_path,
        dynamic_block_template_path=dynamic_block_template_path,
    )
    
    return builder.build() 