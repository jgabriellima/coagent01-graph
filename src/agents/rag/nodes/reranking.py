"""
Reranking Node for RAG Pipeline
Reorders chunks based on relevance scores and query context
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from ..utils import llm
from ..models.state import RAGState
from ..models.chunks import RerankedChunk
import time


class RerankedChunksResponse(BaseModel):
    """Response model for reranked chunks generation"""

    reranked_chunks: List[RerankedChunk] = Field(
        description="List of chunks reranked by relevance and context"
    )


def reranking_node(state: RAGState) -> RAGState:
    """
    Reordena chunks baseado em relevância e contexto da query
    """

    start_time = time.time()

    # Single LLM call to generate reranked chunks
    instruction = f"""
    Rerank chunks based on relevance to query: "{state.processed_query}"
    
    Consider:
    - Semantic relevance to query
    - Contextual enrichment information
    - Temporal relevance
    - Cross-reference strength
    
    Return chunks in order of relevance (most relevant first).
    """

    response = llm(
        instruction,
        RerankedChunksResponse,
        enriched_context=state.enriched_context,
        query_type=state.query_type,
        query_complexity=state.query_complexity,
    )

    # Update metrics and return
    state.processing_time = state.processing_time + (time.time() - start_time)

    return state.copy(
        reranked_chunks=response.reranked_chunks,
    )
