"""
Query Analysis Node for TCE-PA RAG Pipeline
Analyzes user queries and determines processing strategy
"""

from ..utils import llm
from ..models.state import TCE_RAG_State
from ..models.responses import QueryAnalysisResult

def query_analysis_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Analisa query usando LLM structured output para classificação inteligente
    """
    
    instruction = f"""
    Analise a consulta e classifique conforme padrões de documentos oficiais do tribunal de contas:
    
    Query: "{state.original_query}"
    
    Determine:
    1. Tipo de consulta (legislation, acordao, resolucao, jurisprudencia)
    2. Complexidade (simple, medium, complex)
    3. Contexto temporal necessário
    4. Bases de dados relevantes
    5. Se necessita ingestão de novos documentos
    
    Considere padrões típicos de consultas em documentos oficiais.
    """
    
    analysis = llm(instruction, QueryAnalysisResult, 
                   query=state.original_query, 
                   user_context=state.user_id)
    
    return state.copy(
        processed_query=analysis.processed_query,
        query_type=analysis.query_type,
        query_complexity=analysis.query_complexity,
        target_databases=analysis.target_databases,
        temporal_context=analysis.temporal_context,
        needs_ingestion=analysis.needs_ingestion
    ) 