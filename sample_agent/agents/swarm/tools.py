from langgraph.types import Command
from langchain_core.messages import ToolMessage
from typing import Annotated
from langchain_core.tools import InjectedToolCallId
from langgraph.types import interrupt


def get_weather(location: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """
    Get the weather for a given location.
    """
    print(f"Getting weather for {location}")

    return Command(
        update={
            "location": location,
            "temperature": "70 degrees",
            "date": "2025-01-01",
            "time": "12:00:00",
            "tool_call_id": tool_call_id,
            "messages": [
                ToolMessage(
                    f"The weather for {location} is 70 degrees.",
                    tool_call_id=tool_call_id,
                )
            ],
        }
    )


def calculate_math(expression: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """Calculate a math expression using Python's eval."""
    try:
        # Sanitize for safety (only allow math operations)
        allowed_chars = set("0123456789+-*/().,eE ")
        if not set(expression).issubset(allowed_chars):
            raise ValueError("Invalid characters in expression")

        result = eval(expression)
        return Command(
            update={
                "math_expression": expression,
                "math_result": result,
                "messages": [
                    ToolMessage(
                        f"The result of {expression} is {result}",
                        tool_call_id=tool_call_id,
                    )
                ],
            }
        )
    except Exception as e:
        return f"Could not calculate {expression}. Error: {e}"


def ask_user(question_to_user: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    "This tool is used to ask the user any question. Its important always ask for things to make sure you're using the right information."
    user_response = interrupt(
        {
            "type": "question",
            "question": question_to_user,
            "tool_call_id": tool_call_id,
        }
    )
    print(f"User response: {user_response}")

    return f"The user answered with: {user_response.values()}"
