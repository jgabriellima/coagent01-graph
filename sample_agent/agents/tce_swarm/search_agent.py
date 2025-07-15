from typing import Callable
from sample_agent.agents.swarm.builder import AgentBuilder
from sample_agent.agents.tce_swarm.states import SearchAgentState
import os

# Tools
from sample_agent.agents.tce_swarm.tools import (
    etce_processos_info_tool,
    etce_expedientes_info_tool,
    web_search_tool,
    human_in_the_loop,
)


def build_search_agent(model, handoff_tools: list[Callable] | None = None):
    """
    Builds the search agent for system API access and web search with direct user response capability
    """

    tools = [
        etce_processos_info_tool,
        etce_expedientes_info_tool,
        web_search_tool,
        human_in_the_loop,
    ]

    if handoff_tools:
        tools.extend(handoff_tools)

    # Resolve prompt paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    prompt_template_path = os.path.join(base_dir, "prompts", "base_agent_prompt.jinja2")
    dynamic_block_template_path = os.path.join(
        base_dir, "prompts", "tce_fragments", "search_agent.jinja2"
    )

    builder = AgentBuilder(
        name="Search_Agent",
        model=model,
        tools=tools,
        agent_identity=(
            "Agente especializado em busca e recuperação de informações processuais no sistema eletrônico e na web, "
            "respondendo diretamente ao usuário com precisão e clareza."
        ),
        responsibilities=[
            "Responder diretamente ao usuário sobre consultas de expedientes/processos",
            "Executar buscas estruturadas no sistema eletrônico e web",
            "Extrair, formatar e apresentar dados processuais com contexto temporal",
            "Integrar múltiplas fontes de informação de forma coerente",
            "Validar números de processo/expediente conforme padrões institucionais",
            "Fazer handoff para RAG Agent (legislação/acórdãos) ou Main Agent (coordenação complexa) quando necessário",
        ],
        constraints=[
            "Responder em português brasileiro formal/técnico especificando fonte das informações",
            "Validar formato de números de processo (ex: TC/011165/2022) e solicitar esclarecimentos se incompletos",
            "Não inventar informações; manter confidencialidade de processos sigilosos",
            "Formatar dados conforme padrões institucionais integrando múltiplas fontes",
            "Responder diretamente ao usuário; usar handoffs apenas quando necessário",
        ],
        state_schema=SearchAgentState,
        prompt_template_path=prompt_template_path,
        dynamic_block_template_path=dynamic_block_template_path,
    )

    return builder.build()
