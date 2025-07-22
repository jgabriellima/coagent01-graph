# Correção de Anti-Padrões: Eliminação de Dict[str, Any] e default_factory=dict

## Problema Identificado

O uso de `Dict[str, Any]` e `default_factory=dict` quebra princípios fundamentais:

- **Schema Validation**: LLMs com structured output rejeitam dicionários genéricos
- **Type Safety**: Quebra tipagem forte do Pydantic
- **Maintainability**: Impossível documentar estrutura indefinida
- **Validation**: Não há como validar dados em dicts genéricos

## Correções Necessárias

### 1. DocumentMetadata - Campos Customizados Estruturados

**ANTES (Anti-padrão):**
```python
class DocumentMetadata(BaseModel):
    document_type: str
    # PROBLEMA: Dict genérico sem estrutura
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
```

**DEPOIS (Estruturado):**
```python
class LegislationMetadata(BaseModel):
    """Metadados específicos para legislação"""
    lei_numero: str = Field(description="Número da lei")
    data_publicacao: date = Field(description="Data de publicação")
    orgao_emissor: str = Field(description="Órgão emissor")
    vigencia_inicio: date = Field(description="Início da vigência")
    vigencia_fim: Optional[date] = Field(description="Fim da vigência")

class AcordaoMetadata(BaseModel):
    """Metadados específicos para acordãos"""
    numero_acordao: str = Field(description="Número do acordão")
    relator: str = Field(description="Conselheiro relator")
    data_julgamento: date = Field(description="Data do julgamento")
    processo_origem: str = Field(description="Processo de origem")
    ementa: str = Field(description="Ementa do acordão")

class ExpedienteMetadata(BaseModel):
    """Metadados específicos para expedientes"""
    numero_expediente: str = Field(description="Número do expediente")
    unidade_originaria: str = Field(description="Unidade originária")
    assunto: str = Field(description="Assunto do expediente")
    situacao: str = Field(description="Situação atual")

class DocumentMetadata(BaseModel):
    """Metadados estruturados por tipo"""
    document_type: Literal["legislacao", "acordao", "expediente"]
    document_number: str
    year: str
    created_date: Optional[datetime]
    last_updated: Optional[datetime]
    
    # Campos estruturados por tipo
    legislacao: Optional[LegislationMetadata] = None
    acordao: Optional[AcordaoMetadata] = None
    expediente: Optional[ExpedienteMetadata] = None
```

### 2. ChunkingMetadata - Estrutura por Estratégia

**ANTES (Anti-padrão):**
```python
class ChunkStrategyResult(BaseModel):
    chunking_metadata: Dict[str, Any] = Field(description="Metadados do chunking")
```

**DEPOIS (Estruturado):**
```python
class RecursiveChunkingMetadata(BaseModel):
    """Metadados específicos para chunking recursivo"""
    separators_used: List[str] = Field(description="Separadores utilizados")
    hierarchy_depth: int = Field(description="Profundidade da hierarquia")
    chunk_boundaries: List[str] = Field(description="Delimitadores encontrados")

class SemanticChunkingMetadata(BaseModel):
    """Metadados específicos para chunking semântico"""
    similarity_threshold: float = Field(description="Threshold de similaridade")
    embedding_model: str = Field(description="Modelo de embedding usado")
    cluster_count: int = Field(description="Número de clusters formados")

class SdpmChunkingMetadata(BaseModel):
    """Metadados específicos para SDPM chunking"""
    sentence_count: int = Field(description="Número de sentenças")
    paragraph_boundaries: List[int] = Field(description="Limites dos parágrafos")
    discourse_markers: List[str] = Field(description="Marcadores discursivos")

class ChunkingMetadata(BaseModel):
    """Metadados estruturados por estratégia"""
    strategy: Literal["recursive", "semantic", "sdpm", "late"]
    chunk_count: int = Field(description="Total de chunks gerados")
    processing_time: float = Field(description="Tempo de processamento")
    
    # Metadados específicos por estratégia
    recursive: Optional[RecursiveChunkingMetadata] = None
    semantic: Optional[SemanticChunkingMetadata] = None
    sdpm: Optional[SdpmChunkingMetadata] = None

class ChunkStrategyResult(BaseModel):
    selected_chunker: Literal["recursive", "semantic", "sdpm", "late"]
    chunk_size: int
    chunk_overlap: int
    chunking_metadata: ChunkingMetadata  # ESTRUTURADO
    strategy_rationale: str
```

