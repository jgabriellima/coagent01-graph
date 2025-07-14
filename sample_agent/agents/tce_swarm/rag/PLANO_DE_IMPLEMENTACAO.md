# 📋 **Plano de Implementação - PoC RAG Agentico TCE-PA**

## 🎯 **Visão Geral da Estratégia**

### **Objetivo da PoC**
Validar o fluxo completo do pipeline RAG agentico com **comportamento realístico** usando LLM structured output para simular funcionalidades complexas, mantendo a arquitetura modular para facilitar a migração posterior para implementações reais.

### **Filosofia de Implementação**
- **Flow Real**: Pipeline completo funcional com LangGraph
- **Respostas Realísticas**: Mocks gerados por LLM bem instruídas
- **Modularidade**: Substituição simples de mocks por implementações reais
- **Validação Completa**: Comportamento idêntico ao sistema final

---

## 🏗️ **Estrutura de Diretórios**

```
sample_agent/agents/tce_swarm/
├── README.md                    # ✅ Documentação completa
├── PLANO_DE_IMPLEMENTACAO.md    # 📋 Este documento
├── rag/                         # 🆕 Módulo RAG específico
│   ├── __init__.py
│   ├── utils.py                 # 🤖 LLM helper function
│   ├── nodes/                   # 🔄 Nós do pipeline
│   │   ├── __init__.py
│   │   ├── vector_db_setup.py
│   │   ├── query_analysis.py
│   │   ├── chunk_strategy.py
│   │   ├── document_ingestion.py
│   │   ├── document_retrieval.py
│   │   ├── relevance_grading.py
│   │   ├── context_enrichment.py
│   │   ├── reranking.py
│   │   └── response_generation.py
│   ├── processors/              # 📖 Processadores especializados
│   │   ├── __init__.py
│   │   ├── docling_processor.py # (Mock via LLM)
│   │   └── chonkie_processor.py # (Mock via LLM)
│   ├── models/                  # 📊 Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── chunks.py
│   │   ├── documents.py
│   │   └── responses.py
│   └── graph.py                 # 🕸️ Subgrafo RAG
├── main_agent.py                # 🤖 Agente principal
├── rag_agent.py                 # 📚 Agente RAG
├── search_agent.py              # 🔍 Agente de busca
├── tools.py                     # 🛠️ Ferramentas mockadas
├── states.py                    # 📊 Estados consolidados
├── graph.py                     # 🕸️ Grafo principal
└── demo.py                      # 🎮 Demonstração
```

---

## 🤖 **LLM Helper - Core da Estratégia**

### **Função Utilitária Central**

```python
# sample_agent/agents/tce_swarm/rag/utils.py

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
            prompt = PromptTemplate(
                template=base_prompt + "\n\nFORMATO DE SAÍDA:\n{format_instructions}",
                input_variables=[],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )
            
            chain = prompt | model | parser
            response = chain.invoke({})
            
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
```

---

## 📊 **Modelos Pydantic - Structured Output**

### **Modelos para Documentos**

```python
# sample_agent/agents/tce_swarm/rag/models/documents.py

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
```

### **Modelos para Chunks**

```python
# sample_agent/agents/tce_swarm/rag/models/chunks.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChunkResult(BaseModel):
    """Resultado de um chunk individual"""
    content: str = Field(description="Conteúdo do chunk")
    metadata: Dict[str, Any] = Field(description="Metadados associados")
    chunk_id: str = Field(description="ID único")
    
class ChunkingResult(BaseModel):
    """Resultado do processo de chunking"""
    chunks: List[ChunkResult] = Field(description="Lista de chunks gerados")
    strategy_used: str = Field(description="Estratégia utilizada")
    total_chunks: int = Field(description="Número total de chunks")
    processing_time: float = Field(description="Tempo de processamento")

class VectorSearchResult(BaseModel):
    """Resultado da busca no vector database"""
    chunks: List[ChunkResult] = Field(description="Chunks encontrados")
    query: str = Field(description="Query utilizada")
    total_results: int = Field(description="Total de resultados")
    search_time: float = Field(description="Tempo de busca")

class GradedChunk(BaseModel):
    """Chunk com avaliação de relevância"""
    chunk: ChunkResult = Field(description="Chunk original")
    relevance_score: float = Field(description="Score de relevância", ge=0.0, le=1.0)
    confidence: float = Field(description="Confiança na avaliação", ge=0.0, le=1.0)
```

---

## 🔄 **Implementação dos Nós do Pipeline**

### **1. Query Analysis Node**

