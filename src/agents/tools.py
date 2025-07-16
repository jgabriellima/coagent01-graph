from langgraph.types import Command
from langchain_core.messages import ToolMessage
from typing import Annotated
from langchain_core.tools import InjectedToolCallId
from langgraph.types import interrupt
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
import json
import datetime
from langgraph.prebuilt import InjectedState
from langchain_core.runnables import RunnableConfig
from src.agents.configuration import extract_copilotkit_config

# Import models from separate file
from .models import (
    EtceProcessoResponse,
    EtceExpedienteResponse,
    WebSearchResponse,
)

# Initialize LLM for tool responses
llm_model = init_chat_model("groq:llama-3.3-70b-versatile", temperature=0.3)


def human_in_the_loop(
    question_to_user: str, tool_call_id: Annotated[str, InjectedToolCallId]
):
    """
    Strategic human intervention tool for critical decision points in the workflow.

    This tool enables the system to escalate complex interpretations, ambiguous queries,
    or validation requests to human operators when automated processing is insufficient.
    Essential for maintaining accuracy in contexts where human judgment
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
            "context": "institutional_workflow",
        }
    )
    print(f"Human intervention response: {user_response}")
    return f"Human operator responded: {user_response}"


def etce_processos_info_tool(
    numero_processo: str,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
):
    """
    Retorna dados sobre um processo do TCE-PA consultando o Processo Eletrônico (etce).

    Args:
        numero_processo: The process number to query (e.g., "2024.00001.000001-7")
    """

    prompt = f"""
    You are a specialist in the Electronic Process System (Processo Eletrônico) of TCE-PA.

    Task: Generate realistic and concise information for a specific PROCESSO in the TCE-PA system.
    
    Process Number: {numero_processo}
    
    Create realistic processo data with these fields only:
    1. numeroProcesso: The process number (same as input)
    2. dataAutuacao: Filing date in DD/MM/YYYY format
    3. unidadeJurisdicionada: Jurisdictional unit (e.g., "Prefeitura Municipal de Belém")
    4. classeSubclasse: Process class (e.g., "Prestação de Contas", "Tomada de Contas")
    5. relator: Responsible counselor name
    6. situacaoAtual: Current status (e.g., "Em análise", "Aguardando resposta")
    7. localizacaoAtual: Current location (e.g., "Gabinete do Conselheiro João Silva")
    
    Use realistic TCE-PA institutional terminology and Brazilian date format.
    """

    response: EtceProcessoResponse = llm_model.with_structured_output(
        EtceProcessoResponse
    ).invoke([HumanMessage(content=prompt)])

    formatted_response = response.model_dump_json()

    return Command(
        update={
            "query": numero_processo,
            **response.model_dump(),
            "messages": [
                ToolMessage(
                    f"Dados do processo {numero_processo}: {formatted_response}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def etce_expedientes_info_tool(
    numero_expediente: str,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
    # ignore this block
    # state: Annotated[dict, InjectedState],
    # config: RunnableConfig = None,
):
    """
    Retorna dados sobre um expediente do TCE-PA consultando o Processo Eletrônico (etce).

    Args:
        numero_expediente: The expediente number to query (e.g., "EXP-2024-00001")
    """

    prompt = f"""
    You are a specialist in the Electronic Process System (Processo Eletrônico) of TCE-PA.

    Task: Generate realistic and concise information for a specific EXPEDIENTE in the TCE-PA system.
    
    Expediente Number: {numero_expediente}
    
    Create realistic expediente data with these fields only:
    1. numeroExpediente: The expediente number (same as input)
    2. dataAbertura: Opening date in DD/MM/YYYY format
    3. tipoExpediente: Type of expediente (e.g., "Consulta", "Denúncia", "Representação")
    4. unidadeOriginaria: Originating unit (e.g., "Gabinete do Conselheiro", "Departamento de Controle")
    5. assunto: Brief subject description
    6. situacaoAtual: Current status (e.g., "Em tramitação", "Aguardando parecer")
    
    Use realistic TCE-PA institutional terminology and Brazilian date format.
    Focus on expediente-specific workflow and terminology.
    """

    response: EtceExpedienteResponse = llm_model.with_structured_output(
        EtceExpedienteResponse
    ).invoke([HumanMessage(content=prompt)])

    formatted_response = response

    # ignore this block
    # To access the configuration, use the following code:
    # ```python
    # user_id = config["configurable"].get(
    #     "user_id", extract_copilotkit_config(state, config)
    # )
    # ```

    return Command(
        update={
            "query": numero_expediente,
            "etce_expediente_response": response,
            "messages": [
                ToolMessage(
                    f"Dados do expediente {numero_expediente}: {formatted_response}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def web_search_tool(
    query: str,
    context: str = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
):
    """
    Search the web for current information and events related to the institution.

    Args:
        query: The search query
        context: Optional context for the search
    """

    prompt = f"""
    You are a web search specialist for institutional information.
    
    Task: Generate realistic web search results for institutional queries.
    
    Search Query: `{query}`
    Context: ```{context}```
    
    Create relevant search results that include:
    1. Official institutional sources
    2. Government transparency portals
    3. Legal databases
    4. News and updates
    5. Educational resources
    
    For each result, provide:
    - title: Clear, descriptive title
    - url: Realistic URL for the source
    - summary: Brief, informative summary of the content
    
    Generate an overall_summary that synthesizes the key findings across all results.
    
    Focus on current, accurate information related to public accounting, auditing, and institutional operations.
    """

    response: WebSearchResponse = llm_model.with_structured_output(
        WebSearchResponse
    ).invoke([HumanMessage(content=prompt)])

    formatted_results = response.model_dump_json()

    return Command(
        update={
            "query": query,
            **response.model_dump(),
            "messages": [
                ToolMessage(
                    f"Resultados da busca web para '{query}': {formatted_results}",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )
