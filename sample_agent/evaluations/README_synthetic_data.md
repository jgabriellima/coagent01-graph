# Gerador de Dados Sintéticos para Sistema de Swarm Agents

Este sistema gera dados sintéticos para avaliar o desempenho dos agentes no seu sistema de swarm, integrando com LangSmith para coleta automática de traces e executando evaluators para análise de performance.

## 🎯 Visão Geral

O sistema é composto por três componentes principais:

1. **Gerador de Dados Sintéticos**: Cria cenários realistas baseados no comportamento dos agentes
2. **Executor de Cenários**: Executa os cenários nos agentes reais para coletar traces
3. **Pipeline de Evaluation**: Integra geração de dados com suite de evaluators

## 🏗️ Arquitetura

### Agentes Suportados

- **Alice Agent**: Especialista em matemática com tool `calculate_math`
- **Bob Agent**: Especialista em clima (fala como pirata) com tools `get_weather` e `ask_user`
- **Main Agent**: Coordenador que gerencia tarefas e handoffs entre agentes

### Tipos de Cenários

1. **Simples**: Operações básicas (2+2, clima de SP)
2. **Médios**: Operações intermediárias (expressões compostas, cidades específicas)
3. **Complexos**: Operações avançadas (expressões aninhadas, coordenação multi-agente)
4. **Edge Cases**: Casos extremos para testar robustez

## 🚀 Uso Rápido

### Configuração Inicial

```bash
# Configurar variáveis de ambiente
export OPENAI_API_KEY="sua_api_key_aqui"
export LANGSMITH_API_KEY="sua_langsmith_api_key_aqui"
export LANGCHAIN_TRACING_V2="true"

# Instalar dependências
pip install -r requirements.txt
```

### Teste Rápido

```bash
# Executar pipeline completo (3 cenários por agente)
python sample_agent/evaluations/run_evaluation_pipeline.py --quick-test

# Apenas gerar dados sintéticos
python sample_agent/evaluations/run_synthetic_data_generator.py --quick-test
```

### Execução Completa

```bash
# Pipeline completo com configuração personalizada
python sample_agent/evaluations/run_evaluation_pipeline.py \
  --project "minha-avaliacao" \
  --scenarios 20 \
  --model "openai:gpt-4o" \
  --evaluator-profile "comprehensive"
```

## 📚 Scripts Disponíveis

### 1. `synthetic_data_generator.py`

**Funcionalidade**: Núcleo do sistema de geração de dados sintéticos.

**Características**:
- Gera cenários baseados no comportamento dos agentes
- Executa cenários nos agentes reais
- Coleta traces automaticamente via LangSmith
- Gera relatórios detalhados

**Uso programático**:
```python
from sample_agent.evaluations.synthetic_data_generator import SyntheticDataGenerator

generator = SyntheticDataGenerator(
    model_name="openai:gpt-4o-mini",
    temperature=0.7,
    langsmith_project_name="meu-projeto",
    num_scenarios_per_agent=15
)

scenarios = generator.generate_all_scenarios()
results = await generator.execute_all_scenarios(scenarios)
report = generator.generate_report(results)
```

### 2. `run_synthetic_data_generator.py`

**Funcionalidade**: Interface de linha de comando para geração de dados sintéticos.

**Parâmetros principais**:
- `--project`: Nome do projeto LangSmith
- `--scenarios`: Número de cenários por agente (padrão: 15)
- `--model`: Modelo a usar (padrão: openai:gpt-4o-mini)
- `--temperature`: Temperatura do modelo (padrão: 0.7)
- `--quick-test`: Modo teste rápido (3 cenários)

**Exemplos**:
```bash
# Execução básica
python run_synthetic_data_generator.py

# Configuração personalizada
python run_synthetic_data_generator.py \
  --project "avaliacao-agentes" \
  --scenarios 25 \
  --model "openai:gpt-4o" \
  --temperature 0.5

# Teste rápido
python run_synthetic_data_generator.py --quick-test
```

### 3. `run_evaluation_pipeline.py`

**Funcionalidade**: Pipeline completo que integra geração de dados com evaluation.

**Fases do Pipeline**:
1. **Geração de Dados**: Cria e executa cenários sintéticos
2. **Evaluation**: Executa suite de evaluators nos traces coletados
3. **Relatório**: Gera relatório consolidado com métricas

**Parâmetros principais**:
- `--only-generate`: Apenas gerar dados sintéticos
- `--only-evaluate`: Apenas executar evaluators
- `--evaluator-profile`: Perfil de evaluators (minimal, agentic, comprehensive)
- `--evaluation-model`: Modelo para evaluation (padrão: gpt-4o)

**Exemplos**:
```bash
# Pipeline completo
python run_evaluation_pipeline.py \
  --project "pipeline-completo" \
  --scenarios 20 \
  --evaluator-profile "comprehensive"

# Apenas geração de dados
python run_evaluation_pipeline.py \
  --only-generate \
  --scenarios 15

# Apenas evaluation (dados existentes)
python run_evaluation_pipeline.py \
  --only-evaluate \
  --project "projeto-existente"
```

