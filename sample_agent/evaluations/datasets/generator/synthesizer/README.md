# Synthetic Data Generation Architecture

## Overview

This directory contains a unified synthetic data generation framework with two complementary strategies:

1. **BaseSynthesizer** (`base.py`) - Abstract base class with unified interface and common functionality
2. **CustomSynthesizer** (`custom.py`) - Real workflow execution with automatic structure analysis  
3. **DeepEvalSynthesizer** (`deepeval_synthesizer.py`) - LLM-based synthetic data generation

## Key Features

- 🔗 **Unified Interface**: All synthesizers inherit from `BaseSynthesizer` with consistent API
- 🔍 **Universal Workflow Analysis**: Both synthesizers can analyze workflow structure for better generation
- 🏷️ **Dynamic Tagging**: Intelligent tagging system for LangSmith filtering and organization
- 📊 **Standardized Output**: Consistent format across all synthesizers
- 💾 **Agnostic Persistence**: Provider-agnostic persistence layer (LangSmith by default)
- 🚀 **Zero Configuration**: No manual dataset management - automatic tracing and persistence

## Architecture Comparison

| Feature | CustomSynthesizer | DeepEvalSynthesizer |
|---------|-------------------|---------------------|
| **Base Class** | Inherits from `BaseSynthesizer` | Inherits from `BaseSynthesizer` |
| **Execution Modes** | **DUAL**: SYNTHETIC + EXECUTION | Single mode (LLM generation) |
| **Workflow Analysis** | ✅ Required (automatic) | ✅ Optional (enhances generation) |
| **SYNTHETIC Mode** | Workflow analysis + LLM generation (no execution) | N/A |
| **EXECUTION Mode** | Workflow analysis + real execution + traces | N/A |
| **Data Source** | Mode-dependent: Synthetic vs Real execution | Workflow analysis + LLM generation |
| **Persistence** | Auto-tracing (EXECUTION) / Manual (SYNTHETIC) | Manual persistence to LangSmith |
| **Tagging** | Dynamic tags with mode identification | Dynamic tags enhanced by workflow analysis |
| **Use Case** | **Flexible**: Rapid generation OR System validation | Rapid dataset generation |

## CustomSynthesizer Dual Execution Modes

The CustomSynthesizer offers two distinct execution modes for different use cases:

### 🎭 SYNTHETIC Mode
**Purpose**: Generate synthetic datasets from workflow analysis without execution

**Process**:
1. **Workflow Analysis**: Extracts agents, tools, capabilities, and structure
2. **Scenario Generation**: Creates realistic test scenarios based on analysis
3. **LLM Synthesis**: Generates synthetic responses simulating workflow behavior
4. **No Execution**: Never runs the actual workflow

**Use Cases**:
- Rapid dataset creation for training/benchmarking
- Testing dataset generation without infrastructure requirements
- Baseline dataset creation before real system testing
- Understanding workflow capabilities without execution overhead

```python
# SYNTHETIC mode usage
synthesizer = CustomSynthesizer(config, mode=ExecutionMode.SYNTHETIC)
examples = await synthesizer.generate_synthetic_dataset(workflow=my_workflow)
# Result: Synthetic data based on workflow analysis (no real execution)
```

### 🚀 EXECUTION Mode  
**Purpose**: Generate scenarios and execute real workflows for trace collection

**Process**:
1. **Workflow Analysis**: Extracts structure for intelligent scenario generation
2. **Scenario Generation**: Creates test scenarios targeting workflow capabilities  
3. **Real Execution**: Executes actual workflow for each scenario
4. **Trace Collection**: Captures real execution traces and results

**Use Cases**:
- System validation and integration testing
- Performance benchmarking with real execution
- Production-quality dataset generation
- End-to-end workflow verification

```python
# EXECUTION mode usage  
synthesizer = CustomSynthesizer(config, mode=ExecutionMode.EXECUTION)
examples = await synthesizer.generate_synthetic_dataset(workflow=my_workflow)
# Result: Real execution traces from actual workflow runs
```

### Mode Selection Strategy

| Scenario | Recommended Mode | Rationale |
|----------|------------------|-----------|
| **Initial Development** | SYNTHETIC | Fast iteration without infrastructure |
| **Rapid Prototyping** | SYNTHETIC | Quick dataset generation for experimentation |
| **System Validation** | EXECUTION | Real traces for accurate testing |
| **Performance Testing** | EXECUTION | Actual execution metrics needed |
| **Production Datasets** | EXECUTION | Real-world execution patterns |
| **Training Data** | SYNTHETIC | Large-scale generation without costs |

## Automatic Workflow Analysis

Both modes leverage automatic workflow structure analysis:

```python
workflow_context = synthesizer.analyze_workflow_structure(workflow)
# Extracts:
# - Agent names and capabilities
# - Available tools
# - State schema
# - Node relationships
# - Prompt information
```

This analysis drives intelligent scenario generation:
- **Agent-specific scenarios**: Tests each agent's capabilities
- **Tool usage patterns**: Exercises different tools
- **Complexity levels**: From simple to edge cases
- **Realistic interactions**: Based on actual workflow structure

## Standardized Output Format

Both synthesizers generate datasets with consistent structure:

```json
{
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "assistant", "content": "...", "tool_calls": [...] }
  ],
  "custom_state_data": {...}
}
```

Where `custom_state_data` contains workflow-specific state information extracted during execution.

## Dynamic Tagging Strategy

### CustomSynthesizer Tags
- `complexity:simple|medium|complex|edge`
- `scenario:{scenario_id}`
- `agent:{agent_name}` (for each involved agent)
- `tool:{tool_name}` (for each used tool)
- Custom tags from configuration

### DeepEvalSynthesizer Tags
- `generator:deepeval`
- `example:{number}`
- `synthetic:generated`
- Custom tags from configuration

