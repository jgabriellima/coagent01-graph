# Multi-Agent Swarm System Demo

Este repositório contém uma demonstração completa de um sistema multi-agente usando LangGraph com padrão Swarm.

## 📋 Conteúdo

- **`multi_agent_swarm_demo.py`**: Script Python completo com toda a funcionalidade
- **`agent5.py`**: Código original do sistema multi-agente

## 🚀 Exemplo Demonstrado

**Pergunta**: "Qual a temperatura atual no Campeche? Agora pegue essa temperatura e multiplique pelo numero que eu estou pensando e me retorne o final."

**Fluxo Esperado**:
1. Main Agent analisa a pergunta
2. Delega para Bob (especialista em clima) para obter temperatura de Campeche
3. Bob obtém temperatura (70°)
4. Main Agent pergunta ao usuário o número que está pensando
5. Delega para Alice (especialista em matemática) para calcular 70 × número
6. Retorna resultado final

## 🎯 Agentes Especializados

### Main Agent (Coordenador)
- **Responsabilidade**: Orquestração de tarefas e coordenação
- **Ferramentas**: `ask_user`, handoffs para Alice e Bob
- **Papel**: Analisa, planeja, coleta informações e delega

### Alice (Especialista em Matemática) 🧮
- **Responsabilidade**: Cálculos matemáticos
- **Ferramentas**: `calculate_math`, handoffs para Bob e main_agent
- **Papel**: Executa operações matemáticas

### Bob (Especialista em Clima - Pirata) 🏴‍☠️
- **Responsabilidade**: Informações climáticas
- **Ferramentas**: `get_weather`, `ask_user`, handoffs para Alice e main_agent  
- **Papel**: Fornece dados meteorológicos (com personalidade pirata)

## 💾 MemoryCheckpointer

O sistema utiliza `MemorySaver` para:
- ✅ Persistir estado entre execuções
- ✅ Permitir inspeção detalhada do estado
- ✅ Rastrear histórico de mensagens
- ✅ Facilitar debugging e análise

## 🏃‍♂️ Como Executar

### Opção 1: Script Python Direto
```bash
cd sample_agent
python multi_agent_swarm_demo.py
```

### Opção 2: Criar Notebook Jupyter

#### Método 1: Conversão Automática
```bash
# Instalar jupyter se necessário
pip install jupyter nbconvert

# Converter Python para Notebook
jupyter nbconvert --to notebook --execute multi_agent_swarm_demo.py
```

#### Método 2: Criar Notebook Manualmente

1. **Abrir Jupyter**:
```bash
jupyter notebook
```

2. **Criar novo notebook** e copiar cada seção do `multi_agent_swarm_demo.py` em células separadas:

**Célula 1 (Markdown)**:
```markdown
# Multi-Agent Swarm System Demo

Este notebook demonstra um sistema multi-agente usando LangGraph com padrão Swarm.
```

**Célula 2 (Code)** - Importações:
```python
# Copiar seção "1. CONFIGURAÇÃO INICIAL" do .py
```

**Célula 3 (Code)** - Tools:
```python
# Copiar seção "2. DEFINIÇÃO DE TOOLS ESPECIALIZADAS" do .py
```

E assim por diante...

#### Método 3: Usar o script fornecido
```python
# No Jupyter Notebook, execute em células separadas:

# Célula 1: Configuração
exec(open('multi_agent_swarm_demo.py').read())

# Célula 2: Criar sistema
graph = create_multi_agent_system()

# Célula 3: Executar exemplo
thread_config = run_campeche_example(graph)

# Célula 4: Inspecionar estado
inspect_checkpointer_state(graph, thread_config)

# Célula 5: Continuar com input do usuário
continue_with_user_input(graph, thread_config, 3)

# Célula 6: Análise final
analyze_final_state(graph, thread_config)
```

## 🔍 Funcionalidades de Debugging

### Inspeção de Estado
```python
# Ver estado atual
inspect_state_details(graph, thread_config)

# Ver estado do checkpointer
inspect_checkpointer_state(graph, thread_config)
```

### Reset de Conversação
```python
# Resetar para novo teste
new_config = reset_conversation("novo-thread-id")
```

### Continuação com Input do Usuário
```python
# Simular resposta do usuário
continue_with_user_input(graph, thread_config, "numero_do_usuario")
```

## 📊 Saída Esperada

```
🎬 Iniciando execução do exemplo...
💬 Input: Qual a temperatura atual no Campeche? Agora pegue essa temperatura e multiplique pelo numero que eu estou pensando e me retorne o final.

🚶‍♂️ STEP 1:
🎯 Active Agent: main_agent
📍 Location: N/A
🌡️ Temperature: N/A
🧮 Math Expression: N/A
🔢 Math Result: N/A
💬 Message Type: AIMessage
💬 Content: I'll help you with that! Let me break this down into steps:

1. First, I'll get the current temperature in Campeche
2. Then I'll ask you for the number you're thinking of
3. Finally, I'll multiply the temperature by your number

Let me start by getting the weather information for Campeche.

🚶‍♂️ STEP 2:
🎯 Active Agent: Bob
📍 Location: Campeche
🌡️ Temperature: 70 degrees
[... continua ...]
```

## 🎯 Estado Final Esperado

```
📊 ANÁLISE FINAL DO ESTADO:
🏁 Estado Final:
   🎯 Agente Ativo: Alice
   📍 Localização: Campeche
   🌡️ Temperatura: 70 degrees
   🧮 Expressão Matemática: 70 * 3
   🔢 Resultado do Cálculo: 210.0

🎯 RESULTADO ESPERADO:
   🌡️ Temperatura do Campeche: 70°
   🔢 Número pensado: 3.0
   ✅ Resultado Final: 70° × número = 210.0
```

## 🔧 Dependências

```bash
pip install langchain-openai langgraph langgraph-supervisor langgraph-swarm langchain-groq pydantic
```

## 🚀 Próximos Passos

1. 🔧 Implementar mais ferramentas especializadas
2. 🌐 Conectar APIs reais (OpenWeatherMap, etc.)
3. 🧠 Adicionar mais agentes especialistas
4. 📊 Dashboard de monitoramento de estado
5. 🔄 Implementar retry logic e error handling

## 📝 Notas Importantes

- ✅ Sistema usa MemoryCheckpointer para persistência
- ✅ Logging detalhado para debugging
- ✅ Handoff inteligente entre agentes
- ✅ Interrupção para input do usuário
- ✅ Estado completamente inspecionável

Este sistema demonstra um padrão robusto para coordenação multi-agente com rastreamento completo de estado! 