## 📊 Outputs e Relatórios

### Estrutura de Arquivos

```
sample_agent/evaluations/
├── results/                     # Diretório de resultados
│   ├── synthetic_data_report_*.json
│   ├── evaluation_results_*.json
│   └── consolidated_report_*.json
├── synthetic_data_generator.py
├── run_synthetic_data_generator.py
└── run_evaluation_pipeline.py
```

### Relatórios Gerados

1. **Relatório de Dados Sintéticos** (`synthetic_data_report_*.json`):
   - Estatísticas de geração e execução
   - Métricas por agente e complexidade
   - Cenários que falharam
   - Tempos de execução

2. **Relatório de Evaluation** (`evaluation_results_*.json`):
   - Resultados dos evaluators
   - Métricas de performance
   - Scores detalhados por run

3. **Relatório Consolidado** (`consolidated_report_*.json`):
   - Visão geral do pipeline
   - Métricas combinadas
   - Resumo executivo

### Exemplo de Métricas

```json
{
  "pipeline_summary": {
    "project_name": "minha-avaliacao",
    "overall_success_rate": 87.5,
    "total_avg_time": 2.3
  },
  "data_generation": {
    "total_scenarios": 45,
    "successful": 42,
    "success_rate": 93.3
  },
  "evaluation_results": {
    "total_runs": 42,
    "evaluators_executed": 6,
    "avg_scores": {
      "faithfulness": 0.85,
      "relevance": 0.89,
      "tool_usage": 0.92
    }
  }
}
```

## 🔧 Configuração Avançada

### Personalização de Cenários

Para adicionar novos tipos de cenários, edite os templates em `synthetic_data_generator.py`:

```python
# Adicionar novos cenários para Alice
self.alice_scenarios.append({
    "type": "custom",
    "template": "Resolva o problema: {expression}",
    "expressions": ["nova_expressao_1", "nova_expressao_2"]
})
```

### Configuração de Evaluators

O sistema usa perfis de evaluators configuráveis:

- **minimal**: Apenas evaluators básicos
- **agentic**: Evaluators específicos para agentes
- **comprehensive**: Todos os evaluators disponíveis

### Integração com LangSmith

O sistema configura automaticamente:
- Nome do projeto programaticamente
- Coleta de traces habilitada
- Metadados de execução

## 🎯 Casos de Uso

### 1. Desenvolvimento de Agentes

```bash
# Teste rápido durante desenvolvimento
python run_evaluation_pipeline.py --quick-test

# Evaluation completa antes de deploy
python run_evaluation_pipeline.py \
  --project "pre-deploy-validation" \
  --scenarios 30 \
  --evaluator-profile "comprehensive"
```

### 2. Análise de Performance

```bash
# Comparar diferentes modelos
python run_evaluation_pipeline.py \
  --project "gpt-4o-vs-4o-mini" \
  --model "openai:gpt-4o" \
  --scenarios 25

python run_evaluation_pipeline.py \
  --project "gpt-4o-vs-4o-mini" \
  --model "openai:gpt-4o-mini" \
  --scenarios 25
```

### 3. Regression Testing

```bash
# Gerar baseline
python run_evaluation_pipeline.py \
  --project "baseline-v1" \
  --scenarios 50

# Comparar após mudanças
python run_evaluation_pipeline.py \
  --project "after-changes-v1" \
  --scenarios 50
```

## 🔍 Troubleshooting

### Problemas Comuns

1. **Erro de API Key**:
   ```
   ⚠️  OPENAI_API_KEY não encontrada!
   ```
   **Solução**: Configure `export OPENAI_API_KEY="sua_key"`

2. **LangSmith não coleta traces**:
   ```
   ⚠️  LANGSMITH_API_KEY não encontrada!
   ```
   **Solução**: Configure `export LANGSMITH_API_KEY="sua_key"`

3. **Agents não respondem**:
   - Verifique se os agentes estão configurados corretamente
   - Teste com `--quick-test` primeiro
   - Verifique logs de erro com `--verbose`

### Debugging

```bash
# Execução com logs detalhados
python run_evaluation_pipeline.py --verbose --quick-test

# Apenas geração para debug
python run_synthetic_data_generator.py --scenarios 3 --verbose
```

## 📈 Próximos Passos

1. **Análise de Resultados**: Examine os relatórios JSON gerados
2. **LangSmith Dashboard**: Visualize traces e métricas
3. **Otimização**: Ajuste configurações baseado nos resultados
4. **Iteração**: Execute novamente com configurações otimizadas

## 🤝 Contribuição

Para adicionar novos tipos de cenários ou evaluators:

1. Edite os templates em `synthetic_data_generator.py`
2. Adicione novos evaluators em `evaluators/`
3. Registre no `evaluator_registry.py`
4. Teste com `--quick-test`

---

**Pronto para usar!** Execute `python run_evaluation_pipeline.py --quick-test` para começar. 