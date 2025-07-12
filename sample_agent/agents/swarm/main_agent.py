from typing import Callable
from langgraph.prebuilt.chat_agent_executor import AgentState
from sample_agent.agents.swarm.builder import AgentBuilder
import os

# Tools
from sample_agent.agents.swarm.tools import ask_user


class MainAgentState(AgentState):
    temperature: float
    location: str
    weather: str
    math_expression: str
    math_result: str
    thread_mode: str
    task_type: str
    constraints: list[str] = []


MainAgentOutput = None


def build_main_agent(model, handoff_tools: list[Callable] | None = None):

    tools = [ask_user]

    if handoff_tools:
        tools.extend(handoff_tools)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))  # Sobe dois níveis: /swarm/ -> /agents/ -> /sample_agent/
    prompt_template_path = os.path.join(
        base_dir, "prompts", "base_agent_prompt.jinja2"
    )
    dynamic_block_template_path = os.path.join(
        base_dir, "prompts", "fragments", "main.jinja2"
    )

    builder = AgentBuilder(
        name="Main_Agent",
        model=model,
        tools=tools,
        agent_identity="Main Agent, responsible for coordinating tasks and managing user interaction.",
        responsibilities=[
            "Route tasks to the appropriate agent",
            "Coordinate between Alice and Bob",
            "Interact with the user when needed using the `ask_user` (Human-in-the-loop) tool",
        ],
        constraints=[],
        state_schema=MainAgentState,
        response_format=None,
        prompt_template_path=prompt_template_path,
        dynamic_block_template_path=dynamic_block_template_path,
    )

    return builder.build()
