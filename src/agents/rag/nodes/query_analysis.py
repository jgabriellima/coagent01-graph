"""
Query Analysis Node for RAG Pipeline
Analyzes user queries and determines processing strategy with pattern detection
"""

import re
from ..utils import llm
from ..models.state import RAGState
from ..models.responses import QueryAnalysisResult, DocumentToIngest

from langgraph.types import Command


def handoff_to_main_agent_node(state: RAGState) -> RAGState:
    """
    Handoff to main agent or search agent with proper state propagation and validation
    
    This node handles transitions from RAG subgraph back to the parent graph,
    ensuring proper state cleanup and target validation.
    """
    # Validate handoff target exists and is valid
    if not state.handoff_to_agent:
        # Fallback: if no handoff specified, should not reach this node
        # Return to continue processing in RAG pipeline
        return state.copy(handoff_to_agent=None)
    
    # Prepare clean state update for parent graph
    update = {
        "messages": state.messages,
        "handoff_to_agent": None,  # Reset to prevent handoff loops
    }
    
    return Command(
        goto=state.handoff_to_agent,  # Target: "Main_Agent" or "Search_Agent"
        graph=Command.PARENT,         # Return to parent workflow graph
        update=update,
    )


def query_analysis_node(state: RAGState) -> RAGState:
    """
    Analisa query usando LLM structured output para classificação inteligente
    Verifica se documentos em file_paths precisam de ingestão
    """

    # Verifica se há documentos para ingestão
    needs_ingestion = False
    if state.file_paths:
        # Verifica se algum arquivo não foi processado ainda
        for file_path in state.file_paths:
            # Extrai identificador do arquivo (nome sem extensão)
            file_id = file_path.split("/")[-1].split(".")[0]

            # Verifica se o documento já foi processado
            if file_id not in state.user_documents:
                needs_ingestion = True
                break

    instruction = f"""
    Query: "{state.messages[-1].content}"
    Arquivos: {state.file_paths}
    Processados: {state.user_documents}
    
    DECISÃO DE HANDOFF:
    
    SEARCH AGENT → Expedientes (XXXXXX/YYYY), processos (TC/XXXXXX/YYYY), busca web
    MAIN AGENT → Consultas sobre capacidades/sistema, navegação, orientações gerais
    RAG LOCAL → Documentos oficiais, legislação, acordãos, jurisprudência
    
    Se handoff para Search_Agent ou Main_Agent for necessário, retorne:
    "handoff_to_agent": "Search_Agent" ou "Main_Agent"
    
    Se nao for necessário handoff, classifique:
    1. Tipo: legislation/acordao/resolucao/jurisprudencia
    2. Complexidade: simple/medium/complex
    3. Contexto temporal necessário
    4. Bases relevantes  
    5. ingestion_required: {needs_ingestion}
    
    Priorize padrões detectados sobre análise semântica.
    """

    analysis = llm(
        instruction,
        QueryAnalysisResult,
        user_context=state.user_id,
        file_paths=state.file_paths,
        user_documents=state.user_documents,
        needs_ingestion=needs_ingestion,
    )

    # Força o valor correto de ingestion_required baseado na verificação local
    analysis_dict = analysis.model_dump()
    analysis_dict["ingestion_required"] = needs_ingestion

    # Prepara documentos para ingestão se necessário
    documents_to_ingest = []
    if needs_ingestion:
        for file_path in state.file_paths:
            file_id = file_path.split("/")[-1].split(".")[0]
            if file_id not in state.user_documents:
                documents_to_ingest.append(
                    DocumentToIngest(
                        document_id=file_id,
                        document_type=file_path.split(".")[-1],
                        source_url=file_path,
                        priority=5,
                    )
                )

    analysis_dict["documents_to_ingest"] = documents_to_ingest

    return state.copy(**analysis_dict)
