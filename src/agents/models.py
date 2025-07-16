from pydantic import BaseModel
from typing import List, Dict, Any, Optional, TypedDict


class EtceProcessoResponse(TypedDict):
    """Structured response for TCE-PA processo queries"""

    numero_processo: Optional[str] = None
    data_autuacao: Optional[str] = None
    unidade_jurisdicionada: Optional[str] = None
    classe_subclasse: Optional[str] = None
    relator: Optional[str] = None
    situacao_atual: Optional[str] = None
    localizacao_atual: Optional[str] = None


class EtceExpedienteResponse(TypedDict):
    """Structured response for TCE-PA expediente queries"""

    numero_expediente: Optional[str] = None
    data_abertura: Optional[str] = None
    tipo_expediente: Optional[str] = None
    unidade_originaria: Optional[str] = None
    assunto: Optional[str] = None
    situacao_atual: Optional[str] = None


class WebSearchResult(BaseModel):
    """Individual web search result"""

    title: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None


class WebSearchResponse(BaseModel):
    """Structured response for web searches"""

    web_results: Optional[List[WebSearchResult]] = None
    overall_summary: Optional[str] = None
    relevance_score: Optional[float] = None
