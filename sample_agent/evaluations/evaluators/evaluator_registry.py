# sample_agent/evaluations/evaluators/evaluator_registry.py
from typing import Dict, List, Type
from .base import BaseEvaluator

# Import all implemented evaluators here
from .trajectory_fidelity import TrajectoryFidelityEvaluator
from .tool_usage_relevance import ToolUsageRelevanceEvaluator
from .faithfulness import FaithfulnessEvaluator
from .correctness import CorrectnessEvaluator
from .relevance import RelevanceEvaluator
from .hallucination_detection import HallucinationDetectionEvaluator


# Profile types correspond to dataset builders
PROFILE_AGENTIC = "agentic"
PROFILE_CHAT = "chat"
PROFILE_LLM_IO = "llm_io"
PROFILE_RAG = "rag"

# Map of which evaluators to run per profile - Production-grade configuration
EVALUATOR_REGISTRY: Dict[str, List[Type[BaseEvaluator]]] = {
    PROFILE_AGENTIC: [
        TrajectoryFidelityEvaluator,     # Evaluates agent trajectory coherence and effectiveness
        ToolUsageRelevanceEvaluator,     # Evaluates tool selection and usage appropriateness
        FaithfulnessEvaluator,           # Evaluates factual alignment with context
        RelevanceEvaluator,              # Evaluates response relevance to input
        CorrectnessEvaluator,            # Evaluates correctness vs expected output
    ],
    PROFILE_CHAT: [
        FaithfulnessEvaluator,           # Evaluates factual consistency
        RelevanceEvaluator,              # Evaluates response relevance
        CorrectnessEvaluator,            # Evaluates correctness of responses
        HallucinationDetectionEvaluator, # Detects hallucinations in responses
    ],
    PROFILE_LLM_IO: [
        FaithfulnessEvaluator,           # Evaluates factual alignment
        RelevanceEvaluator,              # Evaluates response relevance
        CorrectnessEvaluator,            # Evaluates correctness vs expected
    ],
    PROFILE_RAG: [
        ToolUsageRelevanceEvaluator,     # Evaluates retrieval tool usage (if applicable)
        FaithfulnessEvaluator,           # Evaluates grounding in retrieved context
        RelevanceEvaluator,              # Evaluates response relevance to query
        CorrectnessEvaluator,            # Evaluates correctness vs expected
        HallucinationDetectionEvaluator, # Detects context-unsupported claims
    ],
}

# Alternative profile configurations for different evaluation scenarios
# Minimal evaluation set for fast feedback during development
EVALUATOR_REGISTRY_MINIMAL: Dict[str, List[Type[BaseEvaluator]]] = {
    PROFILE_AGENTIC: [
        TrajectoryFidelityEvaluator,
        ToolUsageRelevanceEvaluator,
    ],
    PROFILE_CHAT: [
        RelevanceEvaluator,
        CorrectnessEvaluator,
    ],
    PROFILE_LLM_IO: [
        CorrectnessEvaluator,
    ],
    PROFILE_RAG: [
        FaithfulnessEvaluator,
        HallucinationDetectionEvaluator,
    ],
}

# Comprehensive evaluation set for thorough analysis
EVALUATOR_REGISTRY_COMPREHENSIVE: Dict[str, List[Type[BaseEvaluator]]] = {
    PROFILE_AGENTIC: [
        TrajectoryFidelityEvaluator,
        ToolUsageRelevanceEvaluator,
        FaithfulnessEvaluator,
        RelevanceEvaluator,
        CorrectnessEvaluator,
        HallucinationDetectionEvaluator,
    ],
    PROFILE_CHAT: [
        FaithfulnessEvaluator,
        RelevanceEvaluator,
        CorrectnessEvaluator,
        HallucinationDetectionEvaluator,
    ],
    PROFILE_LLM_IO: [
        FaithfulnessEvaluator,
        RelevanceEvaluator,
        CorrectnessEvaluator,
    ],
    PROFILE_RAG: [
        ToolUsageRelevanceEvaluator,
        FaithfulnessEvaluator,
        RelevanceEvaluator,
        CorrectnessEvaluator,
        HallucinationDetectionEvaluator,
    ],
}


