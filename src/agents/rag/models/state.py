"""
Estado especializado para pipeline RAG
Contém apenas campos necessários com documentação de uso
"""

from pydantic import BaseModel, Field
from typing import Annotated, List, Dict, Any, Optional, Literal
from .chunks import ChunkResult, GradedChunk, EnrichedChunk, RerankedChunk, Citation
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class RAGState(BaseModel):
    """
    Estado especializado para o pipeline RAG agentico
    Campos refatorados baseados no uso real dos nodes
    """

    # ===== QUERY PROCESSING =====
    original_query: Optional[str] = Field(default=None, description="Query original do usuário")
    processed_query: Optional[str] = Field(
        default=None, description="Query processada/otimizada para retrieval"
    )
    query_type: Optional[Literal["legislation", "acordao", "resolucao", "jurisprudencia"]] = (
        Field(default=None)
    )
    query_complexity: Optional[Literal["simple", "medium", "complex"]] = Field(default=None)

    file_paths: Optional[List[str]] = Field(
        default=None, description="Caminhos dos arquivos a serem processados"
    )
    # ===== DOCUMENT CONTEXT =====
    target_databases: Optional[List[str]] = Field(
        default=None
    )
    temporal_context: Optional[str] = Field(
        default=None, description="Contexto temporal para filtrar documentos"
    )
    document_context: Optional[Dict[str, Any]] = Field(
        default=None, description="Metadados contextuais para filtros"
    )

    # ===== ACCESS CONTROL =====
    document_scope: Optional[Literal["global", "user_specific", "session_specific"]] = Field(
        default=None
    )
    user_id: Optional[str] = Field(
        default=None, description="ID do usuário para controle de acesso"
    )
    session_id: Optional[str] = Field(
        default=None, description="ID da sessão para isolamento temporal"
    )

    # ===== DOCUMENT INGESTION =====
    ingestion_required: Optional[bool] = Field(
        default=None, description="Flag para ingestão de novos documentos"
    )
    documents_to_ingest: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Documentos para processar"
    )
    user_documents: Optional[List[str]] = Field(
        default=None, description="IDs de documentos do usuário"
    )
    ingestion_status: Optional[Dict[str, str]] = Field(
        default=None, description="Status de ingestão por documento"
    )

    # ===== VECTOR DATABASE =====
    vector_db_type: Optional[Literal["azure_ai_search", "lancedb"]] = Field(
        default=None
    )
    collection_names: Optional[List[str]] = Field(
        default=None, description="Nomes das coleções no vector database"
    )

    # ===== CHUNKING STRATEGY =====
    selected_chunker: Optional[Literal["recursive", "semantic", "sdpm", "late"]] = Field(
        default=None
    )
    chunk_size: Optional[int] = Field(default=None, description="Tamanho dos chunks")
    chunk_overlap: Optional[int] = Field(default=None, description="Sobreposição entre chunks")
    chunking_metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Configurações específicas do chunking"
    )

    # ===== RETRIEVAL RESULTS =====
    retrieved_chunks: Optional[List[ChunkResult]] = Field(
        default=None, description="Chunks encontrados na busca"
    )
    graded_chunks: Optional[List[GradedChunk]] = Field(
        default=None, description="Chunks avaliados por relevância"
    )
    enriched_context: Optional[List[EnrichedChunk]] = Field(
        default=None, description="Chunks enriquecidos com contexto"
    )
    reranked_chunks: Optional[List[RerankedChunk]] = Field(
        default=None, description="Chunks reordenados por relevância"
    )

    # ===== GENERATION =====
    generated_response: Optional[str] = Field(default=None, description="Resposta final gerada")
    quality_score: Optional[float] = Field(
        default=None, description="Score de qualidade da resposta"
    )
    citations: Optional[List[Citation]] = Field(
        default=None, description="Citações dos documentos fonte"
    )
    final_context: Optional[str] = Field(default=None, description="Contexto final consolidado")

    # ===== WORKFLOW CONTROL =====
    needs_enrichment: Optional[bool] = Field(
        default=None, description="Flag para enriquecimento de contexto"
    )
    needs_rewrite: Optional[bool] = Field(
        default=None, description="Flag para reescrita da query"
    )
    retry_count: Optional[int] = Field(default=None, description="Contador de tentativas de retry")
    max_retries: Optional[int] = Field(default=None, description="Máximo de tentativas de retry")

    # ===== PERFORMANCE METRICS =====
    retrieval_time: Optional[float] = Field(default=None, description="Tempo de busca")
    processing_time: Optional[float] = Field(
        default=None, description="Tempo total de processamento"
    )
    ingestion_time: Optional[float] = Field(default=None, description="Tempo de ingestão")
    vector_db_queries: Optional[int] = Field(
        default=None, description="Número de consultas ao vector database"
    )

    # ===== MESSAGES =====
    messages: Annotated[List[BaseMessage], add_messages] = Field(
        default_factory=lambda: [], description="Mensagens do pipeline RAG"
    )
    
    handoff_to_agent: Optional[str] = Field(
        default=None, description="Nome do agente para handoff"
    )

    def copy(self, **kwargs):
        """Create a copy of the state with optional field updates"""
        return self.model_copy(update=kwargs)
