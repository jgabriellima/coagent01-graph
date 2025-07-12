from langsmith import Client
import json

client = Client()
ds = client.get_dataset("Swarm-Traces")
records = client.list_examples(dataset_id=ds.id, filter="metadata.deepeval_score<0.8")

with open("finetune/data.jsonl", "w") as f:
    for ex in records:
        obj = {"prompt": ex.inputs["trace"], "completion": ex.outputs["final_response"]}
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
