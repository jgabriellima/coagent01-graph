from typing import Callable
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from sample_agent.agents.swarm.builder import AgentBuilder
from pydantic import BaseModel
import os

# Tools
from sample_agent.agents.tce_swarm.tools import (
    etce_search_tool,
    etce_process_details_tool,
    web_search_tool,
    human_in_the_loop
)


class TCESearchAgentState(AgentStateWithStructuredResponse):
    """Estado do Search Agent TCE-PA"""
    # User context
    username: str = ""
    user_id: str = ""
    current_date: str = ""
    
    # Query context
    query: str = ""
    search_type: str = ""  # "expediente", "processo", "web", "mixed"
    
    # eTCE context
    expediente_number: str = ""
    processo_number: str = ""
    year: str = ""
    etce_results: list[dict] = []
    
    # Web search context
    web_query: str = ""
    web_results: list[dict] = []
    
    # Combined results
    search_response: str = ""
    formatted_results: str = ""
    
    # System state
    thread_mode: str = "production"
    task_type: str = "search_processing"
    enable_web_search: bool = True
    enable_etce_search: bool = True
    
    # Agent context
    constraints: list[str] = []
    metadata: dict = {}


class TCESearchAgentOutput(BaseModel):
    """Formato de saída estruturado do Search Agent"""
    query: str
    search_type: str
    expediente_number: str = ""
    processo_number: str = ""
    search_response: str
    sources: list[str] = []
    web_results_count: int = 0
    etce_results_count: int = 0


def build_tce_search_agent(model, handoff_tools: list[Callable] | None = None):
    """Builds the search agent for eTCE API access and web search"""
    
    tools = [
        etce_search_tool,
        etce_process_details_tool,
        web_search_tool,
        human_in_the_loop
    ]
    
    if handoff_tools:
        tools.extend(handoff_tools)
    
    # Resolve prompt paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    prompt_template_path = os.path.join(
        base_dir, "prompts", "base_agent_prompt.jinja2"
    )
    dynamic_block_template_path = os.path.join(
        base_dir, "prompts", "tce_fragments", "search_agent.jinja2"
    )
    
    builder = AgentBuilder(
        name="TCE_Search_Agent",
        model=model,
        tools=tools,
        agent_identity="""Agente especializado em busca e recuperação de informações do eTCE (Processo Eletrônico do TCE-PA) e busca web.
        Expert em navegação do sistema eTCE, formatação de dados processuais e busca contextual na internet.""",
        responsibilities=[
            "Processar consultas sobre expedientes e processos do TCE-PA no sistema eTCE",
            "Realizar buscas estruturadas no Processo Eletrônico do TCE-PA",
            "Formatar informações processuais de forma clara e organizada",
            "Executar buscas web para informações complementares quando necessário",
            "Extrair e apresentar dados específicos de processos e expedientes",
            "Manter contexto temporal dos processos (datas, prazos, exercícios)",
            "Integrar resultados do eTCE com informações complementares da web",
            "Validar números de processo e expediente conforme padrões do TCE-PA"
        ],
        constraints=[
            "Sempre responder em português brasileiro formal e técnico",
            "Validar formato de números de processo (ex: TC/011165/2022)",
            "Não inventar informações não encontradas no eTCE ou web",
            "Manter confidencialidade de processos sigilosos",
            "Sempre especificar a fonte das informações (eTCE ou web)",
            "Solicitar esclarecimentos quando números de processo estão incompletos",
            "Formatar dados processuais seguindo padrões do TCE-PA",
            "Integrar resultados de múltiplas fontes de forma coerente"
        ],
        state_schema=TCESearchAgentState,
        response_format=TCESearchAgentOutput,
        prompt_template_path=prompt_template_path,
        dynamic_block_template_path=dynamic_block_template_path,
    )
    
    return builder.build() 