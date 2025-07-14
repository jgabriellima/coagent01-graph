"""
TCE RAG State Model
Expanded state model with 24 new fields for complete pipeline control
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from .chunks import ChunkResult, GradedChunk, EnrichedChunk, RerankedChunk, Citation

class TCE_RAG_State(BaseModel):
    """
    Estado especializado para o pipeline RAG agentico do TCE-PA
    Inclui todos os campos necessários para controle completo do workflow
    """
    
    # Query Processing
    original_query: str = Field(default="")
    processed_query: str = Field(default="")
    query_type: Literal["legislation", "acordao", "resolucao", "jurisprudencia"] = Field(default="legislation")
    query_complexity: Literal["simple", "medium", "complex"] = Field(default="medium")
    
    # Document Context & Access Control
    target_databases: List[str] = Field(default_factory=lambda: ["atos", "legislacao", "acordaos", "arquivos-tce"])
    temporal_context: Optional[str] = Field(default=None)
    juridical_context: Dict[str, Any] = Field(default_factory=dict)
    
    # Document Ingestion & Filtering
    document_scope: Literal["global", "user_specific", "session_specific"] = Field(default="global")
    user_id: str = Field(default="")
    session_id: str = Field(default="")
    ingestion_required: bool = Field(default=False)
    user_documents: List[str] = Field(default_factory=list)
    document_filters: Dict[str, Any] = Field(default_factory=dict)
    
    # Vector Database Management
    vector_db_type: Literal["chroma", "pinecone", "weaviate", "faiss"] = Field(default="chroma")
    vector_db_instances: Dict[str, Any] = Field(default_factory=dict)
    collection_names: List[str] = Field(default_factory=list)
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    
    # Chunking Strategy
    selected_chunker: Literal["recursive", "semantic", "sdpm", "late"] = Field(default="recursive")
    chunk_size: int = Field(default=512)
    chunk_overlap: int = Field(default=50)
    chunking_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Ingestion Control
    documents_to_ingest: List[Dict[str, Any]] = Field(default_factory=list)
    ingestion_strategy: Literal["batch", "streaming", "incremental"] = Field(default="batch")
    ingestion_status: Dict[str, str] = Field(default_factory=dict)
    
    # Retrieval Results
    retrieved_chunks: List[ChunkResult] = Field(default_factory=list)
    relevance_scores: List[float] = Field(default_factory=list)
    graded_chunks: List[GradedChunk] = Field(default_factory=list)
    
    # Enrichment & Reranking
    enriched_context: List[EnrichedChunk] = Field(default_factory=list)
    reranked_chunks: List[RerankedChunk] = Field(default_factory=list)
    final_context: str = ""
    
    # Generation & Validation
    generated_response: str = Field(default="")
    quality_score: float = Field(default=0.0)
    validation_passed: bool = Field(default=False)
    citations: List[Citation] = Field(default_factory=list)
    
    # Workflow Control
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    needs_rewrite: bool = Field(default=False)
    needs_enrichment: bool = Field(default=False)
    needs_ingestion: bool = Field(default=False)
    
    # Performance Metrics
    retrieval_time: float = Field(default=0.0)
    processing_time: float = Field(default=0.0)
    ingestion_time: float = Field(default=0.0)
    total_tokens_used: int = Field(default=0)
    vector_db_queries: int = Field(default=0)
    
    def copy(self, **kwargs):
        """Create a copy of the state with optional field updates"""
        return self.model_copy(update=kwargs)
    
    class Config:
        arbitrary_types_allowed = True 