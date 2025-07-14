"""
Context Enrichment Node for TCE-PA RAG Pipeline
Enriches chunks with juridical context, cross-references, and temporal information
"""

from ..utils import llm
from ..models.state import TCE_RAG_State
from ..models.chunks import EnrichedChunk
from ..models.responses import EnrichmentResult
import time

def context_enrichment_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Enriquece contexto dos chunks com informações jurídicas específicas
    """
    
    start_time = time.time()
    
    instruction = f"""
    Enriqueça o contexto dos chunks com informações jurídicas específicas:
    
    Query: {state.processed_query}
    Contexto Jurídico: {state.juridical_context}
    Contexto Temporal: {state.temporal_context}
    
    Para cada chunk, determine:
    1. Relevância semântica (0-1)
    2. Relevância jurídica (0-1)  
    3. Relevância temporal (0-1)
    4. Especificidade TCE-PA (0-1)
    5. Contexto enriquecido
    6. Referências cruzadas
    
    Chunks para enriquecer: {len(state.graded_chunks)}
    """
    
    enrichment_result = llm(instruction, EnrichmentResult,
                           query=state.processed_query,
                           graded_chunks=state.graded_chunks,
                           juridical_context=state.juridical_context)
    
    # Simular enriquecimento de cada chunk
    enriched_chunks = []
    for graded_chunk in state.graded_chunks:
        # Só enriquecer chunks com relevância adequada
        if graded_chunk.relevance_score > 0.6:
            enriched_chunk = EnrichedChunk(
                chunk=graded_chunk.chunk,
                semantic_relevance=graded_chunk.relevance_score,
                juridical_relevance=min(1.0, graded_chunk.relevance_score + 0.1),
                temporal_relevance=0.8 if state.temporal_context else 0.5,
                tce_specificity=0.9,  # Alta especificidade para TCE-PA
                enriched_context=f"Contexto enriquecido para: {graded_chunk.chunk.content[:50]}...",
                cross_references=[f"ref_{i}" for i in range(2)]
            )
            enriched_chunks.append(enriched_chunk)
    
    enrichment_time = time.time() - start_time
    
    return state.copy(
        enriched_context=enriched_chunks,
        needs_enrichment=False,
        processing_time=state.processing_time + enrichment_time
    ) 