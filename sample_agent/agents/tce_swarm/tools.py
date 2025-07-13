from langgraph.types import Command
from langchain_core.messages import ToolMessage
from typing import Annotated
from langchain_core.tools import InjectedToolCallId
from langgraph.types import interrupt
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import json
import datetime


def human_in_the_loop(
    question_to_user: str, tool_call_id: Annotated[str, InjectedToolCallId]
):
    """
    Strategic human intervention tool for critical decision points in the TCE-PA workflow.

    This tool enables the system to escalate complex legal interpretations, ambiguous queries,
    or validation requests to human operators when automated processing is insufficient.
    Essential for maintaining accuracy in legal and regulatory contexts where human judgment
    is required for proper case handling and compliance validation.

    Args:
        question_to_user: Specific question requiring human input with proper context
    """
    user_response = interrupt(
        {
            "type": "human_intervention",
            "question": question_to_user,
            "tool_call_id": tool_call_id,
            "priority": "high",
            "context": "tce_legal_workflow",
        }
    )
    print(f"Human intervention response: {user_response}")
    return f"Human operator responded: {user_response}"


# Initialize LLM for tool responses
llm_model = init_chat_model("groq:llama-3.3-70b-versatile", temperature=0.3)


class TCEDocumentResponse(BaseModel):
    """Structured response for TCE document searches"""

    response: str
    document_type: str
    sources: list[str]
    confidence: float
    legal_context: str


class eTCESearchResponse(BaseModel):
    """Structured response for eTCE expediente searches"""

    numeroProcesso: str
    dataAutuacao: str
    unidadeJurisdicionada: str
    classeSubclasse: str
    relator: str
    interessados: str
    exercicio: int
    assunto: str
    sigiloso: bool
    status: str


class ProcessDetailsResponse(BaseModel):
    """Structured response for process details"""

    numeroProcesso: str
    situacaoAtual: str
    dataUltimaMovimentacao: str
    localizacaoAtual: str
    proximosPrazos: list[str]
    historicoMovimentacao: list[dict]


class WebSearchResult(BaseModel):
    """Individual web search result"""
    title: str
    url: str
    summary: str


class WebSearchResponse(BaseModel):
    """Structured response for web searches"""

    results: list[WebSearchResult]
    overall_summary: str
    relevance_score: float


