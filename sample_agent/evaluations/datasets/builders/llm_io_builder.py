# evaluations/datasets/builders/llm_io_builder.py

from typing import List, Dict, Any
from langsmith import Client


def build_llm_io_dataset(
    project_name: str, tag_filter: str = "llm-io"
) -> List[Dict[str, Any]]:
    """
    Build an evaluation dataset for simple LLM input/output flows.
    Example: instruction -> response

    Args:
        project_name (str): Name of the LangSmith project.
        tag_filter (str): Tag to filter relevant traces.

    Returns:
        List[Dict]: List of {input, expected_output} pairs.
    """
    client = Client()

    runs = client.list_runs(
        project_name=project_name, execution_order=1, run_type="llm"
    )

    dataset = []

    for run in runs:
        if tag_filter not in run.tags:
            continue

        dataset.append(
            {
                "input": run.inputs.get("input") or run.inputs,
                "expected_output": (
                    run.outputs.get("output")
                    if isinstance(run.outputs, dict)
                    else run.outputs
                ),
            }
        )

    return dataset
