# evaluations/datasets/builders/rag_builder.py

from typing import List, Dict, Any
from langsmith import Client


def build_rag_dataset(
    project_name: str, tag_filter: str = "rag"
) -> List[Dict[str, Any]]:
    """
    Build dataset for RAG-style evaluation.
    Example: question + context -> answer

    Args:
        project_name (str): LangSmith project name.
        tag_filter (str): Filter tag to select relevant traces.

    Returns:
        List[Dict]: List of samples with {query, context, expected_answer}
    """
    client = Client()
    runs = client.list_runs(project_name=project_name, run_type="chain")

    dataset = []

    for run in runs:
        if tag_filter not in run.tags:
            continue

        query = run.inputs.get("query") or run.inputs.get("question")
        context = run.inputs.get("context") or run.inputs.get("documents")
        answer = run.outputs.get("output") or run.outputs

        dataset.append({"query": query, "context": context, "expected_answer": answer})

    return dataset