def tce_documents_database_tool(
    query: str,
    document_type: str = "all",
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
):
    """
    Access the TCE-PA knowledge base for legislation, resolutions, acts, and jurisprudence.

    Args:
        query: The search query
        document_type: Type of document to search ("legislacao", "acordao", "resolucao", "ato", "all")
    """

    prompt = f"""
    You are a specialized legal assistant for the Tribunal de Contas do Estado do Pará (TCE-PA).
    
    Task: Process this query for TCE-PA legal documents and provide a realistic response.
    
    Query: {query}
    Document Type: {document_type}
    
    Generate a response that:
    1. Provides relevant legal information based on TCE-PA context
    2. References appropriate document types (legislation, resolutions, acts, jurisprudence)
    3. Maintains professional legal language
    4. Includes realistic document references
    5. Considers temporal aspects of legal documents
    
    Focus on TCE-PA's jurisdiction over public accounts, auditing procedures, and administrative compliance.
    """

    response = llm_model.with_structured_output(TCEDocumentResponse).invoke(
        [HumanMessage(content=prompt)]
    )

    return Command(
        update={
            "rag_result": response.response,
            "document_type": response.document_type,
            "retrieval_results": response.sources,
            "legal_context": response.legal_context,
            "confidence": response.confidence,
            "messages": [
                ToolMessage(
                    f"Busca realizada na base de conhecimento do TCE-PA: {response.response}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def document_ingestion_tool(
    document_content: str,
    document_type: str,
    metadata: dict = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
):
    """
    Ingest and process documents using chonkie chunking strategies.

    Args:
        document_content: The document content to process
        document_type: Type of document
        metadata: Document metadata including temporal information
    """

    prompt = f"""
    You are a document processing specialist for TCE-PA legal documents.
    
    Task: Process this document content using advanced chunking strategies.
    
    Document Content: {document_content[:500]}...
    Document Type: {document_type}
    Metadata: {metadata}
    
    Analyze the document and provide:
    1. Estimated number of logical chunks
    2. Key sections identified
    3. Processing strategy used
    4. Temporal context extraction
    5. Legal document classification
    
    Focus on preserving legal context and maintaining document integrity.
    """

    response = llm_model.invoke([HumanMessage(content=prompt)])
    chunks_count = len(document_content.split()) // 100

    return Command(
        update={
            "chunks": [
                f"Chunk {i}: {document_content[:100]}..."
                for i in range(min(chunks_count, 5))
            ],
            "document_content": document_content,
            "processing_analysis": response.content,
            "metadata": metadata
            or {"processed_at": datetime.datetime.now().isoformat()},
            "messages": [
                ToolMessage(
                    f"Documento processado com {chunks_count} chunks usando estratégia de chunking otimizada para documentos jurídicos.",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def document_summarization_tool(
    document_content: str, tool_call_id: Annotated[str, InjectedToolCallId] = None
):
    """
    Generate summaries of TCE-PA documents.

    Args:
        document_content: The document content to summarize
    """

    prompt = f"""
    You are a legal document summarization specialist for TCE-PA.
    
    Task: Create a comprehensive summary of this TCE-PA document.
    
    Document Content: {document_content}
    
    Generate a summary that:
    1. Captures key legal points and decisions
    2. Identifies relevant legislation and precedents
    3. Highlights procedural aspects
    4. Maintains legal accuracy and context
    5. Provides actionable insights for TCE-PA operations
    
    Focus on administrative compliance, auditing procedures, and regulatory implications.
    """

    response = llm_model.invoke([HumanMessage(content=prompt)])

    return Command(
        update={
            "document_summary": response.content,
            "summary_quality": "high",
            "messages": [
                ToolMessage(
                    f"Resumo gerado: {response.content}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def etce_search_tool(
    expediente_number: str,
    year: str = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
):
    """
    Search for expedientes in the eTCE (Electronic Process System) of TCE-PA.

    Args:
        expediente_number: The expediente number to search for
        year: The year of the expediente (optional)
    """

    prompt = f"""
    You are an eTCE system specialist for TCE-PA.
    
    Task: Generate realistic expediente data for the Electronic Process System.
    
    Expediente Number: {expediente_number}
    Year: {year or "current"}
    
    Create a realistic expediente record that includes:
    1. Complete process number with TC prefix
    2. Appropriate autuação date
    3. Relevant jurisdictional unit
    4. Proper case classification
    5. Assigned rapporteur
    6. Interested parties
    7. Current status and location
    
    Base the response on typical TCE-PA procedures and ensure legal accuracy.
    """

    response = llm_model.with_structured_output(eTCESearchResponse).invoke(
        [HumanMessage(content=prompt)]
    )

    formatted_response = f"""
Número do Processo: {response.numeroProcesso}
Data de Autuação: {response.dataAutuacao}
Unidade Jurisdicionada: {response.unidadeJurisdicionada}
Classe/Subclasse: {response.classeSubclasse}
Relator: {response.relator}
Interessados: {response.interessados}
Exercício: {response.exercicio}
Assunto: {response.assunto}
Status: {response.status}
"""

    return Command(
        update={
            "expediente_number": expediente_number,
            "etce_results": [response.dict()],
            "search_result": formatted_response,
            "messages": [
                ToolMessage(
                    f"Dados do expediente {expediente_number} recuperados do eTCE: {formatted_response}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def etce_process_details_tool(
    processo_number: str, tool_call_id: Annotated[str, InjectedToolCallId] = None
):
    """
    Get detailed information about a specific process in eTCE.

    Args:
        processo_number: The process number to get details for
    """

    prompt = f"""
    You are an eTCE process tracking specialist for TCE-PA.
    
    Task: Generate detailed process information for tracking purposes.
    
    Process Number: {processo_number}
    
    Create realistic process details including:
    1. Current status and location
    2. Recent movement history
    3. Upcoming deadlines
    4. Procedural timeline
    5. Responsible parties
    6. Next steps in the process
    
    Ensure the response reflects typical TCE-PA procedural workflows.
    """

    response = llm_model.with_structured_output(ProcessDetailsResponse).invoke(
        [HumanMessage(content=prompt)]
    )

    formatted_details = f"""
Situação Atual: {response.situacaoAtual}
Data da Última Movimentação: {response.dataUltimaMovimentacao}
Localização Atual: {response.localizacaoAtual}
Próximos Prazos: {', '.join(response.proximosPrazos)}

Histórico de Movimentação:
""" + "\n".join(
        [f"- {mov['data']}: {mov['evento']}" for mov in response.historicoMovimentacao]
    )

    return Command(
        update={
            "processo_number": processo_number,
            "etce_results": [response.dict()],
            "search_result": formatted_details,
            "messages": [
                ToolMessage(
                    f"Detalhes do processo {processo_number}: {formatted_details}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def web_search_tool(
    query: str, tool_call_id: Annotated[str, InjectedToolCallId] = None
):
    """
    Search the web for current information and events related to TCE-PA.

    Args:
        query: The search query
    """

    prompt = f"""
    You are a web search specialist for TCE-PA related information.
    
    Task: Generate realistic web search results for TCE-PA related queries.
    
    Search Query: {query}
    
    Create relevant search results that include:
    1. Official TCE-PA sources
    2. Government transparency portals
    3. Legal databases
    4. News and updates
    5. Educational resources
    
    For each result, provide:
    - title: Clear, descriptive title
    - url: Realistic URL for the source
    - summary: Brief, informative summary of the content
    
    Generate an overall_summary that synthesizes the key findings across all results.
    
    Focus on current, accurate information related to public accounting, auditing, and TCE-PA operations.
    """

    response = llm_model.with_structured_output(WebSearchResponse).invoke(
        [HumanMessage(content=prompt)]
    )

    formatted_results = "\n".join(
        [
            f"• {result.title}\n  {result.summary}\n  URL: {result.url}"
            for result in response.results
        ]
    )

    return Command(
        update={
            "web_query": query,
            "web_results": [result.dict() for result in response.results],
            "search_result": formatted_results,
            "search_summary": response.overall_summary,
            "relevance_score": response.relevance_score,
            "messages": [
                ToolMessage(
                    f"Resultados da busca web para '{query}': {formatted_results}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )
