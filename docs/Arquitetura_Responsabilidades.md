# **Arquitetura de Responsabilidades - ChatContas Multi-Agent**

[[memory:3332709]]

Este documento define a **divisão precisa de responsabilidades** entre os agentes do sistema ChatContas para otimizar eficiência e eliminar sobreposições no fluxo de handoff.

---

## **🎯 Princípios Arquiteturais**

### **Autonomia de Resposta**
- **Qualquer agente pode responder diretamente ao usuário**  
- Handoffs são **opcionais** e baseados em necessidades específicas  
- **Não há consolidação obrigatória** através do Main Agent  
- Cada agente é **autônomo e especializado**  

### **Critérios de Handoff**
- **Expertise específica**: Quando outro agente possui ferramentas/conhecimento mais adequado  
- **Fluxo complexo**: Quando múltiplos agentes precisam colaborar sequencialmente  
- **Contexto inadequado**: Quando a consulta está fora do escopo do agente atual  

---

## **🤖 Main Agent - Coordenador Institucional**

### **Responsabilidades Primárias**
- **Informações institucionais básicas**: História, estrutura, competências do TCE-PA  
- **Navegação do sistema**: Explicar capacidades, orientar sobre tipos de consulta  
- **Coordenação de fluxos complexos**: Quando múltiplos agentes precisam colaborar  
- **Triagem inicial**: Analisar consultas ambíguas e rotear adequadamente  
- **Interação humana**: Escalações via `human_in_the_loop` para casos críticos  

### **Quando Responde Diretamente**
```
✅ "Como funciona o TCE-PA?"
✅ "Quais são as competências do tribunal?"
✅ "Como posso consultar um processo?"
✅ "Qual a diferença entre expediente e processo?"
✅ "Quem são os conselheiros atualmente?"
```

### **Quando Faz Handoff**
```
📄 RAG Agent → Consultas sobre documentos oficiais, legislação, acordãos
🔍 Search Agent → Consultas específicas sobre expedientes/processos, busca web
```

### **Ferramentas Disponíveis**
- `human_in_the_loop`: Escalação para operadores humanos  
- `handoff_to_rag_agent`: Documentos oficiais e normativas  
- `handoff_to_search_agent`: Expedientes e buscas específicas  

---

## **📚 RAG Agent - Especialista Documental**

### **Responsabilidades Primárias**
- **Processamento completo de documentos oficiais** via pipeline RAG  
- **Legislação e normativas**: Leis, decretos, resoluções, atos normativos  
- **Jurisprudência**: Acordãos, decisões, precedentes institucionais  
- **Análise jurídica**: Interpretação e contextualização legal  
- **Ingestão de documentos**: Processamento de novos arquivos pelo usuário  

### **Quando Responde Diretamente**
```
✅ "O que diz a Resolução nº 19.272?"
✅ "Qual o conteúdo do Acórdão nº 192?"
✅ "Como a Lei 8.666 se aplica no TCE-PA?"
✅ "Quais são os prazos da Instrução Normativa X?"
✅ "Analise este documento [arquivo enviado]"
```

### **Quando Faz Handoff**
```
🏛️ Main Agent → Consultas gerais sobre capacidades ou coordenação complexa
🔍 Search Agent → Quando identifica número de expediente/processo específico
```

### **Pipeline RAG Especializado**
1. **Query Analysis**: Classificação e detecção de handoff  
2. **Vector DB Setup**: Configuração de coleções por escopo  
3. **Document Ingestion**: Docling → Chunking → Armazenamento  
4. **Retrieval**: Busca híbrida com filtros de acesso  
5. **Grading**: Avaliação de relevância multi-critério  
6. **Enrichment**: Contexto jurídico e referências cruzadas  
7. **Reranking**: Pontuação e seleção multi-critério  
8. **Generation**: Resposta formal com citações  
9. **Validation**: Verificação de qualidade e retry logic  

### **Estratégias de Chunking por Tipo**
- **Recursive**: Legislação geral  
- **Semantic**: Acordãos e decisões  
- **SDPM**: Resoluções administrativas  
- **Late**: Jurisprudência complexa  

---

## **🔍 Search Agent - Especialista em Busca**

### **Responsabilidades Primárias**
- **Sistema eTCE**: Consultas sobre expedientes e processos específicos  
- **Busca web**: Informações atuais e complementares  
- **Validação de números**: Formatos corretos de expediente/processo  
- **Integração de fontes**: Combinação de dados do sistema e web  
- **Formatação especializada**: Apresentação estruturada de dados processuais  

### **Quando Responde Diretamente**
```
✅ "Expediente 004506/2023 - qual o status?"
✅ "Processo TC/011165/2022 - última movimentação?"
✅ "Buscar notícias sobre TCE-PA na web"
✅ "Informações atuais sobre controle externo"
✅ "Quem é o atual governador do Pará?" (web search)
```

### **Quando Faz Handoff**
```
📄 RAG Agent → Quando encontra referência a documentos oficiais
🏛️ Main Agent → Consultas sobre capacidades ou coordenação geral
```

### **Ferramentas Especializadas**
- `etce_expedientes_info_tool`: Consulta de expedientes  
- `etce_processos_info_tool`: Consulta de processos  
- `web_search_tool`: Busca web contextual  
- `human_in_the_loop`: Escalação para casos complexos  

