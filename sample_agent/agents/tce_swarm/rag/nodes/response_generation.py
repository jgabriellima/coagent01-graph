"""
Response Generation Node for TCE-PA RAG Pipeline
Generates final response with juridical context and specific citations
"""

from ..utils import llm
from ..models.state import TCE_RAG_State
from ..models.chunks import Citation
from ..models.responses import ResponseGenerationResult
import time

def response_generation_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Gera resposta final com contexto jurídico e citações específicas
    """
    
    start_time = time.time()
    
    # Construir contexto a partir dos top chunks
    context_parts = []
    citations = []
    
    for i, reranked_chunk in enumerate(state.reranked_chunks):
        chunk_content = reranked_chunk.chunk.chunk.content
        context_parts.append(f"[{i+1}] {chunk_content}")
        
        # Criar citação baseada no chunk
        citation = Citation(
            source=f"TCE-PA Doc {i+1}",
            document_type=state.query_type,
            document_number=f"DOC-{i+1:03d}",
            excerpt=chunk_content[:100] + "..." if len(chunk_content) > 100 else chunk_content,
            confidence=reranked_chunk.final_score
        )
        citations.append(citation)
    
    final_context = "\n\n".join(context_parts)
    
    instruction = f"""
    Como assistente jurídico especializado do TCE-PA, gere uma resposta formal e precisa:
    
    CONSULTA: {state.original_query}
    
    CONTEXTO JURÍDICO:
    {final_context}
    
    DIRETRIZES:
    1. Use linguagem formal e técnica apropriada
    2. Cite fontes específicas usando formato [fonte]
    3. Indique vigência temporal quando relevante
    4. Destaque especificidades do TCE-PA
    5. Mantenha precisão jurídica
    6. Estruture a resposta de forma clara
    
    CONTEXTO TEMPORAL: {state.temporal_context or "Atual"}
    TIPO DE CONSULTA: {state.query_type}
    """
    
    generation_result = llm(instruction, ResponseGenerationResult,
                           query=state.original_query,
                           context=final_context,
                           query_type=state.query_type,
                           temporal_context=state.temporal_context)
    
    # Simular geração de resposta
    if not generation_result.response_text:
        # Fallback para resposta básica
        generation_result.response_text = f"""
Com base na consulta sobre "{state.original_query}" e na análise dos documentos do TCE-PA, posso fornecer as seguintes informações:

{final_context[:500]}...

Esta resposta é baseada em {len(state.reranked_chunks)} documentos relevantes do TCE-PA e considera o contexto jurídico específico da consulta.

Fontes consultadas: {', '.join([f'[{i+1}]' for i in range(len(citations))])}
"""
    
    generation_time = time.time() - start_time
    state.total_tokens_used += generation_result.tokens_used if hasattr(generation_result, 'tokens_used') else 500
    
    return state.copy(
        generated_response=generation_result.response_text,
        citations=citations,
        final_context=final_context,
        quality_score=generation_result.confidence_score if hasattr(generation_result, 'confidence_score') else 0.8,
        processing_time=state.processing_time + generation_time
    ) 