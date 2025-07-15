# 🎯 Documentação do Fluxo Conversacional

## 📋 **Fluxo Conversacional Correto**

### **1. INPUT (Usuário)**
```python
# ✅ CORRETO - Apenas INPUT real
test_state = ChatContasState(
    messages=[HumanMessage(content="Qual é a resolução 123/2024?")],
    user_id="test_user"  # Sistema de autenticação
)
```

### **2. PROCESSAMENTO (Agentes)**
```python
# Agentes extraem e processam internamente:
# - query = extraído de messages[última HumanMessage]
# - query_type = classificado via LLM
# - original_query = preservado para auditoria
# - routing_decision = decidido pelo main_agent
```

### **3. OUTPUT (Agentes)**
```python
# Agentes adicionam resposta aos messages:
updated_state = state.copy(
    messages=state.messages + [AIMessage(content="Resposta...")],
    query="Qual é a resolução 123/2024?",     # PROCESSAMENTO
    query_type="legislation",                 # PROCESSAMENTO
    routing_decision="RAG_Agent"              # PROCESSAMENTO
)
```

## ❌ **Exemplo INCORRETO**

```python
# ❌ NUNCA fazer isso - campos processados no INPUT
test_state = ChatContasState(
    messages=[HumanMessage(content="Qual é a resolução 123/2024?")],
    query="Qual é a resolução 123/2024?",  # ❌ Extraído dos messages
    query_type="legislation",              # ❌ Processado por LLM
    user_id="test_user"
)
```

## 🔍 **Tipos de Campos no ChatContasState**

### **[INPUT]** - Vem do usuário/sistema
- `messages=[]` - **Canal principal de comunicação**
- `user_id` - ID do usuário autenticado
- `username` - Nome do usuário
- `current_date` - Data atual do sistema

### **[PROCESSAMENTO]** - Gerado internamente pelos agentes
- `query` - Extraído dos messages
- `query_type` - Classificado via LLM
- `original_query` - Preservado para auditoria
- `current_step` - Etapa atual do fluxo
- `routing_decision` - Decisão de roteamento

### **[OUTPUT]** - Retornado ao usuário
- `messages=[]` - **Canal principal de comunicação** (AIMessage)

### **[INPUT+OUTPUT]** - Serve para ambos
- `messages=[]` - **Canal conversacional principal**
  - INPUT: HumanMessage do usuário
  - OUTPUT: AIMessage dos agentes

## 🎯 **Regras Importantes**

1. **INPUT**: Apenas `messages=[]` deve ser usado para entrada do usuário
2. **PROCESSAMENTO**: Campos como `query`, `query_type` são extraídos pelos agentes
3. **OUTPUT**: Resposta sempre via `messages=[]` (AIMessage)
4. **NUNCA**: Passar campos processados como INPUT inicial

## 📊 **Pipeline RAG Conversacional**

```python
# FLUXO CORRETO NO RAG PIPELINE:

# 1. INPUT (ChatContasState)
messages=[HumanMessage("Qual é a resolução 123/2024?")]

# 2. prepare_rag_state_node()
# - Extrai query dos messages
# - Analisa contexto para ingestion_required
# - Determina document_scope baseado em user_id

# 3. execute_rag_pipeline()
# - Processa com RAGState completo
# - Todos os campos populados dinamicamente

# 4. convert_to_chat_state_node()
# - Converte resposta para ChatContasState
# - Adiciona AIMessage com resposta estruturada

# 5. OUTPUT (ChatContasState)
messages=[
    HumanMessage("Qual é a resolução 123/2024?"),
    AIMessage("**Consulta RAG Processada**\n\n**Resposta:** ...")
]
```

## 🔧 **Exemplo de Teste Correto**

```python
from sample_agent.agents.tce_swarm.states import ChatContasState
from langchain_core.messages import HumanMessage

# ✅ CORRETO - Sistema conversacional real
test_state = ChatContasState(
    messages=[HumanMessage(content="Qual é a resolução 123/2024?")],
    user_id="test_user"  # Único campo de contexto necessário
)

# O sistema processará e extrairá:
# - query dos messages
# - query_type via LLM
# - routing_decision baseado na análise
# - resposta via AIMessage nos messages
```

Esta documentação garante que o sistema seja usado corretamente como uma aplicação conversacional real, onde o INPUT sempre vem via `messages=[]` e o processamento interno é transparente para o usuário. 