### **Padrões de Validação**
```python
# Expedientes: formato "XXXXXX/YYYY"
expediente_pattern = r"\d{6}/\d{4}"

# Processos: formato "TC/XXXXXX/YYYY" 
processo_pattern = r"TC/\d{6}/\d{4}"
```

---

## **🔄 Matriz de Decisão de Handoff**

### **Decisões do Main Agent**

| **Tipo de Consulta** | **Ação** | **Justificativa** |
|---------------------|----------|-------------------|
| Informações institucionais | **Responder diretamente** | Conhecimento base do agente |
| Legislação/Acordãos | **→ RAG Agent** | Requer processamento documental |
| Expediente/Processo específico | **→ Search Agent** | Ferramentas de sistema necessárias |
| Consulta ambígua | **Solicitar esclarecimento** | Triagem necessária |
| Fluxo multi-agente | **Coordenar sequência** | Orquestração complexa |

### **Decisões do RAG Agent**

| **Cenário** | **Ação** | **Justificativa** |
|-------------|----------|-------------------|
| Query sobre documento oficial | **Processar via pipeline** | Especialidade direta |
| Número de expediente detectado | **→ Search Agent** | Ferramenta específica necessária |
| Consulta sobre capacidades | **→ Main Agent** | Escopo fora da especialidade |
| Documento não encontrado | **Responder + sugerir alternativas** | Autonomia de resposta |

### **Decisões do Search Agent**

| **Cenário** | **Ação** | **Justificativa** |
|-------------|----------|-------------------|
| Expediente/Processo válido | **Consultar + responder** | Ferramenta direta disponível |
| Referência a documento oficial | **→ RAG Agent** | Processamento documental necessário |
| Consulta geral sobre sistema | **→ Main Agent** | Coordenação institucional |
| Formato inválido | **Solicitar correção + responder** | Validação + autonomia |

---

## **⚡ Padrões de Eficiência**

### **Evitar Handoffs Desnecessários**
```python
# ❌ Ineficiente
Main Agent → RAG Agent → "Documento não encontrado" → Main Agent

# ✅ Eficiente  
RAG Agent → "Documento não encontrado. Você pode consultar..."
```

### **Maximizar Respostas Diretas**
- **Main Agent**: 70% respostas diretas, 30% handoffs  
- **RAG Agent**: 85% respostas diretas, 15% handoffs  
- **Search Agent**: 90% respostas diretas, 10% handoffs  

### **Critério de Qualidade**
- **Tempo de resposta**: < 10s para consultas simples  
- **Precisão**: > 95% para informações institucionais  
- **Completude**: Resposta auto-suficiente sem necessidade de follow-up  

---

## **🛠️ Implementação Técnica**

### **Detecção de Handoff no RAG Agent**
```python
# Em query_analysis_node
if expediente_pattern.match(query) or processo_pattern.match(query):
    return {"handoff_to_agent": "Search_Agent"}
elif capability_query_detected(query):
    return {"handoff_to_agent": "Main_Agent"}
else:
    return {"handoff_to_agent": None}  # Processar localmente
```

### **Estado de Handoff**
```python
return Command(
    goto=state.handoff_to_agent,  # "Main_Agent" ou "Search_Agent"
    graph=Command.PARENT,         # Voltar ao grafo principal
    update={
        "messages": state.messages,
        "handoff_to_agent": None,  # Reset para evitar loops
    }
)
```

### **Validação de Retorno**
- **Verificar** se `state.handoff_to_agent` corresponde a nó válido no grafo principal  
- **Garantir** que o estado seja propagado corretamente  
- **Resetar** flags de handoff para evitar loops infinitos  

---

## **📊 Métricas de Sucesso**

### **Eficiência Operacional**
- **Taxa de handoff**: < 30% do total de consultas  
- **Loops de handoff**: 0% (zero tolerância)  
- **Respostas auto-suficientes**: > 85%  

### **Qualidade de Resposta**
- **Precisão**: > 95% para cada tipo de consulta  
- **Completude**: > 90% sem necessidade de follow-up  
- **Satisfação do usuário**: > 4.5/5.0  

### **Performance Técnica**
- **Latência média**: < 8s por consulta  
- **Taxa de erro**: < 2%  
- **Disponibilidade**: > 99.5%  

---

## **🔍 Exemplos Práticos de Fluxo**

### **Caso 1: Consulta Direta Main Agent**
```
Usuário: "Quais são as competências do TCE-PA?"
Main Agent: [Resposta direta com informações institucionais]
✅ Eficiente - 1 interação
```

### **Caso 2: Handoff RAG Agent**
```
Usuário: "O que diz o Acórdão nº 192?"
Main Agent: Identifica consulta documental → RAG Agent
RAG Agent: [Pipeline RAG + resposta com citações]
✅ Eficiente - 2 interações
```

### **Caso 3: Handoff Search Agent**
```
Usuário: "Status do expediente 004506/2023?"
Main Agent: Identifica consulta específica → Search Agent  
Search Agent: [Consulta eTCE + resposta formatada]
✅ Eficiente - 2 interações
```

### **Caso 4: Handoff Interno RAG → Search**
```
Usuário: "Analise o expediente 004506/2023"
RAG Agent: Detecta número de expediente → Search Agent
Search Agent: [Consulta + análise contextual]
✅ Eficiente - 2 interações diretas
```

Este modelo garante **máxima eficiência** com **mínima sobrecarga**, mantendo cada agente dentro de sua especialidade e evitando handoffs desnecessários.
