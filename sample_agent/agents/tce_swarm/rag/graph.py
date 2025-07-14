"""
TCE-PA RAG Subgraph
Implements complete RAG pipeline with customized workflow and conditional edges
"""

from langgraph.graph import StateGraph, END
from langsmith import traceable
from typing import Dict, Any

from .models.state import TCE_RAG_State
from .nodes import (
    vector_db_setup_node,
    query_analysis_node,
    chunk_strategy_node,
    document_ingestion_node,
    document_retrieval_node,
    relevance_grading_node,
    context_enrichment_node,
    reranking_node,
    response_generation_node
)

def needs_ingestion_decision(state: TCE_RAG_State) -> str:
    """Decide se necessita ingestão de documentos"""
    return "ingestion" if state.needs_ingestion else "continue"

def needs_rewrite_decision(state: TCE_RAG_State) -> str:
    """Decide se necessita reescrita da query"""
    return "rewrite" if state.needs_rewrite else "continue"

def quality_check_decision(state: TCE_RAG_State) -> str:
    """Decide se qualidade está adequada ou precisa retry"""
    if state.quality_score > 0.7:
        return "complete"
    elif state.retry_count < state.max_retries:
        return "retry"
    else:
        return "complete"  # Força conclusão após max retries

def query_rewrite_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """Node para reescrita da query quando necessário"""
    
    from .utils import llm
    
    instruction = f"""
    Reescreva a query para melhorar a recuperação de documentos:
    
    Query Original: {state.original_query}
    Query Atual: {state.processed_query}
    Tipo: {state.query_type}
    
    Problemas identificados:
    - Relevância baixa: {state.needs_rewrite}
    - Retry count: {state.retry_count}
    
    Gere uma query reformulada que seja mais específica e direcionada.
    """
    
    rewritten_query = llm(instruction, None, 
                         original_query=state.original_query,
                         current_query=state.processed_query,
                         query_type=state.query_type)
    
    return state.copy(
        processed_query=rewritten_query,
        needs_rewrite=False,
        retry_count=state.retry_count + 1
    )

def quality_validation_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """Node para validação da qualidade da resposta"""
    
    from .utils import llm
    from .models.responses import ValidationResult
    
    instruction = f"""
    Valide a qualidade da resposta gerada:
    
    Query: {state.original_query}
    Resposta: {state.generated_response}
    Citações: {len(state.citations)}
    
    Critérios de validação:
    1. Precisão jurídica
    2. Relevância da resposta
    3. Qualidade das citações
    4. Completude da informação
    5. Formato adequado
    
    Determine se a resposta atende aos padrões de qualidade.
    """
    
    validation = llm(instruction, ValidationResult,
                    query=state.original_query,
                    response=state.generated_response,
                    citations=state.citations)
    
    return state.copy(
        validation_passed=validation.validation_passed,
        quality_score=validation.quality_score
    )

@traceable(name="TCE_RAG_Pipeline", tags=["rag", "pipeline", "tce-pa"])
def create_tce_rag_subgraph():
    """
    Creates the TCE-PA RAG subgraph with customized workflow
    """
    
    # Create StateGraph
    rag_graph = StateGraph(TCE_RAG_State)
    
    # Add all nodes
    rag_graph.add_node("vector_db_setup", vector_db_setup_node)
    rag_graph.add_node("query_analysis", query_analysis_node)
    rag_graph.add_node("chunk_strategy_selection", chunk_strategy_node)
    rag_graph.add_node("document_ingestion", document_ingestion_node)
    rag_graph.add_node("document_retrieval", document_retrieval_node)
    rag_graph.add_node("relevance_grading", relevance_grading_node)
    rag_graph.add_node("query_rewrite", query_rewrite_node)
    rag_graph.add_node("context_enrichment", context_enrichment_node)
    rag_graph.add_node("reranking", reranking_node)
    rag_graph.add_node("response_generation", response_generation_node)
    rag_graph.add_node("quality_validation", quality_validation_node)
    
    # Set entry point
    rag_graph.set_entry_point("vector_db_setup")
    
    # Linear flow inicial
    rag_graph.add_edge("vector_db_setup", "query_analysis")
    
    # Conditional para ingestão
    rag_graph.add_conditional_edges(
        "query_analysis",
        needs_ingestion_decision,
        {
            "ingestion": "chunk_strategy_selection",
            "continue": "document_retrieval"
        }
    )
    
    # Fluxo de ingestão
    rag_graph.add_edge("chunk_strategy_selection", "document_ingestion")
    rag_graph.add_edge("document_ingestion", "document_retrieval")
    
    # Fluxo principal de retrieval
    rag_graph.add_edge("document_retrieval", "relevance_grading")
    
    # Conditional para reescrita
    rag_graph.add_conditional_edges(
        "relevance_grading",
        needs_rewrite_decision,
        {
            "rewrite": "query_rewrite",
            "continue": "context_enrichment"
        }
    )
    
    # Query rewrite volta para retrieval
    rag_graph.add_edge("query_rewrite", "document_retrieval")
    
    # Fluxo final de processamento
    rag_graph.add_edge("context_enrichment", "reranking")
    rag_graph.add_edge("reranking", "response_generation")
    rag_graph.add_edge("response_generation", "quality_validation")
    
    # Conditional para qualidade
    rag_graph.add_conditional_edges(
        "quality_validation",
        quality_check_decision,
        {
            "retry": "query_rewrite",
            "complete": END
        }
    )
    
    # Compile the graph
    compiled_graph = rag_graph.compile()
    
    return compiled_graph

# Create the subgraph instance
tce_rag_subgraph = create_tce_rag_subgraph()

__all__ = ["create_tce_rag_subgraph", "tce_rag_subgraph"] 