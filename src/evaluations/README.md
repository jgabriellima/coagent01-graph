# Avaliação de Agentes Multi-Agent

## Fluxo de Avaliação

```
---
config:
  layout: dagre
---
flowchart TD
 subgraph PIPELINE_EVAL_REFINEMENT["🧪 Pipeline de Evaluation &amp; Refinamento"]
        A1["📥 Extração de Traces"]
        A2["🧼 Limpeza &amp; Anonimização"]
        A3["📊 Dataset de Avaliação"]
        B1["🧠 Execução de Métricas perfil-specific"]
        B2["🧩 Trajectory Fidelity"]
        B3["🛠 Tool Usage Relevance"]
        B4["🧾 Faithfulness / Relevance / Correctness"]
        C1["📈 Atualização de Indicadores"]
        D1["🔍 Seleção automática de exemplos críticos"]
        D2{"⚙️ Verifica thresholds: seguir refinamento?"}
        D3A["🧬 Preparação/Filtro para Fine-Tuning"]
        D3B["🔁 Início do Subflow de MetaPrompting"]
        F1["🚀 Implantação"]
        F2["🧪 Teste de Regressão pós-deploy"]
        F3["🏷️ Registro &amp; Promoção"]
        P1["📄 Prompt Base + Exemplos"]
  end
 subgraph MetaPrompting_Subflow["🔁 Subflow: MetaPrompting Iterativo"]
        P2["🧠 Refinamento via LLM"]
        P3["📊 Validação estrutural"]
        P4{"Refina novamente?"}
        P5["🔁 Novo Ciclo"]
        P6["✅ Enviar para Avaliação Automática"]
  end
 subgraph INFRA_ORQUESTRACAO["🧩 Infraestrutura de Orquestração"]
        G1["⚙️ Airflow DAG ou Prefect Pipeline"]
        G2["⏱️ Agendamento Recorrente"]
        G3["📦 Paralelismo por Agente/Job"]
        G4["🔄 Retry, Observabilidade, Logs"]
  end
    A1 --> A2
    A2 --> A3
    A3 --> B1
    B1 --> B2 & B3 & B4
    B2 --> C1
    B3 --> C1
    B4 --> C1
    C1 --> D1
    D1 --> D2
    D2 -- Não precisa --> F3
    D2 -- "Precisa fine-tune" --> D3A
    D3A --> F1
    D2 -- Refino via prompt --> D3B
    D3B --> P1
    F1 --> F2
    F2 --> F3
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 -- Sim --> P5
    P5 --> P2
    P4 -- Não --> P6
    P6 L_P6_B1_0@--> B1
    G1 --> G2
    G2 --> G3
    G3 --> G4
    G1 -. executa ciclicamente .-> A1
    F3 -. Trigger externo (CI/CD ou Airflow scheduler) .-> G1
    L_P6_B1_0@{ animation: slow }

```
🧠 Decisões Arquiteturais

1. Seletividade com base em Thresholds

Após o cálculo das métricas, o sistema verifica se os scores obtidos estão dentro dos limites definidos por perfil.

Caso afirmativo, evita custos desnecessários de refinamento.

2. Execução de Métricas conforme o Perfil

O pipeline identifica o perfil do dataset (agentic, llm_io, rag, tool_call) e aplica apenas as métricas relevantes.

Isso permite flexibilidade e uso eficiente de recursos.

3. MetaPrompting Iterativo como Alternativa ao Fine-Tuning

Quando o problema não exige re-treinamento do modelo, mas sim reformulação do prompt, ativamos o subflow MetaPrompting.

Ele aplica LLM para reescrita de prompts usando templates Jinja2 + validação estrutural (via AST/XML ou heurísticas).

4. Limpeza & Anonimização como Pré-requisito

Antes de qualquer avaliação, as entradas e saídas passam por pré-processamento com regex, heurísticas ou ferramentas como Microsoft Presidio.

5. Orquestração Modular

A execução ocorre via pipelines agendáveis (Airflow, Prefect), com suporte a paralelismo, retries e logs detalhados.

6. Ciclo Completo Observável

Todos os resultados são registrados via LangSmith ou LangFuse com tags, run_ids, thresholds e versão do prompt/model.

Este modelo representa a fundação para avaliações contínuas de agentes inteligentes e pipelines LLM com ciclo de feedback fechado e refinamento progressivo.

Essa arquitetura é compatível com ferramentas como:

DeepEval: métricas semânticas (faithfulness, relevance)

AgentEval: métricas de fluxo e tool-usage

LangSmith / LangFuse: rastreamento, visualização e versionamento

## Ferramentas de Avaliação

