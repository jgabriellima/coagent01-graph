"""
Context Enrichment Node for RAG Pipeline
Enriches chunks with context, cross-references, and temporal information
"""

from pydantic import BaseModel, Field
from typing import List
from ..utils import llm
from ..models.state import RAGState
from ..models.chunks import EnrichedChunk
import time


class EnrichedChunksResponse(BaseModel):
    """Response model for enriched chunks generation"""
    enriched_chunks: List[EnrichedChunk] = Field(
        description="List of chunks enriched with context information"
    )


def context_enrichment_node(state: RAGState) -> RAGState:
    """
    Enriquece contexto dos chunks com informações específicas
    """

    start_time = time.time()

    # Single LLM call to generate enriched chunks
    instruction = f"""
    Enrich chunks with specific context information for query: "{state.processed_query}"
    
    For each chunk, provide:
    - Enhanced context with temporal and document information
    - Cross-references to related content
    - Ranking factors for semantic, temporal, and context relevance
    
    Document context: {state.document_context}
    Temporal context: {state.temporal_context}
    """

    response = llm(
        instruction,
        EnrichedChunksResponse,
        graded_chunks=state.graded_chunks,
        document_context=state.document_context,
        temporal_context=state.temporal_context,
    )

    # Update metrics and return
    state.processing_time = state.processing_time + (time.time() - start_time)

    return state.copy(
        enriched_context=response.enriched_chunks,
        needs_enrichment=False,
    )
