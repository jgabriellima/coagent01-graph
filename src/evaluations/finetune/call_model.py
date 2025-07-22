# finetune/deploy_model.py
import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")


def call_model(prompt):
    return openai.ChatCompletion.create(model="ft-XXXXXX", prompt=prompt)["choices"][0][
        "message"
    ]["content"]
