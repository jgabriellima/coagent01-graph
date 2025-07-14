"""
LLM Helper Functions for TCE-PA RAG Pipeline
Core utility functions for simulating complex functionalities via LLM structured output
"""

from typing import Optional, Any, Dict, List, Union
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
import json
import logging

logger = logging.getLogger(__name__)

def llm(instruction: str, output_model: Optional[BaseModel] = None, **kwargs) -> Any:
    """
    Função auxiliar para simular funcionalidades complexas via LLM structured output.
    
    Args:
        instruction: Instrução detalhada para a LLM
        output_model: Modelo Pydantic para structured output (opcional)
        **kwargs: Parâmetros adicionais para contexto
    
    Returns:
        Resposta estruturada conforme output_model ou texto simples
    """
    
    # Configuração da LLM
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.1,
        max_tokens=2000
    )
    
    # Contexto adicional
    context_str = ""
    if kwargs:
        context_str = f"\n\nContexto Adicional:\n{json.dumps(kwargs, indent=2, ensure_ascii=False)}"
    
    # Prompt base
    base_prompt = f"""
Sintetize dados estruturados conforme especificado.

INSTRUÇÃO ESPECÍFICA:
{instruction}

DIRETRIZES:
- Gere dados realísticos e consistentes
- Mantenha estrutura conforme solicitado
- Use terminologia técnica apropriada
- Considere cenários variados
- Foque na qualidade da síntese

{context_str}
"""
    
    try:
        if output_model:
            # Structured output com Pydantic
            parser = PydanticOutputParser(pydantic_object=output_model)
            full_prompt = base_prompt + f"\n\nFORMATO DE SAÍDA:\n{parser.get_format_instructions()}"
            
            chain = model | parser
            response = chain.invoke(full_prompt)
            
            logger.info(f"LLM Mock Response: {type(response).__name__}")
            return response
        else:
            # Resposta em texto simples
            response = model.invoke(base_prompt)
            logger.info(f"LLM Mock Response: {len(response.content)} chars")
            return response.content
            
    except Exception as e:
        logger.error(f"LLM Mock Error: {str(e)}")
        # Fallback para dados default
        if output_model:
            return output_model()
        else:
            return f"Mock response for: {instruction[:50]}..."

# Função específica para simular processamento de documentos
def mock_document_processing(file_path: str, doc_type: str) -> Dict[str, Any]:
    """Simula processamento Docling via LLM"""
    
    instruction = f"""
    Simule o processamento de um documento oficial usando parser estruturado.
    
    Documento: {file_path}
    Tipo: {doc_type}
    
    Retorne dados realísticos incluindo:
    - Conteúdo markdown extraído
    - Estrutura hierárquica detectada
    - Metadados do documento
    - Score de qualidade
    """
    
    from .models.documents import DoclingProcessingResult
    
    return llm(instruction, DoclingProcessingResult, 
               file_path=file_path, doc_type=doc_type)

# Função para simular chunking
def mock_chunking(content: str, strategy: str, config: Dict[str, Any]) -> List[str]:
    """Simula chunking Chonkie via LLM"""
    
    instruction = f"""
    Simule o chunking de conteúdo estruturado usando estratégia {strategy}.
    
    Conteúdo: {content[:200]}...
    Estratégia: {strategy}
    Configuração: {config}
    
    Retorne lista de chunks realísticos mantendo estrutura hierárquica.
    """
    
    from .models.chunks import ChunkingResult
    
    return llm(instruction, ChunkingResult, 
               content=content, strategy=strategy, config=config)

# Função para simular vector database
def mock_vector_search(query: str, collection: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Simula busca no vector database via LLM"""
    
    instruction = f"""
    Simule busca semântica em vector database especializado em documentos oficiais.
    
    Query: {query}
    Collection: {collection}
    Filtros: {filters}
    
    Retorne chunks relevantes com scores realísticos.
    """
    
    from .models.chunks import VectorSearchResult
    
    return llm(instruction, VectorSearchResult, 
               query=query, collection=collection, filters=filters) 