"""
Chunk Strategy Selection Node for TCE-PA RAG Pipeline
Selects optimal chunking strategy based on document type and query complexity
"""

from ..utils import llm
from ..models.state import TCE_RAG_State
from ..models.responses import ChunkStrategyResult

def chunk_strategy_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Seleciona estratégia de chunking via LLM baseada no contexto
    """
    
    instruction = f"""
    Selecione a estratégia de chunking mais adequada para:
    
    Tipo de Consulta: {state.query_type}
    Complexidade: {state.query_complexity}
    Bases de Dados: {state.target_databases}
    
    Estratégias disponíveis:
    - recursive: Estrutura hierárquica preservada
    - semantic: Agrupamento semântico
    - sdpm: Precisão semântica máxima
    - late: Contexto global preservado
    
    Considere características específicas de documentos estruturados.
    """
    
    strategy = llm(instruction, ChunkStrategyResult,
                   query_type=state.query_type,
                   complexity=state.query_complexity,
                   databases=state.target_databases)
    
    return state.copy(
        selected_chunker=strategy.selected_strategy,
        chunk_size=strategy.chunk_size,
        chunk_overlap=strategy.chunk_overlap,
        chunking_metadata=strategy.configuration
    ) 