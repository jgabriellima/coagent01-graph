"""
Synthetic Data Generation
------------------------

Unified interface for synthetic data generation:
- BaseSynthesizer: Abstract base class with common functionality
- CustomSynthesizer: Real execution with automatic workflow analysis
- DeepEvalSynthesizer: LLM-based synthetic data generation

Both synthesizers support workflow analysis and automatic persistence to LangSmith.
"""

from .base import BaseSynthesizer, SynthesizerConfig, SyntheticExample, DatasetPersistence, LangSmithPersistence
from .custom import CustomSynthesizer, ExecutionMode
from .deepeval_synthesizer import DeepEvalSynthesizer

__all__ = [
    "BaseSynthesizer",
    "CustomSynthesizer",
    "ExecutionMode",
    "DeepEvalSynthesizer",
    "SynthesizerConfig", 
    "SyntheticExample",
    "DatasetPersistence",
    "LangSmithPersistence"
] 