### 3. TableData - Estrutura Definida para Tabelas

**ANTES (Anti-padrão):**
```python
class DocumentProcessingResult(BaseModel):
    tables: List[Dict[str, Any]] = Field(description="Tabelas extraídas")
```

**DEPOIS (Estruturado):**
```python
class TableCell(BaseModel):
    """Célula individual da tabela"""
    value: str = Field(description="Valor da célula")
    row: int = Field(description="Linha da célula")
    col: int = Field(description="Coluna da célula")
    colspan: int = Field(default=1, description="Expansão de colunas")
    rowspan: int = Field(default=1, description="Expansão de linhas")

class TableData(BaseModel):
    """Estrutura definida para tabelas extraídas"""
    table_id: str = Field(description="ID único da tabela")
    caption: Optional[str] = Field(description="Legenda da tabela")
    headers: List[str] = Field(description="Cabeçalhos das colunas")
    rows: List[List[str]] = Field(description="Dados das linhas")
    cells: List[TableCell] = Field(description="Células com metadados")
    row_count: int = Field(description="Número total de linhas")
    col_count: int = Field(description="Número total de colunas")

class DocumentProcessingResult(BaseModel):
    success: bool
    method: str
    raw_markdown: str
    structured_content: DocumentStructure
    metadata: DocumentMetadata  # JÁ ESTRUTURADO
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time: float
    tables: List[TableData]  # ESTRUTURADO
```

### 4. EvaluationResults - Estrutura para Avaliações

**ANTES (Anti-padrão):**
```python
def evaluate(self, example: Dict[str, Any]) -> Dict[str, Any]:
```

**DEPOIS (Estruturado):**
```python
class EvaluationInput(BaseModel):
    """Input estruturado para avaliação"""
    query: str = Field(description="Query do usuário")
    expected_output: str = Field(description="Resposta esperada")
    actual_output: str = Field(description="Resposta gerada")
    context: Optional[List[str]] = Field(description="Contexto utilizado")

class EvaluationMetadata(BaseModel):
    """Metadados específicos da avaliação - zero dicionários"""
    evaluator_version: Optional[str] = Field(description="Versão do avaliador")
    model_used: Optional[str] = Field(description="Modelo LLM utilizado")
    processing_time: Optional[float] = Field(description="Tempo de processamento")
    confidence_level: Optional[float] = Field(description="Nível de confiança")
    
class EvaluationResult(BaseModel):
    """Resultado estruturado da avaliação"""
    score: float = Field(description="Score da avaliação", ge=0.0, le=1.0)
    reason: str = Field(description="Justificativa do score")
    category: str = Field(description="Categoria da avaliação")
    timestamp: datetime = Field(description="Timestamp da avaliação")
    metadata: Optional[EvaluationMetadata] = Field(description="Metadados estruturados")

def evaluate(self, example: EvaluationInput) -> EvaluationResult:
```

### 5. HTML Changes - Union Types por Tipo de Mudança

**ANTES (Anti-padrão):**
```python
class HtmlChange(BaseModel):
    change_type: Literal["style", "content", "visibility"]
    old_value: Optional[str] = None  # ❌ Genérico demais
    new_value: str                   # ❌ Tipo inadequado para visibility
```

**DEPOIS (Union Types Estruturados):**
```python
class StyleChange(BaseModel):
    """Mudança específica de CSS/estilo"""
    change_type: Literal["style"] = "style"
    css_property: str = Field(description="Propriedade CSS modificada")
    old_value: Optional[str] = Field(description="Valor CSS anterior")
    new_value: str = Field(description="Novo valor CSS")
    
class ContentChange(BaseModel):
    """Mudança específica de conteúdo"""
    change_type: Literal["content"] = "content"
    content_type: Literal["text", "html", "markdown"] = Field(description="Tipo de conteúdo")
    old_value: Optional[str] = Field(description="Conteúdo anterior")
    new_value: str = Field(description="Novo conteúdo")
    preserve_children: bool = Field(default=True, description="Preservar elementos filhos")

class VisibilityChange(BaseModel):
    """Mudança específica de visibilidade"""
    change_type: Literal["visibility"] = "visibility"
    visibility_method: Literal["display", "visibility", "opacity"] = Field(description="Método de controle")
    old_visible: Optional[bool] = Field(description="Estado anterior")
    new_visible: bool = Field(description="Novo estado de visibilidade")
    
# Union type para mudanças específicas
HtmlChangeUnion = Union[StyleChange, ContentChange, VisibilityChange]

class HtmlChange(BaseModel):
    """Container para mudanças HTML com discriminated union"""
    change_id: str = Field(description="ID único da mudança")
    element_id: str = Field(description="ID do elemento modificado")
    timestamp: str = Field(description="Timestamp da mudança")
    
    # Union type baseado em change_type
    change_data: HtmlChangeUnion = Field(discriminator='change_type')

class HtmlElementModification(BaseModel):
    """Lista de elementos modificados estruturada"""
    modified_elements: List[HtmlChange] = Field(description="Elementos modificados")
    total_changes: int = Field(description="Total de mudanças aplicadas")
    success_count: int = Field(description="Mudanças aplicadas com sucesso")
    failure_count: int = Field(description="Mudanças que falharam")
    rollback_available: bool = Field(description="Possibilidade de rollback")
```

