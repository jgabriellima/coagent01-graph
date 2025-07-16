"""
Chunk Models for RAG Pipeline
Pydantic models for chunk processing and search results
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChunkMetadata(BaseModel):
    """Metadados específicos de um chunk"""
    document_id: Optional[str] = Field(description="ID do documento origem")
    page_number: Optional[int] = Field(description="Número da página")
    section: Optional[str] = Field(description="Seção do documento")
    chunk_index: Optional[int] = Field(description="Índice do chunk no documento")
    timestamp: Optional[str] = Field(description="Timestamp de criação")
    
    class Config:
        extra = "forbid"

class RankingFactors(BaseModel):
    """Fatores utilizados no ranking de chunks"""
    semantic_similarity: Optional[float] = Field(description="Similaridade semântica", ge=0.0, le=1.0)
    keyword_match: Optional[float] = Field(description="Match de palavras-chave", ge=0.0, le=1.0)
    document_authority: Optional[float] = Field(description="Autoridade do documento", ge=0.0, le=1.0)
    recency: Optional[float] = Field(description="Fator de recência", ge=0.0, le=1.0)
    context_relevance: Optional[float] = Field(description="Relevância contextual", ge=0.0, le=1.0)
    
    class Config:
        extra = "forbid"

class ChunkResult(BaseModel):
    """Resultado de um chunk individual"""
    content: str = Field(description="Conteúdo do chunk")
    metadata: ChunkMetadata = Field(description="Metadados associados")
    chunk_id: str = Field(description="ID único")
    
    class Config:
        extra = "forbid"
    
class ChunkingResult(BaseModel):
    """Resultado do processo de chunking"""
    chunks: List[ChunkResult] = Field(description="Lista de chunks gerados")
    strategy_used: str = Field(description="Estratégia utilizada")
    total_chunks: int = Field(description="Número total de chunks")
    processing_time: float = Field(description="Tempo de processamento")
    
    class Config:
        extra = "forbid"

class VectorSearchResult(BaseModel):
    """Resultado da busca no vector database"""
    chunks: List[ChunkResult] = Field(description="Chunks encontrados")
    query: str = Field(description="Query utilizada")
    total_results: int = Field(description="Total de resultados")
    search_time: float = Field(description="Tempo de busca")
    
    class Config:
        extra = "forbid"

class GradedChunk(BaseModel):
    """Chunk com avaliação de relevância"""
    chunk: ChunkResult = Field(description="Chunk original")
    relevance_score: float = Field(description="Score de relevância", ge=0.0, le=1.0)
    confidence: float = Field(description="Confiança na avaliação", ge=0.0, le=1.0)
    
    class Config:
        extra = "forbid"

class EnrichedChunk(BaseModel):
    """Chunk com contexto enriquecido"""
    chunk: ChunkResult = Field(description="Chunk original")
    relevance_score: float = Field(description="Score de relevância combinado", ge=0.0, le=1.0)
    enriched_context: str = Field(description="Contexto enriquecido")
    cross_references: List[str] = Field(description="Referências cruzadas")
    ranking_factors: RankingFactors = Field(description="Fatores considerados no ranking")
    
    class Config:
        extra = "forbid"

class RerankedChunk(BaseModel):
    """Chunk reordenado com score final"""
    chunk: EnrichedChunk = Field(description="Chunk enriquecido")
    final_score: float = Field(description="Score final combinado", ge=0.0, le=1.0)
    ranking_factors: RankingFactors = Field(description="Fatores de ranking")
    
    class Config:
        extra = "forbid"

class Citation(BaseModel):
    """Citação específica do documento"""
    source: str = Field(description="Fonte da citação")
    document_type: str = Field(description="Tipo de documento")
    document_number: str = Field(description="Número do documento")
    page_number: Optional[int] = Field(description="Número da página")
    article_number: Optional[str] = Field(description="Número do artigo")
    excerpt: str = Field(description="Trecho citado")
    confidence: float = Field(description="Confiança na citação", ge=0.0, le=1.0)
    
    class Config:
        extra = "forbid" 