### OpenEvals
- Framework de avaliação open-source para modelos de linguagem. é seu ponto de partida leve e prático para testes automatizados e integra-se bem a CI/CD.

### DeepEval
Proporciona avaliação de saídas de LLMs em geral, cobrindo aspectos como:
- Hallucinações
- Relevância
- Fidelidade
- Viés

**Características:**
- Integração com pipelines de teste (usando Pytest)
- Geração de datasets sintéticos
- Monitoramento em produção
- Ideal para benchmarking de respostas
- Comparações de versões de modelo
- Avaliação nitidamente detalhada

**Recursos:**
- [GitHub](https://github.com/confident-ai/deepeval)
- [DEV Community](https://dev.to/confident-ai)
- [Documentação](https://docs.confident-ai.com/)

### AgentEval
Foi criado especificamente para avaliar agentes baseados em LLMs, ou seja, sistemas que realizam:
- Tarefas compostas
- Uso de ferramentas
- Raciocínio de múltiplos passos
- Autonomia

**Arquitetura:**
- **CriticAgent**: Estrutura critérios de avaliação
- **QuantifierAgent**: Quantifica métricas
- **VerifierAgent**: Verifica resultados

**Foco:**
- Medir desempenho em tarefas específicas
- Eficiência
- Completude
- Uso correto de ferramentas

**Recursos:**
- [Medium](https://medium.com/@confident-ai)
- [Blog Incubyte](https://blog.incubyte.co/)
- [Confident AI](https://confident-ai.com/) (fonte original Microsoft)

## Quando Usar Cada Ferramenta

| Situação | O que usar |
|----------|------------|
| **Você quer medir respostas isoladas** (fidelidade, precisão, coerência) | Use **DeepEval** |
| **Você quer medir o desempenho de um agente completo** (workflow, uso de ferramentas, planejamento) | Use **AgentEval** |
| **Quer testar qualidade de cada componente do agente e também resultados finais** | Combine ambos: ***DeepEval*** avalia as saídas e comportamentos, enquanto ***AgentEval*** monitora o fluxo do agente como um todo |



# Arquitetura orientada a perfis (profile-specific)

| Tipo de Fluxo         | Exemplo                                 | Características-chave                                         | Métricas relevantes                       |
| --------------------- | --------------------------------------- | ------------------------------------------------------------- | ----------------------------------------- |
| 🔁 Agent-based        | LangGraph com múltiplos nós             | Histórico com `intermediate_steps`, `tool_calls`, `state`     | `Trajectory Fidelity`, `Tool Usage`, etc. |
| 💬 LLM pura (Chat)    | Input simples + Output                  | Apenas `input`, `output`                                      | `Faithfulness`, `Correctness`, `Toxicity` |
| 📚 RAG                | Retrieval + Answer                      | Input com contexto + documentos recuperados + resposta gerada | `Context Recall`, `Answer Groundedness`   |
| 🛠️ Tool-calling LLMs | Modelos que chamam ferramentas via JSON | Contêm `tool_calls` e `tool_results` explícitos               | `Tool Usage Accuracy`, `Correctness`      |


## ETAPAS


| Etapa                     | Arquivo                                            |
| ------------------------- | -------------------------------------------------- |
| 📥 Extração de traces     | `evaluations/ingestion/extract_traces.py`          |
| 🧼 Limpeza & Anonimização | `evaluations/preprocessing/clean_and_format.py`    |
| 📊 Criação do Dataset     | `evaluations/datasets/build_evaluation_set.py`     |
| Dataset Builder (agentic) | `evaluations/datasets/builders/agentic_builder.py` |


### Avaliação
| Etapa                                     | Sugestão de Path                                | Observações                                                 |
| ----------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------- |
| 🧠 Execução de Métricas perfil-specific   | `evaluations/evaluators/runner.py`              | Executor central que chama os avaliadores conforme o perfil |
| 🧩 Trajectory Fidelity                    | `evaluations/evaluators/trajectory_fidelity.py` | Métrica específica para agentes                             |
| 🛠 Tool Usage Relevance                   | `evaluations/evaluators/tool_usage.py`          | Métrica baseada nas tool calls usadas                       |
| 🧾 Faithfulness / Relevance / Correctness | `evaluations/evaluators/semantic_metrics.py`    | Pode usar DeepEval ou LangSmith                             |


```bash
evaluations/
├── evaluators/
│   ├── __init__.py
│   ├── evaluator_registry.py       ✅
│   ├── run_evaluations.py          ✅
│   ├── base.py                     ✅ Interface base
│   ├── trajectory_fidelity.py      🔄 Agentic only
│   ├── tool_usage_relevance.py     🔄 Agentic + RAG
│   ├── faithfulness.py             🔄 Todos
│   ├── correctness.py              🔄 Todos
│   ├── relevance.py                🔄 Todos
│   └── hallucination_detection.py  🧪 Opcional avançado
```

```bash
python evaluations/evaluators/run_evaluations.py \
  --dataset_name="fincoder_agentic_v1" \
  --dataset_profile="agentic" \
  --project_name="agent_eval_2025" \
  --tags="['evaluation','v1']"
```

#### Métricas & Avaliadores
| Arquivo                      | Descrição                                                               | Fluxos Aplicáveis       | Integração no Diagrama            |
| ---------------------------- | ----------------------------------------------------------------------- | ----------------------- | --------------------------------- |
| `trajectory_fidelity.py`     | Avalia se os agentes seguiram a trajetória esperada (nodes, transições) | `agentic`               | `🧩 Trajectory Fidelity`          |
| `tool_usage_relevance.py`    | Verifica se ferramentas chamadas eram relevantes para o objetivo        | `agentic`, `rag`        | `🛠 Tool Usage Relevance`         |
| `faithfulness.py`            | Verifica se a resposta está alinhada com a fonte/contexto               | `rag`, `llm_io`, `chat` | `🧾 Faithfulness`                 |
| `correctness.py`             | Compara resposta gerada com ground-truth para exatidão factual          | `llm_io`, `chat`        | `🧾 Correctness`                  |
| `relevance.py`               | Verifica se a resposta é relevante à pergunta                           | `chat`, `llm_io`, `rag` | `🧾 Relevance`                    |
| `hallucination_detection.py` | Detecta possíveis alucinações com base no contexto fornecido            | `rag`, `chat`           | `🧾 Faithfulness / Hallucination` |


##### `trajectory_fidelity`
1. DeepEval (GitHub - langchain-ai/deepeval)
Métrica análoga: Step Consistency, Step Correctness ou Sequential Coherence.

Estado atual: o DeepEval não tem uma métrica explícita chamada trajectory_fidelity, mas oferece ferramentas para testes por step, que podem ser adaptadas.

Recomendação: se deseja seguir com DeepEval, você terá que criar um CustomEvaluator usando as etapas (steps) dos agentes.

🔧 Exemplo (não pronto, só base):

```python
from deepeval.metrics.step_consistency import StepConsistencyMetric
metric = StepConsistencyMetric()
```


###  Seleção e Decisão

| Etapa                           | Sugestão de Path                                    | Observações                             |
| ------------------------------- | --------------------------------------------------- | --------------------------------------- |
| 🔍 Seleção de exemplos críticos | `evaluations/selection/select_critical_examples.py` | LLM + heurística                        |
| ⚙️ Verifica thresholds          | `evaluations/selection/evaluate_thresholds.py`      | Decide se segue para refinamento ou não |

### Fine-Tuning

| Etapa                          | Sugestão de Path                       | Observações                                  |
| ------------------------------ | -------------------------------------- | -------------------------------------------- |
| Preparação/Filtro Fine-Tuning  | `evaluations/finetune/prepare_data.py` | Extrai exemplos relevantes e formata para FT |
| Envio para FT (ex: OpenAI API) | `evaluations/finetune/run_finetune.py` | Possivelmente externo                        |

###  MetaPrompting (Subflow)

| Etapa                                  | Sugestão de Path                                         | Observações                    |
| -------------------------------------- | -------------------------------------------------------- | ------------------------------ |
| Template Base + Exemplos               | `evaluations/prompt_tuning/templates/base_prompt.jinja2` | Prompt principal com slots     |
| Refinamento via LLM                    | `evaluations/prompt_tuning/metaprompt_llm.py`            | Chamada LLM para reescrita     |
| Validação estrutural do novo prompt    | `evaluations/prompt_tuning/validate_prompt.py`           | Pode usar AST/XML ou LangSmith |
| Avaliação automática dos novos prompts | Reaproveita `evaluators/runner.py`                       | Retesta os prompts gerados     |


### Deploy & Versionamento

| Etapa                         | Sugestão de Path                             | Observações                      |
| ----------------------------- | -------------------------------------------- | -------------------------------- |
| Implantação de prompts        | `evaluations/prompt_tuning/deploy_prompt.py` | Usa LangSmith Hub                |
| Teste de Regressão pós-deploy | `evaluations/tests/post_deploy_test.py`      | Executa dataset antigo e compara |
| Registro & Promoção           | `evaluations/registry/promote_version.py`    | Atualiza versão oficial          |