```python
# sample_agent/agents/tce_swarm/rag/nodes/query_analysis.py

from ..utils import llm
from ..models.state import TCE_RAG_State
from ..models.responses import QueryAnalysisResult

def query_analysis_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Analisa query usando LLM structured output para classificação inteligente
    """
    
    instruction = f"""
    Analise a consulta e classifique conforme padrões de documentos oficiais do tribunal de contas:
    
    Query: "{state.original_query}"
    
    Determine:
    1. Tipo de consulta (legislation, acordao, resolucao, jurisprudencia)
    2. Complexidade (simple, medium, complex)
    3. Contexto temporal necessário
    4. Bases de dados relevantes
    5. Se necessita ingestão de novos documentos
    
    Considere padrões típicos de consultas em documentos oficiais.
    """
    
    analysis = llm(instruction, QueryAnalysisResult, 
                   query=state.original_query, 
                   user_context=state.user_id)
    
    return state.copy(
        processed_query=analysis.processed_query,
        query_type=analysis.query_type,
        query_complexity=analysis.query_complexity,
        target_databases=analysis.target_databases,
        temporal_context=analysis.temporal_context,
        needs_ingestion=analysis.needs_ingestion
    )
```

### **2. Chunk Strategy Selection Node**

```python
# sample_agent/agents/tce_swarm/rag/nodes/chunk_strategy.py

from ..utils import llm
from ..models.state import TCE_RAG_State
from ..models.responses import ChunkStrategyResult

def chunk_strategy_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Seleciona estratégia de chunking via LLM baseada no contexto
    """
    
    instruction = f"""
    Selecione a estratégia de chunking mais adequada para:
    
    Tipo de Consulta: {state.query_type}
    Complexidade: {state.query_complexity}
    Bases de Dados: {state.target_databases}
    
    Estratégias disponíveis:
    - recursive: Estrutura hierárquica preservada
    - semantic: Agrupamento semântico
    - sdpm: Precisão semântica máxima
    - late: Contexto global preservado
    
    Considere características específicas de documentos estruturados.
    """
    
    strategy = llm(instruction, ChunkStrategyResult,
                   query_type=state.query_type,
                   complexity=state.query_complexity,
                   databases=state.target_databases)
    
    return state.copy(
        selected_chunker=strategy.selected_strategy,
        chunk_size=strategy.chunk_size,
        chunk_overlap=strategy.chunk_overlap,
        chunking_metadata=strategy.configuration
    )
```

### **3. Document Ingestion Node**

```python
# sample_agent/agents/tce_swarm/rag/nodes/document_ingestion.py

from ..utils import llm, mock_document_processing, mock_chunking
from ..models.state import TCE_RAG_State
from ..models.responses import IngestionResult

def document_ingestion_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Processa ingestão completa: Docling → Chunking → Vector DB
    """
    
    if not state.needs_ingestion or not state.documents_to_ingest:
        return state
    
    ingestion_results = {}
    
    for doc_info in state.documents_to_ingest:
        # 1. Processamento Docling (Mock)
        parsing_result = mock_document_processing(
            doc_info["file_path"], 
            doc_info.get("type", "expediente")
        )
        
        # 2. Chunking com estratégia selecionada (Mock)
        chunks = mock_chunking(
            parsing_result.raw_markdown,
            state.selected_chunker,
            state.chunking_metadata
        )
        
        # 3. Simulação de storage no vector database
        instruction = f"""
        Simule o armazenamento de chunks no vector database:
        
        Chunks: {len(chunks.chunks)} chunks gerados
        Collection: {state.collection_names}
        User ID: {state.user_id}
        Document Scope: {state.document_scope}
        
        Retorne status de ingestion realístico.
        """
        
        storage_result = llm(instruction, IngestionResult,
                           chunks=chunks.chunks,
                           collection=state.collection_names,
                           user_id=state.user_id)
        
        ingestion_results[doc_info["id"]] = storage_result
    
    return state.copy(
        ingestion_status=ingestion_results,
        needs_ingestion=False,
        user_documents=[doc["id"] for doc in state.documents_to_ingest]
    )
```

### **4. Document Retrieval Node**

```python
# sample_agent/agents/tce_swarm/rag/nodes/document_retrieval.py

from ..utils import llm, mock_vector_search
from ..models.state import TCE_RAG_State
from ..models.responses import RetrievalResult

def document_retrieval_node(state: TCE_RAG_State) -> TCE_RAG_State:
    """
    Executa retrieval híbrido nos chunks já armazenados
    """
    
    # Configurar filtros baseados no escopo
    filters = {
        "document_scope": state.document_scope
    }
    
    if state.document_scope == "user_specific":
        filters["user_id"] = state.user_id
    elif state.document_scope == "session_specific":
        filters["session_id"] = state.session_id
    
    # Busca em múltiplas collections
    all_chunks = []
    
    for collection in state.collection_names:
        # Mock da busca semântica
        semantic_results = mock_vector_search(
            state.processed_query,
            collection,
            {**filters, "search_type": "semantic"}
        )
        
        # Mock da busca por keywords
        keyword_results = mock_vector_search(
            state.processed_query,
            collection,
            {**filters, "search_type": "keyword"}
        )
        
        # Combinar resultados
        instruction = f"""
        Combine resultados de busca semântica e keyword:
        
        Semantic Results: {len(semantic_results.chunks)} chunks
        Keyword Results: {len(keyword_results.chunks)} chunks
        
        Pesos: Semantic 0.7, Keyword 0.3
        
        Retorne top 20 chunks combinados sem duplicatas.
        """
        
        combined = llm(instruction, RetrievalResult,
                      semantic_results=semantic_results.chunks,
                      keyword_results=keyword_results.chunks,
                      query=state.processed_query)
        
        all_chunks.extend(combined.chunks)
    
    # Deduplicação e ranking final
    instruction = f"""
    Deduplique e rankeie {len(all_chunks)} chunks por relevância:
    
    Query: {state.processed_query}
    
    Retorne top 10 chunks únicos ordenados por relevância.
    """
    
    final_result = llm(instruction, RetrievalResult,
                      all_chunks=all_chunks,
                      query=state.processed_query)
    
    return state.copy(
        retrieved_chunks=final_result.chunks,
        retrieval_time=final_result.processing_time,
        vector_db_queries=len(state.collection_names) * 2
    )
```

