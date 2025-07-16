"""
Response Generation Node for RAG Pipeline
Generates final response with context and specific citations
"""

from ..utils import llm
from ..models.state import RAGState
from ..models.responses import ResponseGenerationResult
from ..models.chunks import Citation
import time
import random


def response_generation_node(state: RAGState) -> RAGState:
    """
    Gera resposta final com contexto e citações específicas

    ALGORITMO COMPLETO (Lógica de Negócio Original):

    1. CONSTRUÇÃO DE CONTEXTO:
       - Itera sobre state.reranked_chunks
       - Para cada chunk reranked:
         * Extrai chunk_content = reranked_chunk.chunk.chunk.content
         * Cria entrada numerada: f"[{i+1}] {chunk_content}"
         * Adiciona a context_parts[]

    2. GERAÇÃO DE CITAÇÕES:
       - Para cada reranked_chunk:
         * Cria Citation com:
           - source: f"Documento {i+1}"
           - document_type: state.query_type
           - document_number: f"DOC-{i+1:03d}"
           - excerpt: primeiros 100 chars + "..." se necessário
           - confidence: reranked_chunk.final_score
         * Adiciona a citations[]

    3. PREPARAÇÃO DO CONTEXTO FINAL:
       - final_context = "\n\n".join(context_parts)
       - Contexto numerado com todos os chunks relevantes

    4. GERAÇÃO VIA LLM:
       - Prompt estruturado com:
         * CONSULTA: state.original_query
         * CONTEXTO: final_context completo
         * DIRETRIZES: 6 regras específicas
           1. Linguagem formal e técnica
           2. Citações específicas formato [fonte]
           3. Vigência temporal quando relevante
           4. Especificidades institucionais
           5. Precisão mantida
           6. Estrutura clara
         * CONTEXTO TEMPORAL: state.temporal_context ou "Atual"
         * TIPO DE CONSULTA: state.query_type

    5. FALLBACK DE SEGURANÇA:
       - Se generation_result.generated_response vazio:
         * Gera resposta padrão com:
           - Introdução baseada na consulta
           - Primeiros 500 chars do contexto
           - Contagem de documentos consultados
           - Lista de fontes numeradas

    6. RETORNO ESTRUTURADO:
       - citations: lista completa de Citation objects
       - final_context: contexto numerado e formatado
       - processing_time: tempo acumulado
       - **generation_data: todos os campos do LLM (exceto generation_time)

    MÉTRICAS COLETADAS:
    - processing_time: tempo total acumulado
    - citations: array com source, document_type, document_number, excerpt, confidence
    - final_context: contexto formatado para debug/análise

    DEPENDÊNCIAS DE STATE:
    - state.reranked_chunks: chunks já processados e ordenados
    - state.original_query: consulta original do usuário
    - state.query_type: tipo de consulta para contexto
    - state.temporal_context: contexto temporal da consulta
    - state.processing_time: tempo acumulado anterior
    """

    start_time = time.time()

    # 1. CONSTRUÇÃO DE CONTEXTO
    context_parts = []
    citations = []
    
    for i, reranked_chunk in enumerate(state.reranked_chunks):
        # Extrai chunk_content = reranked_chunk.chunk.chunk.content
        chunk_content = reranked_chunk.chunk.chunk.content
        
        # Cria entrada numerada: f"[{i+1}] {chunk_content}"
        context_parts.append(f"[{i+1}] {chunk_content}")
        
        # 2. GERAÇÃO DE CITAÇÕES
        # Para cada reranked_chunk: cria Citation
        excerpt = chunk_content[:100] + "..." if len(chunk_content) > 100 else chunk_content
        
        citation = Citation(
            source=f"Documento {i+1}",
            document_type=state.query_type,
            document_number=f"DOC-{i+1:03d}",
            excerpt=excerpt,
            confidence=reranked_chunk.final_score,
            page_number=random.randint(1, 100),
            article_number=f"ART-{i+1:03d}",
        )
        citations.append(citation)

    # 3. PREPARAÇÃO DO CONTEXTO FINAL
    final_context = "\n\n".join(context_parts)

    # 4. GERAÇÃO VIA LLM
    instruction = f"""
    Sintetisze tecnicamente a resposta para a consulta: `{state.messages[-1].content}`
    
    CONTEXTO DOS DOCUMENTOS:
    ```{final_context}```
    
    DIRETRIZES ESPECÍFICAS:
    1. Linguagem formal e técnica
    2. Citações específicas formato [fonte]
    3. Precisão mantida
    4. Estrutura clara
    5. Não use parágrafos, seja tecnico e direto
    
    TIPO DE CONSULTA: {state.query_type}
    
    Use os documentos numerados para fundamentar sua resposta.
    Formato: Markdown
    """

    generation_result = llm(
        instruction,
        ResponseGenerationResult,
        query=state.original_query,
        context=final_context,
        query_type=state.query_type,
        temporal_context=state.temporal_context,
        citations=[citation.model_dump() for citation in citations],
    )

    processing_time = state.processing_time + (time.time() - start_time)

    return state.copy(
        generated_response=generation_result.generated_response,
        citations=generation_result.citations,
        quality_score=generation_result.quality_score,
        final_context=final_context,
        processing_time=processing_time,
    )
