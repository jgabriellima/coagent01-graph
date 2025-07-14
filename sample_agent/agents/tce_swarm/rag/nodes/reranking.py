"""
Reranking Node for TCE-PA RAG Pipeline
Reorders chunks based on multiple juridical criteria and combined scoring
"""

from ..utils import llm
from ..models.state import TCE_RAG_State
from ..models.chunks import RerankedChunk
from ..models.responses import RerankingResult
import time

def reranking_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Reordena chunks baseado em múltiplos critérios de relevância
    """
    
    start_time = time.time()
    
    instruction = f"""
    Reordene chunks baseado em múltiplos critérios jurídicos:
    
    Query: {state.processed_query}
    Tipo: {state.query_type}
    
    Critérios de ranking:
    1. Relevância semântica (peso 0.3)
    2. Relevância jurídica (peso 0.25)
    3. Relevância temporal (peso 0.2)
    4. Especificidade TCE-PA (peso 0.15)
    5. Qualidade do contexto (peso 0.1)
    
    Chunks para reranking: {len(state.enriched_context)}
    """
    
    reranking_result = llm(instruction, RerankingResult,
                          query=state.processed_query,
                          enriched_chunks=state.enriched_context,
                          query_type=state.query_type)
    
    # Simular reranking de cada chunk
    reranked_chunks = []
    for i, enriched_chunk in enumerate(state.enriched_context):
        # Calcular score combinado
        combined_score = (
            enriched_chunk.semantic_relevance * 0.3 +
            enriched_chunk.juridical_relevance * 0.25 +
            enriched_chunk.temporal_relevance * 0.2 +
            enriched_chunk.tce_specificity * 0.15 +
            0.8 * 0.1  # Qualidade do contexto padrão
        )
        
        ranking_factors = {
            "semantic": enriched_chunk.semantic_relevance,
            "juridical": enriched_chunk.juridical_relevance,
            "temporal": enriched_chunk.temporal_relevance,
            "tce_specificity": enriched_chunk.tce_specificity,
            "context_quality": 0.8
        }
        
        reranked_chunk = RerankedChunk(
            chunk=enriched_chunk,
            final_score=combined_score,
            ranking_factors=ranking_factors
        )
        reranked_chunks.append(reranked_chunk)
    
    # Ordenar por score final
    reranked_chunks.sort(key=lambda x: x.final_score, reverse=True)
    
    # Selecionar top 5 chunks para geração
    top_chunks = reranked_chunks[:5]
    
    reranking_time = time.time() - start_time
    
    return state.copy(
        reranked_chunks=top_chunks,
        processing_time=state.processing_time + reranking_time
    ) 