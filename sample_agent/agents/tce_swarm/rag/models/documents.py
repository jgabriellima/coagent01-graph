"""
Document Models for TCE-PA RAG Pipeline
Pydantic models for document processing and structure
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class DocumentStructure(BaseModel):
    """Estrutura hierárquica detectada no documento"""
    header: str = Field(description="Cabeçalho principal")
    sections: List[Dict[str, Any]] = Field(description="Seções hierárquicas")
    articles: List[Dict[str, Any]] = Field(description="Artigos numerados")
    annexes: List[str] = Field(description="Anexos identificados")
    signatures: List[str] = Field(description="Assinaturas finais")

class DoclingProcessingResult(BaseModel):
    """Resultado do processamento Docling"""
    success: bool = Field(description="Status do processamento")
    method: str = Field(description="Método utilizado")
    raw_markdown: str = Field(description="Conteúdo markdown extraído")
    structured_content: DocumentStructure = Field(description="Estrutura hierárquica detectada")
    metadata: Dict[str, Any] = Field(description="Metadados enriquecidos")
    confidence: float = Field(description="Score de confiança", ge=0.0, le=1.0)
    processing_time: float = Field(description="Tempo de processamento")
    tables: List[Dict[str, Any]] = Field(description="Tabelas extraídas")

class TCEDocumentMetadata(BaseModel):
    """Metadados específicos TCE-PA"""
    document_type: str = Field(description="Tipo de documento")
    document_number: str = Field(description="Número do documento")
    year: str = Field(description="Ano do documento")
    exercise: str = Field(description="Exercício fiscal")
    validity_period: Optional[str] = Field(description="Período de vigência")
    jurisdiction: str = Field(description="Jurisdição")
    rapporteur: Optional[str] = Field(description="Relator")
    created_date: Optional[datetime] = Field(description="Data de criação")
    last_updated: Optional[datetime] = Field(description="Última atualização")
    
class TCEDocumentInfo(BaseModel):
    """Informações completas do documento TCE-PA"""
    doc_id: str = Field(description="ID único do documento")
    file_path: str = Field(description="Caminho do arquivo")
    content: str = Field(description="Conteúdo do documento")
    structure: DocumentStructure = Field(description="Estrutura hierárquica")
    metadata: TCEDocumentMetadata = Field(description="Metadados TCE-PA")
    processing_info: DoclingProcessingResult = Field(description="Resultado do processamento")
    ingestion_timestamp: datetime = Field(description="Timestamp da ingestão")
    user_id: str = Field(description="ID do usuário")
    session_id: str = Field(description="ID da sessão")
    access_level: str = Field(description="Nível de acesso", default="public") 