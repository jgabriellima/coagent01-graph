# finetune/run_finetune.py
import os, subprocess

os.environ["OPENAI_API_KEY"] = "<YOUR_KEY>"
subprocess.run(
    ["openai", "tools", "fine_tunes.prepare_data", "-f", "finetune/data.jsonl"]
)
subprocess.run(
    ["openai", "api", "fine_tunes.create", "-t", "file-XXXXX", "-m", "gpt-4o-mini"]
)
