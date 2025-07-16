from typing import Callable
from src.agents.builder import AgentBuilder
import os

# Tools
from src.agents.tools import human_in_the_loop


def build_main_agent(
    model,
    handoff_tools: list[Callable] | None = None,
    additional_pre_hooks: list | None = None,
):
    """
    Builds the main agent responsible for initial coordination and routing

    Args:
        model: LLM model instance
        handoff_tools: List of handoff tools for agent coordination
        additional_pre_hooks: List of RunnableLambda hooks for pre-processing
    """

    tools = [human_in_the_loop]

    if handoff_tools:
        tools.extend(handoff_tools)

    # Resolve prompt paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    prompt_template_path = os.path.join(base_dir, "src", "prompts", "base_agent_prompt.jinja2")
    dynamic_block_template_path = os.path.join(
        base_dir, "src", "prompts", "tce_fragments", "main_agent.jinja2"
    )

    builder = AgentBuilder(
        name="Main_Agent",
        model=model,
        tools=tools,
        agent_identity="""Chatcontas, assistente inteligente especializado do Tribunal de Contas.
        Responsável pela coordenação, roteamento inteligente e resposta direta a consultas gerais.""",
        responsibilities=[
            "Responder diretamente a consultas gerais sobre o Tribunal de Contas",
            "Analisar perguntas e determinar se agente especializado deve ser acionado",
            "Rotear consultas sobre legislação, acordãos e normas para o RAG Agent (opcional)",
            "Rotear consultas sobre expedientes e processos para o Search Agent (opcional)",
            "Manter contexto da conversa e estado do usuário",
            "Garantir tom formal e técnico adequado ao ambiente",
            "Interagir com usuários quando necessário usando a ferramenta human_in_the_loop",
            "Coordenar fluxos complexos que requerem múltiplos agentes",
            "Fornecer informações institucionais básicas sem necessidade de handoff",
        ],
        constraints=[
            "Sempre responder em português brasileiro formal",
            "Nunca inventar informações não fornecidas pelas ferramentas",
            "Sempre solicitar esclarecimentos quando a pergunta não estiver clara",
            "Manter confidencialidade de operações internas (não expor nomes de ferramentas)",
            "Seguir rigorosamente o workflow predefinido sem desvios",
            "Cumprimentar usuários pelo nome quando disponível",
            "Restringir respostas ao contexto institucional e suas competências",
            "IMPORTANTE: Não responder perguntas que não sejam relacionadas ao Tribunal de Contas do Estado do Pará",
            "Usar handoffs apenas quando necessário - pode responder diretamente ao usuário",
        ],
        response_format=None,  # Main Agent entrega state completo
        prompt_template_path=prompt_template_path,
        dynamic_block_template_path=dynamic_block_template_path,
        additional_pre_hooks=additional_pre_hooks,
    )

    return builder.build()
