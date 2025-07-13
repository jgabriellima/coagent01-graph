"""
Consolidated state definitions for the TCE-PA swarm architecture.
This module defines the combined state schema that all agents share.
"""

from langgraph_swarm import SwarmState
from langgraph.prebuilt.chat_agent_executor import AgentState
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class TCESwarmState(SwarmState):
    """
    Combined state schema for the TCE-PA swarm architecture.
    Inherits from SwarmState for agent coordination and adds TCE-specific fields.
    """

    # ===== USER CONTEXT =====
    username: str = Field(default="", description="Nome do usuário")
    user_id: str = Field(default="", description="ID único do usuário")
    current_date: str = Field(default="", description="Data atual da sessão")

    # ===== QUERY CONTEXT =====
    query: str = Field(default="", description="Consulta atual do usuário")
    query_type: str = Field(
        default="",
        description="Tipo de consulta: legislacao, expediente, acordao, web, general",
    )
    original_query: str = Field(default="", description="Consulta original preservada")

    # ===== MAIN AGENT STATE =====
    # Controle de fluxo e coordenação
    current_step: str = Field(default="", description="Etapa atual do fluxo")
    routing_decision: str = Field(
        default="", description="Decisão de roteamento tomada"
    )
    requires_clarification: bool = Field(
        default=False, description="Indica se é necessário esclarecimento"
    )

    # ===== RAG AGENT STATE =====
    # Document processing and retrieval
    document_type: str = Field(
        default="", description="Tipo de documento: legislacao, acordao, resolucao, ato"
    )
    document_number: str = Field(default="", description="Número do documento")
    document_year: str = Field(default="", description="Ano do documento")
    document_content: str = Field(default="", description="Conteúdo do documento")

    # RAG processing results
    chunks: List[str] = Field(
        default_factory=list, description="Chunks processados pelo sistema"
    )
    retrieval_results: List[str] = Field(
        default_factory=list, description="Resultados da busca RAG"
    )
    rag_result: str = Field(default="", description="Resultado final do RAG Agent")
    rag_response: str = Field(default="", description="Resposta formatada do RAG")

    # RAG metadata
    chunk_strategy: str = Field(
        default="recursive", description="Estratégia de chunking utilizada"
    )
    chunk_size: int = Field(default=512, description="Tamanho dos chunks")
    chunk_overlap: int = Field(default=50, description="Sobreposição entre chunks")
    confidence_score: float = Field(
        default=0.0, description="Pontuação de confiança do RAG"
    )

    # ===== SEARCH AGENT STATE =====
    # Search context
    search_type: str = Field(
        default="", description="Tipo de busca: expediente, processo, web, mixed"
    )
    expediente_number: str = Field(default="", description="Número do expediente")
    processo_number: str = Field(default="", description="Número do processo")
    year: str = Field(default="", description="Ano de referência")

    # Search results
    etce_results: List[Dict[str, Any]] = Field(
        default_factory=list, description="Resultados do sistema eTCE"
    )
    web_results: List[Dict[str, Any]] = Field(
        default_factory=list, description="Resultados da busca web"
    )
    search_result: str = Field(default="", description="Resultado consolidado da busca")
    search_response: str = Field(default="", description="Resposta formatada da busca")

    # Web search specific
    web_query: str = Field(default="", description="Query específica para busca web")

    # ===== SYSTEM CONFIGURATION =====
    # Feature flags
    enable_web_search: bool = Field(default=True, description="Habilita busca web")
    enable_etce_search: bool = Field(default=True, description="Habilita busca no eTCE")
    enable_rag_processing: bool = Field(
        default=True, description="Habilita processamento RAG"
    )

    # TCE databases
    tce_databases: List[str] = Field(
        default_factory=lambda: ["atos", "arquivos-tce", "legislacao", "acordaos"],
        description="Bases de dados TCE disponíveis",
    )

    # ===== OPERATIONAL STATE =====
    # Processing metadata
    thread_mode: str = Field(default="production", description="Modo de operação")
    task_type: str = Field(default="tce_assistance", description="Tipo de tarefa")
    processing_stage: str = Field(
        default="", description="Estágio atual do processamento"
    )

    # Agent constraints and metadata
    constraints: List[str] = Field(
        default_factory=list, description="Restrições específicas do contexto"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadados adicionais"
    )

    # ===== FINAL RESPONSE =====
    # Consolidated response
    final_response: str = Field(default="", description="Resposta final consolidada")
    response_sources: List[str] = Field(
        default_factory=list, description="Fontes utilizadas na resposta"
    )
    response_confidence: float = Field(
        default=0.0, description="Confiança na resposta final"
    )

    # ===== INSTRUMENTATION =====
    # Traces and monitoring
    trace_id: str = Field(default="", description="ID do trace para monitoramento")
    agent_interactions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Histórico de interações entre agentes"
    )
    processing_time: float = Field(
        default=0.0, description="Tempo de processamento total"
    )

    # Error handling
    error_messages: List[str] = Field(
        default_factory=list, description="Mensagens de erro"
    )
    warnings: List[str] = Field(
        default_factory=list, description="Avisos durante o processamento"
    )

    # ===== HUMAN-IN-THE-LOOP =====
    # User interaction
    pending_user_question: str = Field(
        default="", description="Pergunta pendente para o usuário"
    )
    user_response: str = Field(default="", description="Resposta do usuário")
    requires_user_input: bool = Field(
        default=False, description="Indica se é necessário input do usuário"
    )