## Implementação das Correções

### Arquivos a Modificar:

1. **src/agents/rag/models/documents.py**
   - Substituir `custom_fields: Dict[str, Any]` por campos estruturados
   - Criar modelos específicos por tipo de documento

2. **src/agents/rag/models/responses.py**
   - Substituir `chunking_metadata: Dict[str, Any]` por estrutura tipada
   - Criar metadados específicos por estratégia de chunking

3. **src/evaluations/evaluators/base.py**
   - Substituir `Dict[str, Any]` por modelos Pydantic estruturados
   - Criar contratos de input/output para avaliadores

4. **src/evaluations/datasets/generator/synthesizer/base.py**
   - Estruturar todos os metadados de trace e workflow
   - Eliminar `Dict[str, Any]` em favor de modelos específicos

5. **docs/fincoder-multi-agent.md** 
   - Substituir HtmlChange genérico por Union types estruturados
   - Implementar discriminated unions para change_type

## Princípio: ZERO Dicionários Genéricos

**REGRA ABSOLUTA**: Eliminação completa de `Dict[K, V]` em qualquer formato:
- ❌ `Dict[str, Any]` - Tipo genérico sem validação
- ❌ `Dict[str, str]` - Ainda é genérico, não documenta estrutura
- ❌ `dict` - Type hint implícito sem validação
- ❌ `default_factory=dict` - Cria dicionários vazios problemáticos

**SOLUÇÃO**: Sempre usar modelos Pydantic estruturados:
```python
# ERRADO
metadata: Dict[str, str] = Field(description="Metadados")

# CORRETO  
class SpecificMetadata(BaseModel):
    evaluator_version: str = Field(description="Versão")
    model_used: str = Field(description="Modelo")
    
metadata: SpecificMetadata = Field(description="Metadados estruturados")
```

## Benefícios da Refatoração

- **Schema Validation**: LLMs com structured output funcionarão corretamente
- **Type Safety**: Tipagem forte mantida em todo o sistema
- **Documentation**: Estrutura autodocumentada via Pydantic
- **Validation**: Validação automática de todos os campos
- **Maintainability**: Código mais legível e menos propenso a erros
- **IDE Support**: Autocomplete e detecção de erros melhoradas
- **Zero Ambiguity**: Estrutura sempre conhecida e validável
- **Discriminated Unions**: Type safety baseada em discriminator fields

## Vantagens dos Union Types Discriminados

### Exemplo: HtmlChange com Discriminated Union

**Problema Resolvido:**
- Cada `change_type` requer estrutura de dados completamente diferente
- `str` genérico inadequado para visibility (deveria ser boolean)
- Impossível validar CSS vs HTML vs visibility state

**Solução Implementada:**
```python
# Pydantic automaticamente seleciona o tipo correto baseado em change_type
change_data: HtmlChangeUnion = Field(discriminator='change_type')

# Exemplos de uso:
StyleChange(change_type="style", css_property="color", new_value="#FF0000")
ContentChange(change_type="content", content_type="html", new_value="<h1>Title</h1>") 
VisibilityChange(change_type="visibility", new_visible=False)
```

**Benefícios Técnicos:**
- **Automatic Type Selection**: Pydantic seleciona automaticamente o modelo correto
- **Field Validation**: Cada tipo valida apenas campos apropriados 
- **IDE Autocomplete**: Type hints corretos baseados no discriminator
- **LLM Compatibility**: Structured output com esquemas bem definidos
- **Runtime Safety**: Impossível misturar tipos incorretos
- **Self-Documenting**: Estrutura clara para cada caso de uso 