"""
Query Analysis Node for RAG Pipeline
Analyzes user queries and determines processing strategy
"""

from ..utils import llm
from ..models.state import RAGState
from ..models.responses import QueryAnalysisResult, DocumentToIngest


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
    Analise a consulta e classifique conforme padrões de documentos oficiais:
    
    Query: "{state.messages[-1].content}"
    Arquivos fornecidos: {state.file_paths}
    Documentos já processados: {state.user_documents}
    
    Determine:
    1. Tipo de consulta (legislation, acordao, resolucao, jurisprudencia)
    2. Complexidade (simple, medium, complex)
    3. Contexto temporal necessário
    4. Bases de dados relevantes
    5. Processamento de arquivos:
       - Se há arquivos novos em file_paths: ingestion_required=True
       - Se todos os arquivos já foram processados: ingestion_required=False
       - Se não há arquivos: ingestion_required=False
    
    IMPORTANTE: ingestion_required deve ser {needs_ingestion} baseado na verificação de arquivos.
    
    Considere padrões típicos de consultas em documentos oficiais.
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