def get_evaluators_for_profile(
    profile_type: str, 
    registry_type: str = "default",
    **evaluator_kwargs
) -> List[BaseEvaluator]:
    """
    Instantiate all evaluators applicable to a given profile.
    
    Args:
        profile_type: The type of dataset profile ('agentic', 'chat', 'llm_io', 'rag')
        registry_type: Type of evaluator registry to use ('default', 'minimal', 'comprehensive')
        **evaluator_kwargs: Additional keyword arguments to pass to evaluator constructors
    
    Returns:
        List of instantiated evaluator objects
        
    Raises:
        ValueError: If profile_type or registry_type is not recognized
    """
    # Select the appropriate registry
    if registry_type == "minimal":
        registry = EVALUATOR_REGISTRY_MINIMAL
    elif registry_type == "comprehensive":
        registry = EVALUATOR_REGISTRY_COMPREHENSIVE
    elif registry_type == "default":
        registry = EVALUATOR_REGISTRY
    else:
        raise ValueError(f"Unknown registry type: {registry_type}. Available: 'default', 'minimal', 'comprehensive'")
    
    if profile_type not in registry:
        raise ValueError(f"Unknown profile type: {profile_type}. Available: {list(registry.keys())}")

    evaluators = []
    for evaluator_class in registry[profile_type]:
        try:
            # Instantiate evaluator with optional kwargs
            evaluator = evaluator_class(**evaluator_kwargs)
            evaluators.append(evaluator)
        except Exception as e:
            print(f"Warning: Failed to instantiate {evaluator_class.__name__}: {e}")
            continue
    
    return evaluators


def get_available_profiles() -> List[str]:
    """Get list of available evaluation profiles."""
    return list(EVALUATOR_REGISTRY.keys())


def get_available_evaluators() -> Dict[str, List[str]]:
    """Get mapping of profiles to available evaluator names."""
    result = {}
    for profile, evaluator_classes in EVALUATOR_REGISTRY.items():
        result[profile] = [evaluator_class.__name__ for evaluator_class in evaluator_classes]
    return result


def get_evaluator_by_name(evaluator_name: str, **kwargs) -> BaseEvaluator:
    """
    Get an evaluator instance by name.
    
    Args:
        evaluator_name: Name of the evaluator class
        **kwargs: Arguments to pass to evaluator constructor
        
    Returns:
        Instantiated evaluator
        
    Raises:
        ValueError: If evaluator name is not found
    """
    # Build name-to-class mapping
    name_to_class = {
        "TrajectoryFidelityEvaluator": TrajectoryFidelityEvaluator,
        "ToolUsageRelevanceEvaluator": ToolUsageRelevanceEvaluator,
        "FaithfulnessEvaluator": FaithfulnessEvaluator,
        "CorrectnessEvaluator": CorrectnessEvaluator,
        "RelevanceEvaluator": RelevanceEvaluator,
        "HallucinationDetectionEvaluator": HallucinationDetectionEvaluator,
    }
    
    if evaluator_name not in name_to_class:
        available = list(name_to_class.keys())
        raise ValueError(f"Unknown evaluator: {evaluator_name}. Available: {available}")
    
    evaluator_class = name_to_class[evaluator_name]
    return evaluator_class(**kwargs)


def validate_evaluator_configuration(profile_type: str, registry_type: str = "default") -> bool:
    """
    Validate that all evaluators for a profile can be instantiated.
    
    Args:
        profile_type: Profile to validate
        registry_type: Registry type to use
        
    Returns:
        True if all evaluators can be instantiated, False otherwise
    """
    try:
        evaluators = get_evaluators_for_profile(profile_type, registry_type)
        return len(evaluators) > 0
    except Exception as e:
        print(f"Validation failed for profile '{profile_type}': {e}")
        return False


def create_test_evaluator_suite(
    profile_type: str,
    model: str = "gpt-4o-mini",
    threshold: float = 0.5,
    async_mode: bool = True,
) -> List[BaseEvaluator]:
    """
    Create a test suite of evaluators for a specific profile.
    
    Args:
        profile_type: Profile to create evaluators for
        model: LLM model to use for evaluation
        threshold: Default threshold for pass/fail
        async_mode: Whether to enable async mode
        
    Returns:
        List of configured evaluators
    """
    evaluator_kwargs = {
        "model": model,
        "threshold": threshold,
        "async_mode": async_mode,
    }
    
    return get_evaluators_for_profile(profile_type, "default", **evaluator_kwargs)


