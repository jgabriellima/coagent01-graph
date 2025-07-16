"""
Document Models for RAG Pipeline
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

class DocumentMetadata(BaseModel):
    """Metadados genéricos de documento extensíveis"""
    document_type: str = Field(description="Tipo de documento")
    document_number: str = Field(description="Número do documento")
    year: str = Field(description="Ano do documento")
    created_date: Optional[datetime] = Field(description="Data de criação")
    last_updated: Optional[datetime] = Field(description="Última atualização")
    
    # Metadados extensíveis para diferentes tipos de documento
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Campos customizados por tipo de documento")
    
class DocumentInfo(BaseModel):
    """Informações completas do documento"""
    doc_id: str = Field(description="ID único do documento")
    file_path: str = Field(description="Caminho do arquivo")
    content: str = Field(description="Conteúdo do documento")
    structure: DocumentStructure = Field(description="Estrutura hierárquica")
    metadata: DocumentMetadata = Field(description="Metadados do documento")
    processing_info: DoclingProcessingResult = Field(description="Resultado do processamento")
    ingestion_timestamp: datetime = Field(description="Timestamp da ingestão")
    user_id: str = Field(description="ID do usuário")
    session_id: str = Field(description="ID da sessão")
    access_level: str = Field(description="Nível de acesso", default="public") 