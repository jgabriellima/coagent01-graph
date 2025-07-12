# sample_agent/evaluations/evaluators/evaluator_registry.py
from typing import Dict, List, Optional
from .base import BaseEvaluator

# Import all implemented evaluators here
from .trajectory_fidelity import TrajectoryFidelityEvaluator
from .tool_usage_relevance import ToolUsageRelevanceEvaluator
from .faithfulness import FaithfulnessEvaluator
from .correctness import CorrectnessEvaluator
from .relevance import RelevanceEvaluator
from .hallucination_detection import HallucinationDetectionEvaluator

# Auto-discovery of evaluators using reflection
ALL_EVALUATORS = {
    cls.__name__: cls
    for cls in [
        TrajectoryFidelityEvaluator,
        ToolUsageRelevanceEvaluator,
        FaithfulnessEvaluator,
        CorrectnessEvaluator,
        RelevanceEvaluator,
        HallucinationDetectionEvaluator,
    ]
}

# Profile configurations - comprehensive evaluation per profile
EVALUATOR_PROFILES = {
    "agentic": [
        "TrajectoryFidelityEvaluator",
        "ToolUsageRelevanceEvaluator",
        "FaithfulnessEvaluator",
        "RelevanceEvaluator",
        "CorrectnessEvaluator",
        "HallucinationDetectionEvaluator",
    ],
    "chat": [
        "FaithfulnessEvaluator",
        "RelevanceEvaluator",
        "CorrectnessEvaluator",
        "HallucinationDetectionEvaluator",
    ],
    "llm_io": [
        "FaithfulnessEvaluator",
        "RelevanceEvaluator",
        "CorrectnessEvaluator",
    ],
    "rag": [
        "ToolUsageRelevanceEvaluator",
        "FaithfulnessEvaluator",
        "RelevanceEvaluator",
        "CorrectnessEvaluator",
        "HallucinationDetectionEvaluator",
    ],
}


def get_evaluators_for_profile(
    profile_type: str, **evaluator_kwargs
) -> List[BaseEvaluator]:
    """
    Instantiate evaluators for a given profile.

    Args:
        profile_type: Profile type ('agentic', 'chat', 'llm_io', 'rag')
        **evaluator_kwargs: Arguments for evaluator constructors

    Returns:
        List of instantiated evaluator objects
    """
    if profile_type not in EVALUATOR_PROFILES:
        raise ValueError(
            f"Unknown profile: {profile_type}. Available: {list(EVALUATOR_PROFILES.keys())}"
        )

    evaluator_names = EVALUATOR_PROFILES[profile_type]
    evaluators = []

    for name in evaluator_names:
        try:
            evaluator_class = ALL_EVALUATORS[name]
            evaluator = evaluator_class(**evaluator_kwargs)
            evaluators.append(evaluator)
        except Exception as e:
            print(f"Warning: Failed to instantiate {name}: {e}")
            continue

    return evaluators


def get_evaluator_by_name(evaluator_name: str, **kwargs) -> BaseEvaluator:
    """Get an evaluator instance by name."""
    if evaluator_name not in ALL_EVALUATORS:
        raise ValueError(
            f"Unknown evaluator: {evaluator_name}. Available: {list(ALL_EVALUATORS.keys())}"
        )

    evaluator_class = ALL_EVALUATORS[evaluator_name]
    return evaluator_class(**kwargs)


def get_available_profiles() -> List[str]:
    """Get list of available evaluation profiles."""
    return list(EVALUATOR_PROFILES.keys())


def get_available_evaluators() -> Dict[str, List[str]]:
    """Get mapping of profiles to available evaluator names."""
    return EVALUATOR_PROFILES.copy()


def validate_evaluator_configuration(profile_type: str) -> bool:
    """Validate that all evaluators for a profile can be instantiated."""
    try:
        evaluators = get_evaluators_for_profile(profile_type)
        return len(evaluators) > 0
    except Exception as e:
        print(f"Validation failed for profile '{profile_type}': {e}")
        return False


# Example usage:
# evaluators = get_evaluators_for_profile("agentic")
# evaluator = get_evaluator_by_name("FaithfulnessEvaluator")