def get_registry_metadata() -> Dict[str, Dict[str, List[str]]]:
    """
    Get metadata about all available registries.
    
    Returns:
        Dictionary with registry metadata
    """
    return {
        "default": get_available_evaluators(),
        "minimal": {
            profile: [cls.__name__ for cls in evaluator_classes]
            for profile, evaluator_classes in EVALUATOR_REGISTRY_MINIMAL.items()
        },
        "comprehensive": {
            profile: [cls.__name__ for cls in evaluator_classes]
            for profile, evaluator_classes in EVALUATOR_REGISTRY_COMPREHENSIVE.items()
        },
    }


class EvaluatorRegistry:
    """
    Object-oriented wrapper for evaluator registry functionality.
    
    This class provides a clean interface for managing and instantiating evaluators
    based on different profiles and registry types.
    """
    
    def __init__(self, default_registry_type: str = "default", **default_kwargs):
        """
        Initialize the evaluator registry.
        
        Args:
            default_registry_type: Default registry type to use
            **default_kwargs: Default arguments to pass to evaluator constructors
        """
        self.default_registry_type = default_registry_type
        self.default_kwargs = default_kwargs
        
        # Validate registry type
        if default_registry_type not in ["default", "minimal", "comprehensive"]:
            raise ValueError(f"Invalid registry type: {default_registry_type}")
    
    def get_evaluators(self, profile_type: str, registry_type: str = None, **kwargs) -> Dict[str, BaseEvaluator]:
        """
        Get evaluators for a specific profile as a dictionary.
        
        Args:
            profile_type: Profile to get evaluators for
            registry_type: Registry type to use (overrides default)
            **kwargs: Additional arguments to pass to evaluator constructors
            
        Returns:
            Dictionary mapping evaluator names to instances
        """
        # Use provided registry type or default
        registry_type = registry_type or self.default_registry_type
        
        # Merge default kwargs with provided kwargs
        evaluator_kwargs = {**self.default_kwargs, **kwargs}
        
        # Get evaluators as list
        evaluators_list = get_evaluators_for_profile(profile_type, registry_type, **evaluator_kwargs)
        
        # Convert to dictionary
        evaluators_dict = {}
        for evaluator in evaluators_list:
            evaluators_dict[evaluator.name()] = evaluator
        
        return evaluators_dict
    
    def get_evaluator_by_name(self, evaluator_name: str, **kwargs) -> BaseEvaluator:
        """
        Get a specific evaluator by name.
        
        Args:
            evaluator_name: Name of the evaluator
            **kwargs: Arguments to pass to evaluator constructor
            
        Returns:
            Evaluator instance
        """
        # Merge default kwargs with provided kwargs
        evaluator_kwargs = {**self.default_kwargs, **kwargs}
        
        return get_evaluator_by_name(evaluator_name, **evaluator_kwargs)
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available evaluation profiles."""
        return get_available_profiles()
    
    def get_available_evaluators(self) -> Dict[str, List[str]]:
        """Get mapping of profiles to available evaluator names."""
        return get_available_evaluators()
    
    def validate_profile(self, profile_type: str, registry_type: str = None) -> bool:
        """
        Validate that all evaluators for a profile can be instantiated.
        
        Args:
            profile_type: Profile to validate
            registry_type: Registry type to use (overrides default)
            
        Returns:
            True if all evaluators can be instantiated, False otherwise
        """
        registry_type = registry_type or self.default_registry_type
        return validate_evaluator_configuration(profile_type, registry_type)
    
    def create_test_suite(self, profile_type: str, **kwargs) -> Dict[str, BaseEvaluator]:
        """
        Create a test suite of evaluators for a specific profile.
        
        Args:
            profile_type: Profile to create evaluators for
            **kwargs: Additional arguments to pass to evaluator constructors
            
        Returns:
            Dictionary mapping evaluator names to instances
        """
        return self.get_evaluators(profile_type, **kwargs)
    
    def get_registry_metadata(self) -> Dict[str, Dict[str, List[str]]]:
        """Get metadata about all available registries."""
        return get_registry_metadata()
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"EvaluatorRegistry(default_registry_type='{self.default_registry_type}')"
