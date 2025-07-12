# evaluations/ingestion/extract_traces.py

from langsmith import Client
from datetime import datetime, timedelta
from typing import Literal


def extract_traces(dataset_name: str, start_days_ago: int = 7) -> list[dict]:
    """Fetch traces for a given dataset using LangSmith API."""
    client = Client()
    since = datetime.now() - timedelta(days=start_days_ago)

    runs = client.list_runs(
        project_name=dataset_name,
        run_type="chain",
        execution_order="desc",
        created_after=since,
    )

    traces = []
    for run in runs:
        if run.outputs:
            traces.append(
                {
                    "id": run.id,
                    "input": run.inputs,
                    "output": run.outputs,
                    "tags": run.tags,
                    "config": run.config,
                }
            )
    return traces
