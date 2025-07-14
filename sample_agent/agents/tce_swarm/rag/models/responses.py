"""
Response Models for TCE-PA RAG Pipeline
Pydantic models for structured responses from pipeline nodes
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal

class QueryAnalysisResult(BaseModel):
    """Resultado da análise de query"""
    processed_query: str = Field(description="Query processada")
    query_type: Literal["legislation", "acordao", "resolucao", "jurisprudencia"] = Field(description="Tipo de consulta")
    query_complexity: Literal["simple", "medium", "complex"] = Field(description="Complexidade da consulta")
    target_databases: List[str] = Field(description="Bases de dados alvo")
    temporal_context: Optional[str] = Field(description="Contexto temporal")
    needs_ingestion: bool = Field(description="Necessita ingestão")
    analysis_confidence: float = Field(description="Confiança na análise", ge=0.0, le=1.0)

class ChunkStrategyResult(BaseModel):
    """Resultado da seleção de estratégia de chunking"""
    selected_strategy: Literal["recursive", "semantic", "sdpm", "late"] = Field(description="Estratégia selecionada")
    chunk_size: int = Field(description="Tamanho do chunk")
    chunk_overlap: int = Field(description="Sobreposição entre chunks")
    configuration: Dict[str, Any] = Field(description="Configuração específica")
    strategy_rationale: str = Field(description="Justificativa da estratégia")

class IngestionResult(BaseModel):
    """Resultado da ingestão de documentos"""
    document_id: str = Field(description="ID do documento")
    status: Literal["success", "error", "partial"] = Field(description="Status da ingestão")
    chunks_created: int = Field(description="Chunks criados")
    processing_time: float = Field(description="Tempo de processamento")
    quality_score: float = Field(description="Score de qualidade", ge=0.0, le=1.0)
    error_message: Optional[str] = Field(description="Mensagem de erro se houver")

class RetrievalResult(BaseModel):
    """Resultado da busca e recuperação"""
    query: str = Field(description="Query utilizada")
    chunks_found: int = Field(description="Chunks encontrados")
    processing_time: float = Field(description="Tempo de processamento")
    search_methods: List[str] = Field(description="Métodos de busca utilizados")
    collection_stats: Dict[str, int] = Field(description="Estatísticas por collection")

class GradingResult(BaseModel):
    """Resultado da avaliação de relevância"""
    total_chunks: int = Field(description="Total de chunks avaliados")
    relevant_chunks: int = Field(description="Chunks relevantes")
    average_relevance: float = Field(description="Relevância média", ge=0.0, le=1.0)
    grading_time: float = Field(description="Tempo de avaliação")
    needs_rewrite: bool = Field(description="Necessita reescrita da query")

class EnrichmentResult(BaseModel):
    """Resultado do enriquecimento de contexto"""
    enriched_chunks: int = Field(description="Chunks enriquecidos")
    cross_references_found: int = Field(description="Referências cruzadas encontradas")
    temporal_context_added: bool = Field(description="Contexto temporal adicionado")
    juridical_context_added: bool = Field(description="Contexto jurídico adicionado")
    enrichment_time: float = Field(description="Tempo de enriquecimento")

class RerankingResult(BaseModel):
    """Resultado do reranking"""
    reranked_chunks: int = Field(description="Chunks reordenados")
    ranking_criteria: List[str] = Field(description="Critérios de ranking")
    score_distribution: Dict[str, float] = Field(description="Distribuição de scores")
    final_selection: int = Field(description="Chunks selecionados para geração")

class ResponseGenerationResult(BaseModel):
    """Resultado da geração de resposta"""
    response_text: str = Field(description="Texto da resposta")
    citations: List[str] = Field(description="Citações incluídas")
    confidence_score: float = Field(description="Score de confiança", ge=0.0, le=1.0)
    tokens_used: int = Field(description="Tokens utilizados")
    generation_time: float = Field(description="Tempo de geração")
    quality_indicators: Dict[str, float] = Field(description="Indicadores de qualidade")

class ValidationResult(BaseModel):
    """Resultado da validação de qualidade"""
    validation_passed: bool = Field(description="Validação aprovada")
    quality_score: float = Field(description="Score de qualidade", ge=0.0, le=1.0)
    validation_criteria: Dict[str, bool] = Field(description="Critérios de validação")
    improvement_suggestions: List[str] = Field(description="Sugestões de melhoria")
    requires_retry: bool = Field(description="Requer nova tentativa") 