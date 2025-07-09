from typing_extensions import Literal, TypedDict, Optional, Annotated, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.types import Command
from langgraph_supervisor import create_supervisor

# from copilotkit import CopilotKitState
from langgraph.prebuilt import create_react_agent, ToolNode
from langgraph.prebuilt.chat_agent_executor import (
    AgentState,
    AgentStateWithStructuredResponse,
)
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from langgraph.types import Command, interrupt
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool, InjectedToolCallId, BaseTool
from langgraph.graph import StateGraph, MessagesState
from langgraph.constants import START, END
from pydantic import BaseModel, Field, ConfigDict
import operator
from langchain_core.messages import BaseMessage


# CopilotKit integration (optional)
from copilotkit import CopilotKitState
from copilotkit.langgraph import copilotkit_interrupt

# Define model
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ---------- STATE MODELS ----------


class CalculatorAgentState(AgentState):
    expression: str = ""
    result: str = ""


class WeatherAgentState(AgentState):
    location: str = ""
    temperature: str = ""
    date: str = ""
    time: str = ""
    tool_call_id: str = ""
    messages: list[BaseMessage] = []


class SupervisorState(AgentState):
    calculator_agent_data: CalculatorAgentState = CalculatorAgentState()
    weather_agent_data: WeatherAgentState = WeatherAgentState()
    next_agent: str = ""
    input_to_next_agent: str = ""


# ---------- TOOLS ----------


@tool(description="This tool is used to get the weather for a given location.")
def get_weather(location: str):
    """
    This tool is used to get the weather for a given location.
    """
    # return Command(
    #     update={
    #         "location": location,
    #         "temperature": "70 degrees",
    #         "date": "2025-01-01",
    #         "time": "12:00:00",
    #         "tool_call_id": tool_call_id,
    #         "messages": [
    #             ToolMessage(
    #                 content=f"Weather for {location} is 70 degrees.",
    #                 tool_call_id=tool_call_id,
    #             )
    #         ],
    #     }
    # )
    return f"Weather for {location} is 70 degrees."


@tool
def calculate_math(expression: str):
    """
    This tool is used to calculate a math expression.
    """
    try:
        result = str(eval(expression))
        return f"The result of {expression} is {result}"
    except:
        return f"Could not evaluate {expression}"


@tool
def ask_user(question_to_user: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """
    This tool is used to ask the user a question.
    """
    user_response = interrupt(
        {
            "type": "question",
            "question": question_to_user,
            "tool_call_id": tool_call_id,
        }
    )
    return f"The user answered with: {user_response.values()}"


# ---------- WEATHER SUBGRAPH ----------


def create_weather_subgraph():
    weather_agent = create_react_agent(
        model=model,
        tools=[get_weather],
        prompt="You are a weather specialist. Just give weather info based on location.",
        name="weather_agent",
        state_schema=WeatherAgentState,
    )

    def node_hook(state: WeatherAgentState, config: RunnableConfig):
        print(f"WeatherAgentState: {state}")
        return Command(
            update={
                "next_agent": "fincoder_supervisor_node",
                "weather_agent_data": state,
                "messages": HumanMessage(content=f"Weather for {state.location} is 70 degrees."),
            },
        )

    graph = StateGraph(WeatherAgentState)
    graph.add_node("weather_agent", weather_agent)
    graph.add_node("node_hook", node_hook)
    graph.add_edge(START, "weather_agent")
    graph.add_edge("weather_agent", "node_hook")
    graph.add_edge("node_hook", END)
    # graph.add_edge("weather_agent", END)
    graph.set_entry_point("weather_agent")

    return graph.compile(name="weather_workflow")


# ---------- CALCULATOR AGENT ----------


def create_calculator_agent():
    return create_react_agent(
        model=model,
        tools=[calculate_math],
        prompt="You are a math agent. Answer math expressions directly.",
        name="calculator_agent",
    )


# ---------- SUPERVISOR NODE ----------

FINCODER_PROMPT = """
You are a supervisor managing a weather and math agent.
Decide which agent should handle the request.
Return one of: weather_agent, calculator_agent, ask_user_node, END.
"""


def fincoder_supervisor_node(state: SupervisorState, config: RunnableConfig):
    class NextAgentModel(BaseModel):
        next_agent: Optional[str] = Field(None)
        input_to_next_agent: Optional[str] = Field(None)
        messages: Optional[List[str]] = Field(default=None)
        model_config = ConfigDict(extra='forbid')


    structured_model = model.with_structured_output(NextAgentModel)
    result: NextAgentModel = structured_model.invoke([SystemMessage(content=FINCODER_PROMPT)] + state.get("messages", []))
    print(f"Result: {result}")
    return Command(
        goto=result.next_agent,
        update={
            "next_agent": result.next_agent,
            "input_to_next_agent": result.input_to_next_agent,
            "messages": result.messages,
        },
    )


def should_continue(state: SupervisorState) -> str:
    return state.get("next_agent", END)


# ---------- MAIN WORKFLOW ----------
def compile_workflow(workflow: StateGraph):
    import os
    is_langgraph_api = (
        os.environ.get("LANGGRAPH_API", "false").lower() == "true"
        or os.environ.get("LANGGRAPH_API_DIR") is not None
    )
    
    if is_langgraph_api:
        return workflow.compile()
    else:  
        from langgraph.checkpoint.memory import MemorySaver
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    

def create_multi_agent_system():
    workflow = StateGraph(SupervisorState)
    workflow.add_node("fincoder_supervisor_node", fincoder_supervisor_node)
    workflow.add_node("weather_agent", create_weather_subgraph())
    workflow.add_node("calculator_agent", create_calculator_agent())
    workflow.add_node("ask_user_node", ToolNode(tools=[ask_user], name="ask_user_node"))

    workflow.add_conditional_edges("fincoder_supervisor_node", should_continue)
    workflow.add_edge("weather_agent", "fincoder_supervisor_node")
    workflow.add_edge("calculator_agent", "fincoder_supervisor_node")
    workflow.add_edge("ask_user_node", "fincoder_supervisor_node")

    workflow.add_edge(START, "fincoder_supervisor_node")
    workflow.add_edge("fincoder_supervisor_node", END)
    workflow.set_entry_point("fincoder_supervisor_node")

    workflow = compile_workflow(workflow)
    return workflow


# ---------- EXECUTION ----------

graph = create_multi_agent_system()
