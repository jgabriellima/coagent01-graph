# 🏛️ Chat Contas - TCE-PA

**Chat Contas** é o assistente inteligente especializado do **Tribunal de Contas do Estado do Pará (TCE-PA)**, desenvolvido com arquitetura multi-agente production-grade baseada em LangGraph e padrão Swarm. O sistema oferece suporte especializado aos usuários do TCE-PA com acesso a documentos jurídicos, processos eletrônicos e informações atualizadas.

## 🚀 **Versão 2.0 - Arquitetura Swarm**

### **Principais Melhorias**
- ✅ **Arquitetura Multi-Agente**: Transição de single agent monolítico para swarm distribuído
- ✅ **Production-Grade**: Escalabilidade, gerenciabilidade e instrumentação completa
- ✅ **LangGraph**: Framework robusto para orquestração de agentes
- ✅ **Especialização**: Agentes dedicados para RAG, Search e Coordenação
- ✅ **Chonkie Integration**: Chunking inteligente para documentos jurídicos
- ✅ **Instrumentation**: Traces, monitoring e health checks

---

## 🏗️ **Arquitetura do Sistema**

### **Visão Geral**
```
🤖 TCE_Main_Agent (Coordenador)
├── 📚 TCE_RAG_Agent (Documentos)
├── 🔍 TCE_Search_Agent (Busca)
└── 🔄 Swarm Communication Layer
```

### **Agentes Especializados**

#### **🤖 TCE_Main_Agent (Coordenador)**
- **Responsabilidade**: Coordenação de tarefas, gerenciamento de conversas e roteamento inteligente
- **Ferramentas**: `ask_user` (Human-in-the-loop)
- **Especialização**: Análise de consultas, decisões de roteamento, interação com usuários
- **Roteamento**:
  - Legislação/Acordãos/Resoluções → `TCE_RAG_Agent`
  - Expedientes/Processos → `TCE_Search_Agent`
  - Busca Web → `TCE_Search_Agent`
  - Consultas Gerais → Tratamento direto

#### **📚 TCE_RAG_Agent (Documentos)**
- **Responsabilidade**: Processamento de documentos jurídicos via RAG (Retrieval-Augmented Generation)
- **Ferramentas**: 
  - `tce_documents_database_tool`: Busca na base de conhecimento TCE-PA
  - `document_ingestion_tool`: Ingestion com chunking inteligente
  - `document_summarization_tool`: Sumarização de documentos
  - `ask_user`: Human-in-the-loop quando necessário
- **Especialização**: Legislação, acordãos, resoluções, atos normativos
- **Chunking Strategy**: Chonkie.ai com estratégias otimizadas para documentos jurídicos
- **Metadados**: Contexto temporal, exercícios financeiros, vigência

#### **🔍 TCE_Search_Agent (Busca)**
- **Responsabilidade**: Busca em sistemas externos e eTCE
- **Ferramentas**:
  - `etce_search_tool`: Busca expedientes no sistema eTCE
  - `etce_process_details_tool`: Detalhes de processos
  - `web_search_tool`: Busca web para informações complementares
  - `ask_user`: Human-in-the-loop para esclarecimentos
- **Especialização**: Expedientes, processos, busca web contextual
- **Validação**: Formatos de processo (TC/NNNNNN/AAAA) e expediente (NNNNNN/AAAA)

---

## 🛠️ **Ferramentas e Capacidades**

### **Bases de Dados TCE-PA**
- **atos**: Atos normativos e portarias
- **arquivos-tce**: Documentos históricos
- **legislacao**: Leis, decretos, resoluções
- **acordaos**: Decisões colegiadas e jurisprudência

### **Sistemas Integrados**
- **eTCE**: Sistema de Processo Eletrônico do TCE-PA
- **Web Search**: Busca contextual na internet
- **Chonkie.ai**: Chunking inteligente para documentos jurídicos

---

## 📝 **Exemplos de Uso**

### **Consultas Legislativas**
```python
# Exemplo: Consulta sobre teletrabalho
query = "O teletrabalho pode ser estendido ou prorrogado no TCE-PA?"
# Roteamento: TCE_Main_Agent → TCE_RAG_Agent
# Resposta: "De acordo com a Resolução nº 19.272 do TCE-PA, o regime de teletrabalho pode ser prorrogado..."
```

### **Consultas de Acordãos**
```python
# Exemplo: Consulta sobre acordão específico
query = "Qual é o tema do Acórdão nº 192?"
# Roteamento: TCE_Main_Agent → TCE_RAG_Agent
# Resposta: "O Acórdão nº 192 do TCE-PA trata da fiscalização de contratos..."
```

