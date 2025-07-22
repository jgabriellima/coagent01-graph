"""
Document Retrieval Node for RAG Pipeline
Executes hybrid retrieval with access filters and multiple collections
"""

from ..utils import llm
from ..models.state import RAGState
from ..models.chunks import ChunkingResult
import time

def document_retrieval_node(state: RAGState) -> RAGState:
    """
    Mock document retrieval - just return chunks via LLM
    """
    
    start_time = time.time()
    
    # Single LLM call to generate chunks
    instruction = f"""
    Generate ONLY 3 realistic document small chunks that would be retrieved for: "{state.processed_query}"
    Make it sound like actual institutional document content relevant to the query.
    Return as ChunkingResult with chunks list.
    """
    
    result = llm(instruction, ChunkingResult)
    
    # Update metrics and return
    state.retrieval_time = time.time() - start_time
    state.vector_db_queries = 2  # Mock query count
    
    return state.copy(retrieved_chunks=result.chunks)
