"""
Chunk Models for TCE-PA RAG Pipeline
Pydantic models for chunk processing and search results
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChunkResult(BaseModel):
    """Resultado de um chunk individual"""
    content: str = Field(description="Conteúdo do chunk")
    metadata: Dict[str, Any] = Field(description="Metadados associados")
    chunk_id: str = Field(description="ID único")
    
class ChunkingResult(BaseModel):
    """Resultado do processo de chunking"""
    chunks: List[ChunkResult] = Field(description="Lista de chunks gerados")
    strategy_used: str = Field(description="Estratégia utilizada")
    total_chunks: int = Field(description="Número total de chunks")
    processing_time: float = Field(description="Tempo de processamento")

class VectorSearchResult(BaseModel):
    """Resultado da busca no vector database"""
    chunks: List[ChunkResult] = Field(description="Chunks encontrados")
    query: str = Field(description="Query utilizada")
    total_results: int = Field(description="Total de resultados")
    search_time: float = Field(description="Tempo de busca")

class GradedChunk(BaseModel):
    """Chunk com avaliação de relevância"""
    chunk: ChunkResult = Field(description="Chunk original")
    relevance_score: float = Field(description="Score de relevância", ge=0.0, le=1.0)
    confidence: float = Field(description="Confiança na avaliação", ge=0.0, le=1.0)

class EnrichedChunk(BaseModel):
    """Chunk com contexto enriquecido"""
    chunk: ChunkResult = Field(description="Chunk original")
    semantic_relevance: float = Field(description="Relevância semântica", ge=0.0, le=1.0)
    juridical_relevance: float = Field(description="Relevância jurídica", ge=0.0, le=1.0)
    temporal_relevance: float = Field(description="Relevância temporal", ge=0.0, le=1.0)
    tce_specificity: float = Field(description="Especificidade TCE-PA", ge=0.0, le=1.0)
    enriched_context: str = Field(description="Contexto enriquecido")
    cross_references: List[str] = Field(description="Referências cruzadas")

class RerankedChunk(BaseModel):
    """Chunk reordenado com score final"""
    chunk: EnrichedChunk = Field(description="Chunk enriquecido")
    final_score: float = Field(description="Score final combinado", ge=0.0, le=1.0)
    ranking_factors: Dict[str, float] = Field(description="Fatores de ranking")

class Citation(BaseModel):
    """Citação específica do documento"""
    source: str = Field(description="Fonte da citação")
    document_type: str = Field(description="Tipo de documento")
    document_number: str = Field(description="Número do documento")
    page_number: Optional[int] = Field(description="Número da página")
    article_number: Optional[str] = Field(description="Número do artigo")
    excerpt: str = Field(description="Trecho citado")
    confidence: float = Field(description="Confiança na citação", ge=0.0, le=1.0) 