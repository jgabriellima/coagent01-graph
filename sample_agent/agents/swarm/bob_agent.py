from sample_agent.agents.swarm.builder import AgentBuilder
from pydantic import BaseModel
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
import os

# Tools
from sample_agent.agents.swarm.tools import get_weather, ask_user
from typing import Callable


class BobState(AgentStateWithStructuredResponse):
    location: str
    weather: str
    temperature: float
    thread_mode: str
    task_type: str
    constraints: list[str] = []


class BobOutput(BaseModel):
    location: str
    weather: str
    temperature: float


def build_bob_agent(
    model, handoff_tools: list[Callable] | None = None, state: dict = None
):
    tools = [get_weather, ask_user]

    if handoff_tools:
        tools.extend(handoff_tools)

    # Dynamically resolve the prompt paths relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))  # Sobe dois níveis: /swarm/ -> /agents/ -> /sample_agent/
    prompt_template_path = os.path.join(
        base_dir, "prompts", "base_agent_prompt.jinja2"
    )
    dynamic_block_template_path = os.path.join(
        base_dir, "prompts", "fragments", "bob.jinja2"
    )

    builder = AgentBuilder(
        name="Bob",
        model=model,
        tools=tools,
        agent_identity="Bob, the pirate weather specialist.",
        responsibilities=[
            "Provide accurate weather reports",
            "Respond only within your weather expertise",
            "Use get_weather tool responsibly",
        ],
        constraints=[
            "Speak like a pirate in every response",
            "Never answer non-weather related questions",
            "Never make assumptions beyond the given location",
            "Interact with the user when needed using the `ask_user` (Human-in-the-loop) tool",
        ],
        state_schema=BobState,
        response_format=BobOutput,
        prompt_template_path=prompt_template_path,
        dynamic_block_template_path=dynamic_block_template_path,
    )

    return builder.build()
