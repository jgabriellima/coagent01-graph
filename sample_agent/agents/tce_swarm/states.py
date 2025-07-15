"""
Consolidated state definitions for the swarm architecture.
This module defines the combined state schema that all agents share.
"""

from langgraph_swarm import SwarmState
from langgraph.prebuilt.chat_agent_executor import AgentState
from typing import List, Optional, TypedDict
from pydantic import Field

from .models import EtceProcessoResponse, EtceExpedienteResponse, WebSearchResponse


class SearchAgentState(AgentState):
    """
    Search Agent state schema for system and web search.

    Composição dos response models das tools do Search Agent:
    - TCE-PA processo/expediente lookups
    - Web search results

    Campos opcionais com estado inicial nulo - apenas sensibilizados quando tools executadas.
    """

    query: str = Field(default="", description="Consulta sendo processada")
    etce_processo_response: Optional[EtceProcessoResponse] = Field(
        default=None, description="Resposta de consulta de processo TCE-PA"
    )
    etce_expediente_response: Optional[EtceExpedienteResponse] = Field(
        default=None, description="Resposta de consulta de expediente TCE-PA"
    )
    web_search_response: Optional[WebSearchResponse] = Field(
        default=None, description="Resposta de busca web"
    )


class ChatContasStateOutput:
    query: str = Field(default="", description="[INPUT] Consulta sendo processada")
    etce_expediente_response: Optional[EtceExpedienteResponse] = Field(
        default=None, description="Resposta de consulta de expediente TCE-PA"
    )
    messages: List[str] = Field(
        default_factory=list, description="Mensagens da conversa"
    )


class ChatContasInputState(SwarmState):
    """
    Input state schema for the chat contas agent.
    """

    enable_web_search: bool = Field(default=True, description="Habilita busca web")
    enable_system_search: bool = Field(
        default=True, description="Habilita busca no sistema eletrônico"
    )
    enable_rag_processing: bool = Field(
        default=True, description="Habilita processamento RAG"
    )
