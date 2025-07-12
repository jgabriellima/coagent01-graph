# evaluations/datasets/build_evaluation_set.py

from typing import List, Dict, Any
from .builders.builder_registry import get_builder_by_type


def build_dataset(dataset_type: str, project_name: str) -> List[Dict[str, Any]]:
    """
    Build an evaluation dataset using the builder associated with the dataset type.

    Args:
        dataset_type (str): One of 'agentic', 'llm_io', 'chat', 'rag'
        project_name (str): LangSmith project to scan.

    Returns:
        List[Dict]: Dataset ready for evaluation.
    """
    builder = get_builder_by_type(dataset_type)
    return builder(project_name)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Build evaluation dataset.")
    parser.add_argument(
        "--type", required=True, help="Dataset type: agentic, llm_io, chat, rag"
    )
    parser.add_argument("--project", required=True, help="LangSmith project name")
    parser.add_argument(
        "--output", default="dataset.json", help="Path to output JSON file"
    )
    args = parser.parse_args()

    dataset = build_dataset(args.type, args.project)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"✅ Dataset built with {len(dataset)} examples. Saved to {args.output}")