---

## 🎯 **Estratégia de Migração Mock → Real**

### **1. Substituição Modular**

```python
# Estrutura atual (PoC)
from .utils import llm, mock_document_processing

def document_ingestion_node(state):
    parsing_result = mock_document_processing(file_path, doc_type)
    # ... resto do código

# Estrutura futura (Produção)
from .processors.docling_processor import DoclingProcessor

def document_ingestion_node(state):
    processor = DoclingProcessor()
    parsing_result = processor.process_document(file_path, doc_type)
    # ... resto do código IDÊNTICO
```

### **2. Interface Consistente**

Todos os mocks retornam **exatamente a mesma estrutura** que as implementações reais:

```python
# Mock e Real retornam DoclingProcessingResult
class DoclingProcessingResult(BaseModel):
    success: bool
    raw_markdown: str
    structured_content: TCEStructure
    metadata: Dict[str, Any]
    confidence: float
```

---

## 🧪 **Validação e Testes**

### **1. Testes de Integração**

```python
# test_rag_pipeline.py

def test_full_pipeline():
    """Testa pipeline completo com mocks"""
    
    state = TCE_RAG_State(
        original_query="Qual é o prazo para recurso em processos TCE-PA?",
        user_id="test_user",
        session_id="test_session"
    )
    
    # Executa pipeline completo
    result = tce_rag_subgraph.invoke(state)
    
    # Validações
    assert result.generated_response
    assert result.quality_score > 0.7
    assert len(result.citations) > 0
    assert result.processing_time < 10.0
```

### **2. Testes de Comportamento**

```python
def test_realistic_behavior():
    """Verifica se mocks geram comportamento realístico"""
    
    # Teste com diferentes tipos de documento
    for doc_type in ["legislation", "acordao", "resolucao"]:
        result = mock_document_processing(f"test_{doc_type}.pdf", doc_type)
        
        # Comportamento esperado por tipo
        if doc_type == "legislation":
            assert len(result.structured_content.articles) > 0
        elif doc_type == "acordao":
            assert "ACÓRDÃO" in result.structured_content.header
```

## 🎯 **Vantagens da Abordagem**

### **✅ Benefícios Imediatos**
- **Validação Rápida**: Pipeline completo em dias, não semanas
- **Comportamento Realístico**: LLM gera respostas contextualmente apropriadas
- **Modularidade**: Migração sem refatoração de arquitetura
- **Teste Completo**: Fluxo end-to-end funcionando

### **✅ Benefícios Futuros**
- **Migração Suave**: Substituição gradual componente por componente
- **Risco Reduzido**: Arquitetura validada antes da implementação real
- **Feedback Antecipado**: Usuários podem avaliar comportamento
- **Documentação Viva**: Especificações testadas e funcionais

---

## 🔧 **Comandos de Execução**

### **Setup da PoC**
```bash
# Instalar dependências
uv sync

# Configurar ambiente
export USE_MOCKS=true
export OPENAI_API_KEY=your_key

# Executar testes
python -m pytest sample_agent/agents/tce_swarm/rag/tests/

# Demo completa
python sample_agent/agents/tce_swarm/demo.py --rag-poc
```

### **Migração para Produção**
```bash
# Desabilitar mocks
export USE_MOCKS=false

# Instalar dependências reais
uv add docling chonkie-ai chromadb

# Executar com implementações reais
python sample_agent/agents/tce_swarm/demo.py --production
```

---

## 📋 **Resumo Executivo**

### **Estratégia**
**PoC Inteligente** usando LLM structured output para simular comportamento realístico do pipeline RAG agentico, mantendo arquitetura modular para migração suave.

### **Entregáveis**
1. **Pipeline RAG Completo** com 8 nós funcionais
2. **Respostas Realísticas** via LLM bem instruídas
3. **Arquitetura Modular** para migração gradual
4. **Validação End-to-End** com métricas e observabilidade

### **Timeline**
**11 dias** para PoC completa funcional, pronta para avaliação e feedback.

### **Próximos Passos**
1. **Aprovação** do plano de implementação
2. **Início da Fase 1** - Setup da estrutura base
3. **Implementação iterativa** com validação contínua
4. **Demo e avaliação** com stakeholders

**Status**: 📋 **Plano aprovado - Pronto para implementação** 