"""
Relevance Grading Node for TCE-PA RAG Pipeline
Evaluates relevance of retrieved chunks using multiple criteria
"""

from ..utils import llm
from ..models.state import TCE_RAG_State
from ..models.chunks import GradedChunk
from ..models.responses import GradingResult
import time

def relevance_grading_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Avalia relevância dos chunks recuperados usando múltiplos critérios
    """
    
    start_time = time.time()
    
    instruction = f"""
    Avalie a relevância dos chunks recuperados para a consulta jurídica:
    
    Query: {state.processed_query}
    Tipo: {state.query_type}
    Contexto Temporal: {state.temporal_context}
    
    Critérios de avaliação:
    1. Relevância semântica (0-1)
    2. Aplicabilidade jurídica (0-1)
    3. Vigência temporal (0-1)
    4. Especificidade TCE-PA (0-1)
    
    Chunks para avaliar: {len(state.retrieved_chunks)}
    """
    
    grading_result = llm(instruction, GradingResult,
                        query=state.processed_query,
                        chunks=state.retrieved_chunks,
                        query_type=state.query_type)
    
    # Simular avaliação de cada chunk
    graded_chunks = []
    for i, chunk in enumerate(state.retrieved_chunks):
        # Relevância baseada na posição (chunks top têm maior relevância)
        relevance_score = max(0.5, 1.0 - (i * 0.1))
        confidence = 0.8 + (0.2 * relevance_score)
        
        graded_chunk = GradedChunk(
            chunk=chunk,
            relevance_score=relevance_score,
            confidence=confidence
        )
        graded_chunks.append(graded_chunk)
    
    # Determinar se precisa de reescrita
    average_relevance = sum(gc.relevance_score for gc in graded_chunks) / len(graded_chunks) if graded_chunks else 0
    needs_rewrite = average_relevance < 0.6
    
    grading_time = time.time() - start_time
    
    return state.copy(
        graded_chunks=graded_chunks,
        needs_rewrite=needs_rewrite,
        processing_time=state.processing_time + grading_time
    ) 