## Strategy Complementarity

### CustomSynthesizer
- **Purpose**: Generate datasets from real system execution with workflow intelligence
- **Strengths**: 
  - Automatic context generation from workflow structure
  - Real traces with operational metrics
  - Agent-aware scenario generation
- **Best for**: System validation, integration testing, workflow verification

### DeepEvalSynthesizer  
- **Purpose**: Generate large-scale synthetic datasets quickly
- **Strengths**: 
  - Fast generation without infrastructure requirements
  - Diverse scenarios through LLM creativity
  - Configurable output formats
- **Best for**: Initial dataset creation, benchmark generation, rapid prototyping

## Usage Patterns

### Unified Interface

Both synthesizers follow the same interface:

```python
from .base import BaseSynthesizer
from .custom import CustomSynthesizer
from .deepeval_synthesizer import DeepEvalSynthesizer

# All synthesizers have consistent API
synthesizer: BaseSynthesizer = CustomSynthesizer(config)
# or
synthesizer: BaseSynthesizer = DeepEvalSynthesizer(config)

# Unified generation method
examples = await synthesizer.generate_synthetic_dataset(
    workflow=my_workflow,  # Optional for DeepEval, Required for Custom
    num_scenarios=20
)
```

### CustomSynthesizer (Dual Modes)
```python
# SYNTHETIC mode: Workflow analysis + LLM generation (no execution)
synthesizer = CustomSynthesizer(config, mode=ExecutionMode.SYNTHETIC)
examples = await synthesizer.generate_synthetic_dataset(workflow=my_workflow)

# EXECUTION mode: Workflow analysis + real execution + traces
synthesizer = CustomSynthesizer(config, mode=ExecutionMode.EXECUTION) 
examples = await synthesizer.generate_synthetic_dataset(workflow=my_workflow)

# Default mode is EXECUTION
synthesizer = CustomSynthesizer(config)  # mode=ExecutionMode.EXECUTION
examples = await synthesizer.generate_synthetic_dataset(workflow=my_workflow)
```

### DeepEvalSynthesizer (LLM Generation)
```python
# Workflow is optional but enhances generation
synthesizer = DeepEvalSynthesizer(config)

# Without workflow (generic generation)
examples = await synthesizer.generate_synthetic_dataset(num_scenarios=10)

# With workflow (enhanced generation)
examples = await synthesizer.generate_synthetic_dataset(
    workflow=my_workflow,  # Optional: enhances generation quality
    num_scenarios=10
)
```

### Combined Approach
1. Use **DeepEvalSynthesizer** for baseline dataset generation
2. Use **CustomSynthesizer** for validation with real execution  
3. Both can use workflow analysis for better generation
4. Compare outputs using LangSmith tag filtering

## Configuration

Both synthesizers use `SynthesizerConfig`:

```python
config = SynthesizerConfig(
    project_name="my-project",           # LangSmith project
    tags=["synthetic", "evaluation"],    # Base tags
    trace_metadata={"env": "test"},       # Additional metadata
    num_scenarios=20                     # Number of examples
)
```

## LangSmith Integration

### Automatic Tracing
- No manual dataset creation required
- All executions automatically traced to configured project
- Dynamic tags applied for intelligent filtering
- Rich metadata captured with each trace

### Filtering Examples
```python
# Filter by complexity in LangSmith
tags: ["complexity:complex"]

# Filter by agent involvement
tags: ["agent:alice_agent", "agent:bob_agent"]

# Filter by generation method
tags: ["generator:deepeval"] or ["execution_type:custom_synthesizer"]
```

## Example Usage

```python
# Unified interface for all synthesizers
from .base import BaseSynthesizer
from .custom import CustomSynthesizer, ExecutionMode
from .deepeval_synthesizer import DeepEvalSynthesizer

# CustomSynthesizer - SYNTHETIC mode (analysis + LLM generation, no execution)
synthesizer = CustomSynthesizer(config, mode=ExecutionMode.SYNTHETIC)
synthetic_examples = await synthesizer.generate_synthetic_dataset(workflow=my_workflow)

# CustomSynthesizer - EXECUTION mode (analysis + real execution + traces)  
synthesizer = CustomSynthesizer(config, mode=ExecutionMode.EXECUTION)
execution_examples = await synthesizer.generate_synthetic_dataset(workflow=my_workflow)

# DeepEvalSynthesizer with optional workflow analysis
synthesizer = DeepEvalSynthesizer(config)
deepeval_examples = await synthesizer.generate_synthetic_dataset(
    workflow=my_workflow,  # Optional: enhances generation
    num_scenarios=10
)

# Provider-agnostic persistence
await synthesizer.persist_dataset(examples)

# All examples automatically traced/persisted to LangSmith with dynamic tags
```

## Key Benefits

- **Unified Interface**: Consistent API across all synthesizers following solid design principles
- **Dual Execution Modes**: CustomSynthesizer supports both synthetic generation and real execution
- **Universal Workflow Analysis**: All synthesizers leverage workflow structure for intelligent generation
- **Zero Manual Work**: No context description needed - workflow analysis is automatic
- **Flexible Use Cases**: Choose between rapid generation (SYNTHETIC) or system validation (EXECUTION)
- **Intelligent Scenarios**: Generated scenarios match actual workflow capabilities  
- **Provider-Agnostic Persistence**: Pluggable persistence layer (LangSmith by default)
- **Rich Tracing**: Every execution captured with relevant metadata and tags
- **Mode-Aware Tagging**: Dynamic tags include execution mode for sophisticated filtering
- **Easy Filtering**: Dynamic tags enable sophisticated LangSmith queries
- **Scalable**: Works with any `CompiledStateGraph` or `Runnable` 