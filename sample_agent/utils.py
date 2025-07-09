from langchain_core.tools import tool
from langgraph.types import Command
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from typing import Annotated
from langgraph_swarm import create_handoff_tool
from langgraph_swarm.handoff import (
    _normalize_agent_name,
    WHITESPACE_RE,
    METADATA_KEY_HANDOFF_DESTINATION,
)
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId


def create_handoff_tool_with_state_propagation(
    *,
    agent_name: str,
    name: str | None = None,
    description: str | None = None,
    propagate_keys: list[str] | None = None,  # opcional: definir campos específicos
) -> tool:
    """
    Custom version of LangGraph's handoff tool that propagates the current agent's state
    along with messages and active_agent.

    Args:
        agent_name: Destination agent node name.
        name: Tool name.
        description: Tool description.
        propagate_keys: Optional list of state keys to propagate in the update.
                        If None, the entire state is forwarded.
    """

    if name is None:
        name = f"transfer_to_{_normalize_agent_name(agent_name)}"

    if description is None:
        description = f"Ask agent '{agent_name}' for help"

    @tool(name, description=description)
    def handoff_to_agent_with_state(
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        tool_message = ToolMessage(
            content=f"Successfully transferred to {agent_name}",
            name=name,
            tool_call_id=tool_call_id,
        )

        update = {
            "messages": state["messages"] + [tool_message],
            "active_agent": agent_name,
        }

        if propagate_keys:
            update.update({key: state[key] for key in propagate_keys if key in state})
        else:
            update.update(
                {
                    k: v
                    for k, v in state.items()
                    if k not in ["messages", "active_agent"]
                }
            )

        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update=update,
        )

    handoff_to_agent_with_state.metadata = {
        METADATA_KEY_HANDOFF_DESTINATION: agent_name
    }
    return handoff_to_agent_with_state



def create_handoff_tool_with_task(
    *,
    name: str | None = None,
    agent_name: str,
    description: str | None = None,
    propagate_keys: list[str] | None = None,
):
    """
    Custom handoff tool that transfers control to another agent with a task message
    and optional partial state propagation.
    """

    if name is None:
        name = f"handoff_to_{agent_name.lower()}"

    if description is None:
        description = f"Ask agent '{agent_name}' for help"

    @tool(description=description)
    def handoff_to_agent_with_task(
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
        task_message: str  # this is required at tool invocation
    ):
        # Only the task message is passed forward in messages
        messages = [HumanMessage(content=task_message)]

        update = {
            "messages": messages,
            "active_agent": agent_name,
        }

        if propagate_keys:
            update.update({key: state[key] for key in propagate_keys if key in state})
        else:
            update.update({
                k: v for k, v in state.items()
                if k not in ["messages", "active_agent"]
            })

        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update=update,
        )

    # Used by LangGraph to route tools to their destinations
    handoff_to_agent_with_task.metadata = {
        "handoff_to_agent": agent_name
    }

    return handoff_to_agent_with_task