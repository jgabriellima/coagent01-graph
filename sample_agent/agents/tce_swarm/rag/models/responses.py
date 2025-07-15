"""
Response Models for TCE-PA RAG Pipeline
Pydantic models for structured responses from pipeline nodes
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from .chunks import Citation


class DocumentToIngest(BaseModel):
    """Documento que precisa ser ingerido"""

    document_id: str = Field(description="ID do documento")
    document_type: str = Field(description="Tipo do documento")
    source_url: Optional[str] = Field(description="URL de origem")
    priority: Optional[int] = Field(description="Prioridade de ingestão", ge=1, le=10)

    class Config:
        extra = "forbid"

class QueryAnalysisResult(BaseModel):
    """Resultado da análise de query"""

    processed_query: str = Field(description="Query processada e ajustada para maximizar a consulta")
    query_type: Literal["legislation", "acordao", "resolucao", "jurisprudencia"] = (
        Field(description="Tipo da query")
    )
    query_complexity: Literal["simple", "medium", "complex"] = Field(
        description="Complexidade da query"
    )
    target_databases: Optional[List[str]] = Field(description="Bases de dados alvo")
    temporal_context: Optional[str] = Field(description="Contexto temporal i.e '2024'")
    ingestion_required: bool = Field(description="Necessita ingestão")
    analysis_confidence: Optional[float] = Field(
        description="Confiança da análise", ge=0.0, le=1.0
    )
    documents_to_ingest: Optional[List[DocumentToIngest]] = Field(description="Documentos que precisam ser ingeridos")

    class Config:
        extra = "forbid"

class ChunkStrategyResult(BaseModel):
    """Resultado da seleção de estratégia de chunking"""

    selected_chunker: Literal["recursive", "semantic", "sdpm", "late"] = Field(
        description="Chunker selecionado"
    )
    chunk_size: int = Field(description="Tamanho do chunk")
    chunk_overlap: int = Field(description="Sobreposição entre chunks")
    chunking_metadata: Dict[str, Any] = Field(description="Metadados do chunking")
    strategy_rationale: str = Field(description="Justificativa da estratégia")


class IngestionResult(BaseModel):
    """Resultado da ingestão de documentos"""

    document_id: str = Field(description="ID do documento")
    status: Literal["success", "error", "partial"] = Field(
        description="Status da ingestão"
    )
    chunks_created: int = Field(description="Chunks criados")
    processing_time: float = Field(description="Tempo de processamento")
    quality_score: float = Field(description="Score de qualidade", ge=0.0, le=1.0)
    error_message: Optional[str] = Field(description="Mensagem de erro")


class EnrichmentResult(BaseModel):
    """Resultado do enriquecimento de contexto"""

    enriched_chunks: int = Field(description="Chunks enriquecidos")
    cross_references_found: int = Field(description="Referências cruzadas encontradas")
    temporal_context_added: bool = Field(description="Contexto temporal adicionado")
    juridical_context_added: bool = Field(description="Contexto jurídico adicionado")


class ResponseGenerationResult(BaseModel):
    """Resultado da geração de resposta"""

    generated_response: str = Field(description="Resposta gerada")
    citations: List[Citation] = Field(description="Citações estruturadas")
    quality_score: float = Field(description="Score de qualidade", ge=0.0, le=1.0)


class ValidationResult(BaseModel):
    """Resultado da validação de qualidade"""

    quality_score: float = Field(description="Score de qualidade", ge=0.0, le=1.0)
    needs_rewrite: bool = Field(description="Necessita reescrita")