class TCEAgentOutput(BaseModel):
    """Base output format for TCE agents"""

    agent_name: str
    query: str
    response: str
    sources: List[str] = []
    confidence: float = 0.0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = {}


class TCEMainAgentOutput(TCEAgentOutput):
    """Specific output format for Main Agent"""

    routing_decision: str
    next_agent: str = ""
    requires_clarification: bool = False


class TCERagAgentOutput(TCEAgentOutput):
    """Specific output format for RAG Agent"""

    document_type: str
    chunk_strategy: str
    chunks_processed: int = 0
    retrieval_method: str = ""


class TCESearchAgentOutput(TCEAgentOutput):
    """Specific output format for Search Agent"""

    search_type: str
    expediente_number: str = ""
    processo_number: str = ""
    etce_results_count: int = 0
    web_results_count: int = 0


# State factory function
def create_tce_state(**kwargs) -> TCESwarmState:
    """
    Factory function to create a TCE swarm state with default values.

    Args:
        **kwargs: Additional state values to override defaults

    Returns:
        TCESwarmState: Initialized state object
    """
    default_state = TCESwarmState()

    # Update with provided kwargs
    for key, value in kwargs.items():
        if hasattr(default_state, key):
            setattr(default_state, key, value)

    return default_state


# State validation functions
def validate_expediente_format(expediente: str) -> bool:
    """Validate expediente number format (NNNNNN/AAAA)"""
    import re

    pattern = r"^\d{6}/\d{4}$"
    return bool(re.match(pattern, expediente))


def validate_process_format(process: str) -> bool:
    """Validate process number format (TC/NNNNNN/AAAA)"""
    import re

    pattern = r"^TC/\d{6}/\d{4}$"
    return bool(re.match(pattern, process))


def get_query_type(query: str) -> str:
    """
    Determine query type based on content analysis.

    Args:
        query: User query string

    Returns:
        str: Query type classification
    """
    query_lower = query.lower()

    # Check for expediente patterns
    if "expediente" in query_lower or "processo" in query_lower:
        return "expediente"

    # Check for legislation patterns
    elif any(
        term in query_lower
        for term in ["resolução", "lei", "decreto", "ato", "portaria"]
    ):
        return "legislacao"

    # Check for acordão patterns
    elif "acordão" in query_lower or "acórdão" in query_lower:
        return "acordao"

    # Check for web search patterns
    elif any(
        term in query_lower
        for term in ["último", "recente", "notícia", "atual", "hoje"]
    ):
        return "web"

    # Default to general
    else:
        return "general"
