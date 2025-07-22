"""
Quality Validation Node for RAG Pipeline
Validates response quality based on multiple criteria
"""

from ..utils import llm
from ..models.state import RAGState
from ..models.responses import ValidationResult
from src.utils import create_handoff_tool_with_state_propagation

def quality_validation_node(state: RAGState) -> RAGState:
    """
    Valida a qualidade da resposta gerada baseada em múltiplos critérios
    """

    instruction = f"""
    Valide a qualidade da resposta gerada:
    
    Query: {state.original_query}
    Resposta: {state.generated_response}
    Citações: {len(state.citations)}
    
    Critérios de validação:
    1. Precisão da informação
    2. Relevância da resposta
    3. Qualidade das citações
    4. Completude da informação
    5. Formato adequado
    
    Determine se a resposta atende aos padrões de qualidade.
    Se o score for baixo (< 0.5), indique que precisa de rewrite.
    """

    validation = llm(
        instruction,
        ValidationResult,
        query=state.original_query,
        response=state.generated_response,
        citations=state.citations,
        retry_count=state.retry_count,
    )

    return state.copy(
        quality_score=validation.quality_score,
        needs_rewrite=validation.needs_rewrite,
    )
