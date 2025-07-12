# Chonkie.ai - Advanced Text Chunking for RAG Applications

`by João Gabriel Lima`

## Chunkers Comparison Table

A tabela abaixo detalha as principais diferenças, casos de uso e funcionamento de cada chunker disponível no Chonkie.ai:

| Chunker | Estratégia | Caso de Uso Ideal | Performance | Complexidade | Requer Modelo |
|---------|------------|-------------------|-------------|--------------|---------------|
| **TokenChunker** | Divisão por tokens fixos | APIs com limites de tokens, controle preciso | Muito Alta | Baixa | Tokenizer |
| **SentenceChunker** | Divisão por limites de sentença | Documentos bem estruturados, textos narrativos | Alta | Baixa | Não |
| **RecursiveChunker** | Divisão hierárquica com regras customizáveis | Documentos hierárquicos, papers acadêmicos | Média-Alta | Média | Não |
| **SemanticChunker** | Agrupamento por similaridade semântica | Documentos longos, conteúdo heterogêneo | Média | Alta | Embedding Model |
| **SDPMChunker** | Semantic Double-Pass Merge | Documentos complexos, alta precisão semântica | Média-Baixa | Muito Alta | Embedding Model |
| **LateChunker** | Embedding primeiro, chunk depois | RAG avançado, preservação de contexto | Baixa | Muito Alta | Embedding Model |
| **NeuralChunker** | Chunking baseado em redes neurais | Documentos não estruturados, ML avançado | Baixa | Muito Alta | Neural Model |
| **SlumberChunker** | Chunking otimizado para embeddings | Otimização para embedding models | Média | Alta | Embedding Model |
| **CodeChunker** | Chunking específico para código fonte | Repositórios de código, documentação técnica | Alta | Média | Não |

## 🔍 **Detalhamento das Estratégias**

### **TokenChunker** 🚀
- **Como funciona**: Divide texto em chunks de tamanho fixo baseado em contagem de tokens
- **Vantagem**: Controle preciso para limites de API, processamento muito rápido
- **Ideal para**: OpenAI API, Claude API, modelos com limites rígidos de contexto

### **SentenceChunker** 📝  
- **Como funciona**: Agrupa sentenças em chunks respeitando limites semânticos
- **Vantagem**: Preserva integridade semântica, fácil de implementar
- **Ideal para**: Textos narrativos, documentos educacionais, artigos de blog

### **RecursiveChunker** 🌳
- **Como funciona**: Aplica regras hierárquicas (headers → parágrafos → sentenças)
- **Vantagem**: Respeita estrutura do documento, configurável
- **Ideal para**: Papers acadêmicos, documentação técnica, relatórios estruturados

### **SemanticChunker** 🧠
- **Como funciona**: Usa embeddings para agrupar conteúdo semanticamente similar
- **Vantagem**: Chunks tematicamente coerentes, melhor para recuperação
- **Ideal para**: Documentos longos, conteúdo multi-tópico, knowledge bases

### **LateChunker** ⚡
- **Como funciona**: Processa documento inteiro primeiro, depois chunking com contexto global
- **Vantagem**: Preserva contexto máximo, estado da arte para RAG
- **Ideal para**: RAG de alta qualidade, documentos complexos

### **SDPMChunker** 🔄
- **Como funciona**: Semantic Double-Pass Merge - duas passadas para otimizar semântica
- **Vantagem**: Máxima precisão semântica, reduz perda de contexto
- **Ideal para**: Documentos científicos complexos, análise legal, pesquisa médica

### **NeuralChunker** 🤖
- **Como funciona**: Redes neurais treinadas para identificar pontos ideais de divisão
- **Vantagem**: Aprende padrões complexos, adaptável a diferentes domínios
- **Ideal para**: Textos não estruturados, linguagem natural complexa

### **SlumberChunker** 😴
- **Como funciona**: Chunking otimizado especificamente para modelos de embedding
- **Vantagem**: Maximiza qualidade dos embeddings resultantes
- **Ideal para**: Sistemas de busca semântica, recomendação de conteúdo

### **CodeChunker** 💻
- **Como funciona**: Usa AST (Abstract Syntax Tree) para chunking inteligente de código
- **Vantagem**: Preserva estrutura sintática, respeita funções e classes
- **Ideal para**: Documentação de código, análise de repositórios, AI coding assistants

## ⚖️ **Guia de Seleção Rápida**

| Prioridade | Escolha | Justificativa |
|------------|---------|---------------|
| **Velocidade** | TokenChunker → SentenceChunker → CodeChunker | Performance máxima |
| **Qualidade RAG** | LateChunker → SDPMChunker → SemanticChunker | Contexto preservado |
| **Simplicidade** | SentenceChunker → TokenChunker → RecursiveChunker | Fácil implementação |
| **Flexibilidade** | RecursiveChunker → SemanticChunker → NeuralChunker | Configurabilidade |

## Installation

```bash
# Installation - Base package
uv add chonkie

# Installation - Full features
uv add "chonkie[all]"

# Additional dependencies for comprehensive testing
uv add tiktoken sentence-transformers transformers torch numpy pandas matplotlib seaborn
```

## Example Usage

```python
# Basic TokenChunker example
from chonkie import TokenChunker

chunker = TokenChunker(chunk_size=512)
chunks = chunker("Your text here...")

for chunk in chunks:
    print(f"Chunk: {chunk.text}")
    print(f"Tokens: {chunk.token_count}")
```

```python
# SentenceChunker example
from chonkie import SentenceChunker

chunker = SentenceChunker(sentences_per_chunk=3)
chunks = chunker("Your text here...")

for chunk in chunks:
    print(f"Chunk: {chunk.text}")
```

```python
# RecursiveChunker example
from chonkie import RecursiveChunker

chunker = RecursiveChunker(chunk_size=1024)
chunks = chunker("Your text here...")

for chunk in chunks:
    print(f"Chunk: {chunk.text}")
```

## References

- **Official Website**: [chonkie.ai](https://chonkie.ai)
- **Documentation**: [docs.chonkie.ai](https://docs.chonkie.ai)
- **GitHub Repository**: [github.com/chonkie-ai/chonkie](https://github.com/chonkie-ai/chonkie)
- **PyPI Package**: [pypi.org/project/chonkie](https://pypi.org/project/chonkie)

---

**Created by:** João Gabriel Lima  
**Date:** January 2025  
**🦛 Ready to CHONK!** ✨ 