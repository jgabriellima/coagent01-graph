# evaluations/datasets/builders/builder_registry.py

from typing import Callable, Dict, List, Any

from .agentic_builder import build_agentic_dataset
from .llm_io_builder import build_llm_io_dataset
from .chat_builder import build_chat_dataset
from .rag_builder import build_rag_dataset


DATASET_BUILDERS: Dict[str, Callable[[str], List[Dict[str, Any]]]] = {
    "agentic": build_agentic_dataset,
    "llm_io": build_llm_io_dataset,
    "chat": build_chat_dataset,
    "rag": build_rag_dataset,
}


def get_builder_by_type(dataset_type: str) -> Callable[[str], List[Dict[str, Any]]]:
    """
    Retrieve the dataset builder based on the type.

    Args:
        dataset_type (str): One of 'agentic', 'llm_io', 'chat', 'rag'

    Returns:
        Callable: The corresponding builder function

    Raises:
        ValueError: If the type is unknown or not registered.
    """
    try:
        return DATASET_BUILDERS[dataset_type]
    except KeyError:
        raise ValueError(
            f"Unknown dataset type: '{dataset_type}'. Available types: {list(DATASET_BUILDERS.keys())}"
        )
