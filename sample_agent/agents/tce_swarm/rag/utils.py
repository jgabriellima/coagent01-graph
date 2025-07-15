"""
LLM Helper Functions for TCE-PA RAG Pipeline
Core utility functions for simulating complex functionalities via LLM structured output
"""

from typing import Optional, Any, Dict, List, Union, TypeVar, Type
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
import json
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

def llm(instruction: str, output_model: Optional[Type[T]] = None, **kwargs) -> Optional[T]:
    """
    Função auxiliar para simular funcionalidades complexas via LLM structured output.

    Args:
        instruction: Instrução detalhada para a LLM
        output_model: Modelo Pydantic para structured output (opcional)
        **kwargs: Parâmetros adicionais para contexto

    Returns:
        Resposta estruturada conforme output_model ou None
    """

    # Configuração da LLM
    # model_name = "groq:llama-3.1-8b-instant"
    model_name = "openai:gpt-4o-mini"
    model = init_chat_model(model_name, temperature=0)
    if output_model:
        model = model.with_structured_output(output_model)
    # Contexto adicional
    context_str = ""
    if kwargs:
        context_str = f"\n\nContexto Adicional:\n{json.dumps(kwargs, indent=2, ensure_ascii=False, default=str)}"

    if "groq" in model_name:
        context_str += f"\n\nDados do modelo: ```{output_model.model_json_schema()}```"
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

    # try:
    #     if output_model:
    #         # Structured output com Pydantic
    #         parser = PydanticOutputParser(pydantic_object=output_model)
    #         full_prompt = (
    #             base_prompt
    #             + f"\n\nFORMATO DE SAÍDA:\n{parser.get_format_instructions()}"
    #         )

    #         chain = model | parser
    #         response = chain.invoke(full_prompt)

    #         logger.info(f"LLM Mock Response: {type(response).__name__}")
    #         return response
    #     else:
    #         # Resposta em texto simples
    #         response = model.invoke(base_prompt)
    #         logger.info(f"LLM Mock Response: {len(response.content)} chars")
    #         return response.content

    # except Exception as e:
    #     logger.error(f"LLM Mock Error: {str(e)}")
    #     # Fallback para dados default
    #     if output_model:
    #         return output_model()
    #     else:
    #         return f"Mock response for: {instruction[:50]}..."

    if output_model:
        response: T = model.invoke(base_prompt)
        return response
    else:
        response = model.invoke(base_prompt)
        return response.content if hasattr(response, 'content') else str(response)

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

    return llm(
        instruction, DoclingProcessingResult, file_path=file_path, doc_type=doc_type
    )


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

    return llm(
        instruction, ChunkingResult, content=content, strategy=strategy, config=config
    )


# Função para simular vector database
def mock_vector_search(
    query: str, collection: str, filters: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Simula busca no vector database via LLM"""

    instruction = f"""
    Simule busca semântica em vector database especializado em documentos oficiais.
    
    Query: {query}
    Collection: {collection}
    Filtros: {filters}
    
    Retorne chunks relevantes com scores realísticos.
    """

    from .models.chunks import VectorSearchResult

    return llm(
        instruction,
        VectorSearchResult,
        query=query,
        collection=collection,
        filters=filters,
    )