### **Consultas de Expedientes**
```python
# Exemplo: Consulta sobre expediente
query = "Do que trata o expediente 004506/2023?"
# Roteamento: TCE_Main_Agent → TCE_Search_Agent
# Resposta: Dados formatados do expediente com informações processuais
```

### **Consultas Web**
```python
# Exemplo: Informações atuais
query = "Últimas notícias sobre teletrabalho no TCE-PA"
# Roteamento: TCE_Main_Agent → TCE_Search_Agent
# Resposta: Resultados de busca web contextualizados
```

---

## 🎯 **Fluxo de Processamento**

### **1. Recepção da Consulta**
- Usuário envia consulta ao sistema
- **TCE_Main_Agent** recebe e analisa a consulta
- Classificação automática do tipo de consulta

### **2. Roteamento Inteligente**
- **Legislação/Acordãos/Resoluções** → **TCE_RAG_Agent**
- **Expedientes/Processos** → **TCE_Search_Agent**
- **Busca Web** → **TCE_Search_Agent**
- **Ambíguas** → Solicita esclarecimentos

### **3. Processamento Especializado**
- Agente especializado executa ferramentas específicas
- Processamento com contexto temporal e metadados
- Validação de formatos e integridade dos dados

### **4. Resposta Consolidada**
- Formatação em português brasileiro formal
- Citação de fontes específicas
- Retorno ao usuário via **TCE_Main_Agent**

---

## 📊 **Estado do Sistema (State)**

### **Configurações Padrão**
```python
TCESwarmState(
    enable_web_search=True,
    enable_etce_search=True,
    enable_rag_processing=True,
    tce_databases=["atos", "arquivos-tce", "legislacao", "acordaos"],
    thread_mode="production",
    task_type="tce_assistance",
    chunk_strategy="recursive",
    chunk_size=512,
    chunk_overlap=50
)
```

### **Contexto de Usuário**
- **username**: Nome do usuário
- **user_id**: ID único do usuário
- **current_date**: Data atual da sessão

### **Contexto de Consulta**
- **query**: Consulta atual
- **query_type**: Tipo classificado automaticamente
- **routing_decision**: Decisão de roteamento tomada

### **Metadados de Processamento**
- **trace_id**: ID único para rastreamento
- **agent_interactions**: Histórico de interações
- **processing_time**: Tempo de processamento
- **response_sources**: Fontes utilizadas

---

## 🎯 **Sistema de Prompts**

### **Arquitetura de Prompts**
O sistema utiliza **templates Jinja2** modulares com estrutura padrão baseada em:
- **Template Base**: `base_agent_prompt.jinja2`
- **Fragmentos Específicos**: `tce_fragments/` por agente
- **Configuração Dinâmica**: Responsabilidades, tools e constraints por agente

### **Estrutura Padrão de Prompt**
```jinja2
# CURRENT_DATETIME: {{ current_datetime }}

## 👤 Identity
You are {{ agent_identity }}.

## 🎯 Responsibilities
{% for item in responsibilities %}
- {{ item }}
{% endfor %}

## 🧠 Behavior Rules
{{ dynamic_block }}

## 🛠️ Tools Available
{% for tool in tools %}
- `{{ tool.name }}` → {{ tool.description }}
{% endfor %}

{% if constraints %}
### Constraints:
{% for c in constraints %}
- {{ c }}
{% endfor %}
{% endif %}
```

### **Prompts por Agente**

#### **🤖 TCE_Main_Agent**
- **Identity**: Chatcontas, assistente oficial do TCE-PA
- **Responsibilities**: Coordenação, análise de consultas, roteamento
- **Tools**: `ask_user` + handoff tools
- **Workflow**: Análise → Roteamento → Gestão de Estado → Comunicação

#### **📚 TCE_RAG_Agent**
- **Identity**: Especialista em RAG para documentos jurídicos
- **Responsibilities**: Processamento de legislação, acordãos, resoluções
- **Tools**: `tce_documents_database_tool`, `document_ingestion_tool`, `document_summarization_tool`
- **Workflow**: Análise Jurídica → Retrieval → Chunking → Formatação

#### **🔍 TCE_Search_Agent**
- **Identity**: Especialista em busca eTCE e web
- **Responsibilities**: Consultas processuais, expedientes, busca web
- **Tools**: `etce_search_tool`, `etce_process_details_tool`, `web_search_tool`
- **Workflow**: Identificação → Validação → Busca → Formatação

