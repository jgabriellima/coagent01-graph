# Generic Dataset Builders for LangGraph + DeepEval/AgentEvals

## Overview

This refactored implementation provides a **generic, configurable** dataset builder system optimized for:
- **LangGraph** agents (basic, supervisor, swarm)
- **DeepEval** evaluation framework
- **AgentEvals** trajectory evaluation
- **LangSmith** traces and datasets

## Key Improvements

### ✅ Problems Solved
- **No more redundancy**: Single generic builder with configurations
- **LangGraph compatible**: Handles `create_react_agent` (no intermediate_steps)
- **Framework optimized**: Pre-configured for DeepEval/AgentEvals requirements
- **Flexible**: Easy to extend without changing evaluation process

### 🏗️ Architecture

```
GenericDatasetBuilder
├── DatasetConfig (configurable)
├── Transform Functions (custom logic)
└── Framework Adapters (DeepEval/AgentEvals)
```

## Quick Start

### 1. Basic Usage (New Interface)

```python
from evaluations.datasets.builders import build_dataset

# For DeepEval evaluation
dataset_id = build_dataset(
    project_name="my-langgraph-project",
    dataset_name="react_evaluation",
    framework="deepeval",
    config_name="agentic"
)
```

### 2. Tag-Based Filtering

```python
from evaluations.datasets.builders import build_dataset

# Agent-specific evaluation
dataset_id = build_dataset(
    project_name="swarm-project",
    dataset_name="alice_eval",
    tags=["Alice-Agent"]
)

# System-wide evaluation
dataset_id = build_dataset(
    project_name="swarm-project",
    dataset_name="swarm_eval",
    tags=["main-swarm"]
)
```

### 3. Trajectory Evaluation (AgentEvals)

```python
from evaluations.datasets.builders import build_dataset

dataset_id = build_dataset(
    project_name="my-project",
    dataset_name="trajectory_eval",
    framework="agentevals",
    config_name="trajectory",
    tags=["main-swarm"]
)
```

## Available Builders

### Recommended (New)
- `build_react_agent_dataset` - Optimized for create_react_agent
- `build_for_deepeval` - Generic DeepEval datasets
- `build_for_agentevals` - Generic AgentEvals datasets  
- `build_for_langgraph` - Configurable LangGraph datasets

### Legacy (Deprecated)
- `build_agentic_dataset` - Old agentic builder
- `build_llm_io_dataset` - Simple LLM I/O
- `build_chat_dataset` - Multi-turn chat
- `build_rag_dataset` - RAG evaluation

## Custom Configuration

```python
from evaluations.datasets.builders import DatasetConfig, EvaluationFramework, GenericDatasetBuilder

# Custom config
config = DatasetConfig(
    framework=EvaluationFramework.DEEPEVAL,
    input_fields=["input", "messages"],
    output_fields=["output", "tool_calls"],
    metadata_fields=["execution_time", "tools_used"],
    filter_tags=["production", "agent"],
    run_type="chain"
)

# Use custom config
builder = GenericDatasetBuilder()
dataset_id = builder.build_dataset(
    project_name="my-project",
    dataset_name="custom_eval",
    config=config
)
```

## Migration from Legacy

### Before (Old Way)
```python
from evaluations.datasets.builders.agentic_builder import build_agentic_dataset

# Assumed specific trace structure
dataset_id = build_agentic_dataset(traces, "dataset_name")
```

### After (New Way)
```python
from evaluations.datasets.builders import build_for_deepeval

# Generic, configurable
dataset_id = build_for_deepeval(
    project_name="my-project",
    dataset_name="dataset_name",
    config_type="agentic"
)
```

## Benefits

1. **Less Code**: Single generic builder vs multiple specific ones
2. **More Flexible**: Easy to configure without changing evaluation logic
3. **LangGraph Native**: Properly handles LangGraph trace structure
4. **Tool Framework Ready**: Pre-configured for DeepEval/AgentEvals
5. **Maintainable**: Add new configurations without touching core logic

## Example Usage

See `usage_example.py` for complete examples of all features. 