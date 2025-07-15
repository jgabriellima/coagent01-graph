"""
Relevance Grading Node for RAG Pipeline
Evaluates and grades chunks based on relevance to query
"""

from pydantic import BaseModel, Field
from typing import List
from ..utils import llm
from ..models.state import RAGState
from ..models.chunks import GradedChunk
import time


class GradedChunksResponse(BaseModel):
    """Response model for graded chunks generation"""
    graded_chunks: List[GradedChunk] = Field(
        description="List of chunks graded by relevance to the query"
    )


def relevance_grading_node(state: RAGState) -> RAGState:
    """
    Avalia relevância dos chunks para a query processada
    """

    start_time = time.time()

    # Single LLM call to generate graded chunks
    instruction = f"""
    Grade chunks for relevance to query: "{state.processed_query}"
    
    For each chunk, provide:
    - Relevance score (0.0-1.0)
    - Grading justification
    - Key relevance factors
    
    Query type: {state.query_type}
    Query complexity: {state.query_complexity}
    """

    response = llm(
        instruction,
        GradedChunksResponse,
        retrieved_chunks=state.retrieved_chunks,
        query=state.processed_query,
        query_type=state.query_type,
    )

    # Update metrics and return
    state.processing_time = time.time() - start_time

    return state.copy(
        graded_chunks=response.graded_chunks,
    )
