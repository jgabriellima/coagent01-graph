"""
Document Retrieval Node for TCE-PA RAG Pipeline
Executes hybrid retrieval with access filters and multiple collections
"""

from ..utils import llm, mock_vector_search
from ..models.state import TCE_RAG_State
from ..models.responses import RetrievalResult
import time

def document_retrieval_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Executa retrieval híbrido nos chunks já armazenados
    """
    
    start_time = time.time()
    
    # Configurar filtros baseados no escopo
    base_filters = {
        "temporal_context": state.temporal_context,
        "juridical_context": state.juridical_context,
        **state.document_filters
    }
    
    # Aplicar filtros de acesso baseados no escopo
    if state.document_scope == "user_specific":
        base_filters["user_id"] = state.user_id
        base_filters["doc_id"] = {"$in": state.user_documents}
    elif state.document_scope == "session_specific":
        base_filters["session_id"] = state.session_id
    elif state.document_scope == "global":
        base_filters["document_scope"] = "global"
    
    # Busca em múltiplas collections
    all_chunks = []
    state.vector_db_queries = 0
    
    for collection in state.collection_names:
        # Mock da busca semântica
        semantic_results = mock_vector_search(
            state.processed_query,
            collection,
            {**base_filters, "search_type": "semantic"}
        )
        
        # Mock da busca por keywords
        keyword_results = mock_vector_search(
            state.processed_query,
            collection,
            {**base_filters, "search_type": "keyword"}
        )
        
        # Combinar resultados
        instruction = f"""
        Combine resultados de busca semântica e keyword:
        
        Semantic Results: {len(semantic_results.chunks)} chunks
        Keyword Results: {len(keyword_results.chunks)} chunks
        
        Pesos: Semantic 0.7, Keyword 0.3
        
        Retorne top 10 chunks combinados sem duplicatas.
        """
        
        combined = llm(instruction, RetrievalResult,
                      semantic_results=semantic_results.chunks,
                      keyword_results=keyword_results.chunks,
                      query=state.processed_query,
                      collection=collection)
        
        all_chunks.extend(combined.chunks_found)
        state.vector_db_queries += 2  # Semantic + keyword
    
    # Deduplicação e ranking final
    instruction = f"""
    Deduplique e rankeie {len(all_chunks)} chunks por relevância:
    
    Query: {state.processed_query}
    
    Retorne top 10 chunks únicos ordenados por relevância.
    """
    
    from ..models.chunks import ChunkResult
    
    # Simular chunks como ChunkResult
    mock_chunks = []
    for i in range(min(10, len(all_chunks))):
        mock_chunks.append(ChunkResult(
            content=f"Mock chunk {i+1} content for query: {state.processed_query}",
            metadata={"relevance": 0.9 - i*0.1, "source": f"tce_doc_{i+1}"},
            chunk_id=f"chunk_{i+1}"
        ))
    
    # Atualizar métricas
    state.retrieval_time = time.time() - start_time
    
    return state.copy(retrieved_chunks=mock_chunks) 