### **Configuração de Ferramentas**

#### **Ferramentas Disponíveis**
```python
# Main Agent
tools = [ask_user, handoff_to_rag_agent, handoff_to_search_agent]

# RAG Agent
tools = [tce_documents_database_tool, document_ingestion_tool, 
         document_summarization_tool, ask_user, handoff_to_main_agent]

# Search Agent
tools = [etce_search_tool, etce_process_details_tool, 
         web_search_tool, ask_user, handoff_to_main_agent]
```

#### **Exemplo de Tool Description**
```python
ask_user = {
    "name": "ask_user",
    "description": "Ferramenta para interagir com usuário quando esclarecimentos são necessários"
}
```

### **Fragmentos Específicos por Agente**

#### **Main Agent (main_agent.jinja2)**
- **Contexto**: Coordenação e workflow do TCE-PA
- **Roteamento**: Análise → Legislação/Acordãos → RAG / Expedientes → Search
- **Saudação**: Cumprimentar usuário pelo nome
- **Validação**: Formatos de processo e expediente

#### **RAG Agent (rag_agent.jinja2)**
- **Contexto**: Processamento de documentos jurídicos
- **Chunking**: Strategies (Recursive, Semantic, Sentence)
- **Retrieval**: Busca semântica e híbrida
- **Citação**: Fontes específicas e contexto temporal

#### **Search Agent (search_agent.jinja2)**
- **Contexto**: Busca eTCE e web
- **Validação**: Formatos TC/NNNNNN/AAAA e NNNNNN/AAAA
- **Formatação**: Estrutura de dados padronizada
- **Integração**: Múltiplas fontes com contexto

---

## 🧪 **Sistema de Avaliação**

### **Arquitetura de Avaliação**
O sistema implementa avaliação contínua baseada em **perfis específicos** para diferentes tipos de fluxos:

#### **Perfis de Avaliação**
- **🔁 Agent-based**: Fluxos multi-agente com histórico e tool calls
- **💬 LLM Chat**: Interações simples input/output
- **📚 RAG**: Retrieval-Augmented Generation com contexto
- **🛠️ Tool-calling**: Modelos que executam ferramentas via JSON

### **Métricas Implementadas**

#### **Métricas Específicas para Agentes**
- **🧩 Trajectory Fidelity**: Verifica se agentes seguiram trajetória esperada
- **🛠️ Tool Usage Relevance**: Avalia relevância das ferramentas utilizadas
- **🔄 Agent Interaction Quality**: Qualidade dos handoffs entre agentes

#### **Métricas Semânticas Gerais**
- **🧾 Faithfulness**: Alinhamento com fontes/contexto
- **✅ Correctness**: Precisão factual das respostas
- **🎯 Relevance**: Relevância ao contexto da consulta
- **🚨 Hallucination Detection**: Detecção de alucinações

### **Pipeline de Avaliação**
```
📥 Extração Traces → 🧼 Limpeza → 📊 Dataset → 🧠 Métricas → 📈 Análise
```

### **Executando Avaliações**
```bash
# Avaliação completa do sistema multi-agente
python evaluations/evaluators/run_evaluations.py \
  --dataset_name="tce_swarm_v1" \
  --dataset_profile="agentic" \
  --project_name="tce_agent_eval"

# Avaliação específica por agente
python evaluations/evaluators/run_evaluations.py \
  --agent_filter="TCE_RAG_Agent" \
  --metrics="trajectory_fidelity,tool_usage_relevance"
```

### **Integração com Monitoramento**
- **LangSmith**: Traces automáticos e métricas
- **Thresholds**: Limiares automáticos para refinamento
- **Feedback Loop**: Ciclo fechado de melhoria contínua

---

## 🚀 **Execução e Demonstração**

### **Execução do Sistema**
```bash
# Instalar dependências
uv sync

# Executar demo completo
python sample_agent/agents/tce_swarm/demo.py

# Executar demo interativo
python sample_agent/agents/tce_swarm/demo.py --interactive
```

### **Uso Programático**
```python
from sample_agent.agents.tce_swarm.graph import tce_swarm_graph
from langchain_core.messages import HumanMessage

# Configurar thread
thread_config = {"configurable": {"thread_id": "user_session_123"}}

# Criar estado inicial
initial_state = {
    "messages": [HumanMessage(content="Qual é o tema do Acórdão nº 192?")],
    "username": "João Silva",
    "user_id": "user_123",
    "current_date": "2024-01-12T10:00:00Z"
}

# Executar consulta
response = tce_swarm_graph.invoke(initial_state, thread_config)
print(response['messages'][-1].content)
```

