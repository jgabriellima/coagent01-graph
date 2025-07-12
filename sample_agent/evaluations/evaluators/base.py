# evaluations/evaluators/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseEvaluator(ABC):
    """Abstract class for all evaluators."""

    @abstractmethod
    def name(self) -> str:
        """Returns the name of the evaluation metric."""
        pass

    @abstractmethod
    def applicable_profiles(self) -> List[str]:
        """Returns which dataset profiles this evaluator supports (e.g., ['agentic', 'rag'])"""
        pass

    @abstractmethod
    def evaluate(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single example. Returns evaluation metadata to be added to the example."""
        pass
