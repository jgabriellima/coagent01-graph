from typing import Callable
from langgraph.prebuilt.chat_agent_executor import AgentState
from sample_agent.agents.swarm.builder import AgentBuilder
import os

# Tools
from sample_agent.agents.tce_swarm.tools import human_in_the_loop


class TCEMainAgentState(AgentState):
    """Estado do Main Agent TCE-PA"""

    # User context
    username: str = ""
    user_id: str = ""
    current_date: str = ""

    # Current query context
    query: str = ""
    query_type: str = ""  # "legislacao", "expediente", "acordao", "web", "general"

    # Search results
    rag_result: str = ""
    search_result: str = ""
    etce_result: str = ""

    # System state
    thread_mode: str = "production"
    task_type: str = "tce_assistance"
    enable_web_search: bool = True
    enable_etce_search: bool = True
    tce_databases: list[str] = ["atos", "arquivos-tce", "legislacao", "acordaos"]

    # Agent context
    constraints: list[str] = []
    metadata: dict = {}


def build_tce_main_agent(model, handoff_tools: list[Callable] | None = None):
    """Builds the main TCE agent responsible for coordination and conversation management"""

    tools = [human_in_the_loop]

    if handoff_tools:
        tools.extend(handoff_tools)

    # Resolve prompt paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    prompt_template_path = os.path.join(base_dir, "prompts", "base_agent_prompt.jinja2")
    dynamic_block_template_path = os.path.join(
        base_dir, "prompts", "tce_fragments", "main_agent.jinja2"
    )

    builder = AgentBuilder(
        name="TCE_Main_Agent",
        model=model,
        tools=tools,
        agent_identity="""Chatcontas, assistente inteligente especializado do Tribunal de Contas do Estado do Pará (TCE-PA).
        Responsável pela coordenação de tarefas, gerenciamento de conversas e roteamento inteligente para agentes especializados.""",
        responsibilities=[
            "Coordenar e gerenciar o fluxo de conversação com usuários do TCE-PA",
            "Analisar perguntas e determinar qual agente especializado deve ser acionado",
            "Rotear consultas sobre legislação, acordãos e normas para o RAG Agent",
            "Rotear consultas sobre expedientes e processos para o Search Agent",
            "Manter contexto da conversa e estado do usuário",
            "Garantir tom formal e técnico adequado ao ambiente jurídico",
            "Interagir com usuários quando necessário usando a ferramenta human_in_the_loop",
            "Validar e formatar respostas finais antes de apresentar ao usuário",
        ],
        constraints=[
            "Sempre responder em português brasileiro formal",
            "Nunca inventar informações não fornecidas pelas ferramentas",
            "Sempre solicitar esclarecimentos quando a pergunta não estiver clara",
            "Manter confidencialidade de operações internas (não expor nomes de ferramentas)",
            "Seguir rigorosamente o workflow predefinido sem desvios",
            "Cumprimentar usuários pelo nome quando disponível",
            "Restringir respostas ao contexto do TCE-PA e suas competências",
        ],
        state_schema=TCEMainAgentState,
        response_format=None,
        prompt_template_path=prompt_template_path,
        dynamic_block_template_path=dynamic_block_template_path,
    )

    return builder.build()