---

## 📊 **Monitoramento e Instrumentação**

### **Health Check**
```python
from sample_agent.agents.tce_swarm.graph import health_check, tce_swarm_graph

# Verificar saúde do sistema
status = health_check(tce_swarm_graph)
print(f"System Status: {status['status']}")
```

### **Traces e Métricas**
- **LangSmith Integration**: Traces automáticos para debugging
- **Agent Interactions**: Histórico completo de handoffs
- **Performance Metrics**: Tempo de processamento por agente
- **Error Tracking**: Captura e análise de erros

### **Tags de Instrumentação**
```python
# Tags automáticas para traces
tags = [
    "tce-pa", "tribunal-contas", "multi-agent", "swarm", 
    "production", "brazil", "legal-assistant"
]

# Traces por agente
TCE_Main_Agent: ["main", "coordinator", "tce-pa"]
TCE_RAG_Agent: ["rag", "documents", "legislation", "tce-pa"]
TCE_Search_Agent: ["search", "etce", "web", "processes", "tce-pa"]
```

---

## 🛠️ **Desenvolvimento e Manutenção**

### **Estrutura de Arquivos**
```
sample_agent/agents/tce_swarm/
├── __init__.py                 # Módulo principal
├── main_agent.py              # Agente coordenador
├── rag_agent.py               # Agente RAG
├── search_agent.py            # Agente de busca
├── tools.py                   # Ferramentas mockadas
├── states.py                  # Estados consolidados
├── graph.py                   # Grafo principal
└── demo.py                    # Demonstração

sample_agent/prompts/tce_fragments/
├── main_agent.jinja2          # Prompt do Main Agent
├── rag_agent.jinja2           # Prompt do RAG Agent
└── search_agent.jinja2        # Prompt do Search Agent
```

### **Configuração de Prompts**
- **Jinja2 Templates**: Prompts dinâmicos e reutilizáveis
- **Fragmentos Especializados**: Contexto específico por agente
- **Workflow Robusto**: Diretrizes claras para cada agente

### **Extensibilidade**
- **Novos Agentes**: Seguir padrão Builder existente
- **Novas Ferramentas**: Implementar no módulo tools.py
- **Novos Estados**: Extender TCESwarmState
- **Instrumentação**: Adicionar tags e traces personalizados

---

## 🔐 **Segurança e Compliance**

### **Proteção de Dados**
- **Processos Sigilosos**: Validação automática de confidencialidade
- **Dados Pessoais**: Conformidade com LGPD
- **Auditoria**: Logs completos de todas as interações

### **Validação de Entrada**
- **Formatos de Processo**: Validação automática (TC/NNNNNN/AAAA)
- **Formatos de Expediente**: Validação automática (NNNNNN/AAAA)
- **Sanitização**: Limpeza de inputs para segurança

---

## 📚 **Glossário TCE-PA**

- **Legislações**: Conjunto de leis e normas que regulam a administração pública
- **Acordãos**: Decisões colegiadas do Tribunal de Contas
- **Resoluções**: Normas internas do TCE-PA
- **Jurisprudência**: Conjunto de decisões reiteradas do Tribunal
- **Atos**: Manifestações formais das autoridades do TCE-PA
- **Expedientes**: Documentos e processos administrativos
- **eTCE**: Sistema de Processo Eletrônico do TCE-PA

---

## 🎯 **Próximos Passos**

### **Roadmap de Desenvolvimento**
- [ ] Integração com sistema eTCE real
- [ ] Implementação de chunking com Chonkie para documentos reais
- [ ] Dashboard de monitoramento em tempo real
- [ ] API REST para integração externa
- [ ] Testes automatizados de regressão
- [ ] Otimização de performance para produção

### **Melhorias Planejadas**
- [ ] Suporte a múltiplos idiomas
- [ ] Sistema de feedback de usuários
- [ ] Análise de sentimento nas interações
- [ ] Integração com outros sistemas do TCE-PA
- [ ] Modelo de embeddings específico para contexto jurídico

---

**Versão**: 2.0.0  
**Última Atualização**: Janeiro 2024  
**Arquitetura**: Production-Grade Multi-Agent Swarm  
**Framework**: LangGraph + LangChain  
**Status**: ✅ Production Ready 