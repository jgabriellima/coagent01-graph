# evaluations/datasets/builders/chat_builder.py

from typing import List, Dict, Any
from langsmith import Client


def build_chat_dataset(
    project_name: str, tag_filter: str = "chat"
) -> List[Dict[str, Any]]:
    """
    Build dataset for multi-turn conversational evaluation.
    Example: [{role: 'user', content: ...}, {role: 'assistant', content: ...}, ...]

    Args:
        project_name (str): LangSmith project to scan.
        tag_filter (str): Optional tag to filter runs.

    Returns:
        List[Dict]: List of conversation histories and last assistant reply.
    """
    client = Client()
    runs = client.list_runs(project_name=project_name, run_type="chain")

    dataset = []

    for run in runs:
        if tag_filter not in run.tags:
            continue

        messages = run.inputs.get("messages", [])
        if not messages or not isinstance(messages, list):
            continue

        last_message = run.outputs.get("output") or run.outputs
        dataset.append({"history": messages, "expected_response": last_message})

    return dataset
