# evaluations/datasets/builders/__init__.py

"""
Clean Dataset Builder for LangGraph + DeepEval/AgentEvals

Core Interface:
- build_dataset() - Single unified interface with maximum flexibility
  - framework: "deepeval" or "agentevals"
  - config_name: "agentic", "trajectory", "tool_use"
  - tags: Filter by agent tags ["Alice-Agent", "main-swarm"]
- GenericDatasetBuilder - Core implementation

LangGraph traces work directly with DeepEval/AgentEvals without transformation.
"""

from .generic_builder import (
    GenericDatasetBuilder,
    DatasetConfig,
    EvaluationFramework,
    build_dataset
)

__all__ = [
    # Core Interface (Essential)
    "build_dataset",
    
    # Core Classes
    "GenericDatasetBuilder",
    "DatasetConfig", 
    "EvaluationFramework"
]
