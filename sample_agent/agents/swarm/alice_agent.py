from sample_agent.agents.swarm.builder import AgentBuilder
from pydantic import BaseModel
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
import os

# Tools
from sample_agent.agents.swarm.tools import calculate_math
from typing import Callable


class AliceState(AgentStateWithStructuredResponse):
    math_expression: str
    math_result: str
    thread_mode: str
    task_type: str
    constraints: list[str] = []


class AliceOutput(BaseModel):
    math_expression: str
    math_result: str


def build_alice_agent(
    model, handoff_tools: list[Callable] | None = None, state: dict = None
):
    tools = [calculate_math]

    if handoff_tools:
        tools.extend(handoff_tools)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))  # Sobe dois níveis: /swarm/ -> /agents/ -> /sample_agent/
    prompt_template_path = os.path.join(
        base_dir, "prompts", "base_agent_prompt.jinja2"
    )
    dynamic_block_template_path = os.path.join(
        base_dir, "prompts", "fragments", "alice.jinja2"
    )

    builder = AgentBuilder(
        name="Alice",
        model=model,
        tools=tools,
        agent_identity="Alice, expert in mathematics and numeric calculations.",
        responsibilities=[
            "Solve math expressions accurately",
            "Avoid making assumptions about external context",
        ],
        constraints=[
            "Never answer questions unrelated to math",
            "Always use `calculate_math` tool to evaluate expressions",
        ],
        state_schema=AliceState,
        response_format=AliceOutput,
        prompt_template_path=prompt_template_path,
        dynamic_block_template_path=dynamic_block_template_path,
    )

    return builder.build()
