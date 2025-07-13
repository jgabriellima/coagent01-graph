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


def build_tce_rag_agent(model, handoff_tools: list[Callable] | None = None):
    """Builds the RAG agent for TCE-PA document processing"""
    
    tools = [
        tce_documents_database_tool,
        document_ingestion_tool,
        document_summarization_tool,
        human_in_the_loop
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
            "Realizar busca semântica inteligente na base de conhecimento do TCE-PA",
            "Aplicar estratégias de chunking otimizadas para documentos jurídicos",
            "Executar ingestion de documentos com metadados temporais e contextuais",
            "Fornecer respostas precisas baseadas em retrieval augmented generation",
            "Citar fontes e referências específicas dos documentos consultados",
            "Manter contexto jurídico e formal nas respostas",
            "Processar documentos com influência temporal (exercícios, vigência, etc.)"
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