# evaluations/datasets/builders/agentic_builder.py

from langsmith import Client
import uuid

client = Client()


def build_agentic_dataset(cleaned_traces: list[dict], dataset_name: str):
    dataset = client.create_or_update_dataset(name=dataset_name)

    for trace in cleaned_traces:
        run_input = trace["input"]
        final_output = trace["output"]
        intermediate_steps = trace.get("intermediate_steps", [])
        tool_calls = trace.get("tool_calls", [])

        inputs = {"input": run_input}
        outputs = {
            "final_output": final_output,
            "intermediate_steps": intermediate_steps,
            "tool_calls": tool_calls,
        }

        client.create_example(
            dataset_id=dataset.id,
            inputs=inputs,
            outputs=outputs,
            tags=trace.get("tags", []),
            metadata={"source_trace_id": trace.get("id"), "profile": "agentic"},
        )

    return dataset.id
