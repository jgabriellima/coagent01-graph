# Teste Isolado de Análise de Workflow

## Visão Geral

Este teste permite analisar a estrutura de workflows de forma isolada, fornecendo insights detalhados sobre:
- Agentes e suas capacidades
- Ferramentas disponíveis
- Padrões de colaboração
- Complexidade do sistema
- Recomendações de testes

## Funcionalidades

### 🔍 Análise Estrutural
- **Tipo de workflow**: CompiledStateGraph vs Runnable
- **Agentes identificados**: Nomes, papéis e capacidades
- **Ferramentas disponíveis**: Lista completa de tools
- **Esquema de estado**: Campos do estado do workflow

### 🧠 Insights Inteligentes
- **Classificação de complexidade**: Low, Medium, High
- **Padrão de colaboração**: Hub-and-spoke, Peer-to-peer
- **Tipo de sistema**: Single-agent, Small/Medium/Large multi-agent
- **Inferência de papéis**: Baseada em nomes e capacidades

### 📊 Relatório Detalhado
- **Agentes detalhados**: Papel, capacidades, ferramentas, padrões de interação
- **Avaliação de complexidade**: Por categoria (agentes, ferramentas, capacidades)
- **Recomendações de testes**: Unit tests, integration tests, edge cases
- **Capacidades identificadas**: Lista completa de capabilities

## Como Usar

### 1. Execução Básica

```bash
# Navegar até o diretório
cd sample_agent/evaluations/datasets/generator/synthesizer

# Executar análise
python test_workflow_analysis.py
```

### 2. Usar com Workflow Customizado

```python
from test_workflow_analysis import WorkflowAnalyzer

# Criar analisador
analyzer = WorkflowAnalyzer()

# Seu workflow customizado
workflow = create_custom_workflow()

# Analisar
analysis = analyzer.analyze_workflow_detailed(workflow)

# Imprimir relatório
print_analysis_report(analysis)
```

### 3. Análise Programática

```python
# Apenas estrutura básica
basic_analysis = analyzer.analyze_workflow_structure(workflow)

# Análise completa com insights
detailed_analysis = analyzer.analyze_workflow_detailed(workflow)

# Acessar dados específicos
agents = detailed_analysis["detailed_agents"]
complexity = detailed_analysis["complexity_assessment"]
recommendations = detailed_analysis["testing_recommendations"]
```

## Exemplo de Saída

```
================================================================================
🔬 RELATÓRIO DE ANÁLISE DE WORKFLOW
================================================================================

📊 INFORMAÇÕES BÁSICAS:
   • Tipo: CompiledStateGraph
   • Descrição: Multi-agent workflow with Alice (math) and Bob (weather) agents

💡 INSIGHTS DO WORKFLOW:
   • Número de agentes: 3
   • Total de capacidades: 8
   • Total de ferramentas: 3
   • Tipo de workflow: Small multi-agent system
   • Nível de complexidade: Medium complexity
   • Padrão de colaboração: Hub-and-spoke (coordinator pattern)

🤖 AGENTES DETALHADOS:

   📋 alice_agent:
      • Papel: Mathematical computation specialist
      • Capacidades: 3
      • Ferramentas: ['calculate_math']
      • Padrões de interação:
        - Collaborates with 2 other agents

   📋 bob_agent:
      • Papel: Weather information provider
      • Capacidades: 2
      • Ferramentas: ['get_weather', 'ask_user']
      • Padrões de interação:
        - Collaborates with 2 other agents

   📋 main_agent:
      • Papel: Task coordinator and orchestrator
      • Capacidades: 3
      • Ferramentas: []
      • Padrões de interação:
        - Receives initial user requests
        - Delegates tasks to specialized agents
        - Coordinates multi-agent workflows
        - Collaborates with 2 other agents
```

## Casos de Uso

### 1. **Desenvolvimento de Agentes**
- Validar estrutura de workflow antes do deploy
- Identificar agentes e suas responsabilidades
- Verificar colaboração entre agentes

### 2. **Planejamento de Testes**
- Obter recomendações específicas de testes
- Identificar cenários de edge cases
- Planejar testes de integração

### 3. **Documentação Automática**
- Gerar documentação do workflow
- Criar diagramas de arquitetura
- Documentar APIs e interfaces

### 4. **Auditoria e Revisão**
- Avaliar complexidade do sistema
- Identificar pontos de melhoria
- Validar padrões de design

## Estrutura do Resultado

```json
{
  "type": "CompiledStateGraph",
  "workflow_description": "Multi-agent workflow description",
  "agents": {
    "agent_name": {
      "capabilities": [...],
      "tools": [...],
      "prompt_info": {...}
    }
  },
  "detailed_agents": {
    "agent_name": {
      "role_description": "Agent role",
      "interaction_patterns": [...]
    }
  },
  "workflow_insights": {
    "agent_count": 3,
    "complexity_level": "Medium complexity",
    "collaboration_pattern": "Hub-and-spoke"
  },
  "complexity_assessment": {
    "overall_complexity": "Medium complexity",
    "agent_complexity": {...},
    "tool_complexity": {...}
  },
  "testing_recommendations": {
    "unit_tests": [...],
    "integration_tests": [...],
    "edge_cases": [...]
  }
}
```

## Outputs Gerados

1. **Console**: Relatório formatado e colorido
2. **JSON**: `workflow_analysis_result.json` com dados completos
3. **Insights**: Análise inteligente da estrutura

## Customização

### Estender Análise

```python
class CustomWorkflowAnalyzer(WorkflowAnalyzer):
    def _custom_analysis(self, analysis):
        # Sua análise customizada
        return custom_insights
```

### Personalizar Relatório

```python
def custom_report(analysis):
    # Seu formato de relatório
    print("Custom Analysis Report")
    # ...
```

## Compatibilidade

- **LangGraph**: CompiledStateGraph
- **LangChain**: Runnable, Chain
- **Multi-agent Systems**: Swarm, Crew, AutoGen
- **Custom Workflows**: Qualquer workflow compatível

## Próximos Passos

1. Execute o teste básico
2. Analise o relatório gerado
3. Use insights para melhorar seu workflow
4. Implemente testes recomendados
5. Documente sua arquitetura

---

**Nota**: Este teste é parte do framework de synthetic data generation e evaluation. Para uso em produção, considere integrar com pipeline de CI/CD. 