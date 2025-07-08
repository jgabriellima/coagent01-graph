from typing_extensions import Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.types import Command
from langgraph_supervisor import create_supervisor

# from copilotkit import CopilotKitState
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from typing import Annotated
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool, InjectedToolCallId, BaseTool
import os
from langgraph.graph import StateGraph, MessagesState
from langgraph.constants import START, END


model = init_chat_model("openai:gpt-4o-mini", temperature=0)
model_groq = init_chat_model("groq:llama-3.1-8b-instant", temperature=0)

FINCODER_PROMPT = """

You are a supervisor managing a weather specialist and a math specialist. 
Assign tasks to the appropriate agent based on the user's request. 
For weather-related queries, use the weather_agent. 
For math calculations, use the calculator_agent. 
You can also provide general assistance when needed.

"""

class CalculatorAgentState(AgentState):
    expression: str
    result: str

class WeatherAgentState(AgentState):
    location: str
    temperature: str
    date: str
    time: str

# class AgentState(CopilotKitState):
class SupervisorState(MessagesState):
    """
    Here we define the state of the agent

    In this instance, we're inheriting from CopilotKitState, which will bring in
    the CopilotKitState fields. We're also adding a custom field, `language`,
    which will be used to set the language of the agent.
    """

    proverbs: list[str] = []
    weather_agent_data: WeatherAgentState = {}
    # your_custom_agent_state: str = ""


@tool
def get_weather(location: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """
    Get the weather for a given location.
    """
    print(f"Getting weather for {location}")    
    return f"The weather for {location} is 70 degrees."
    # return Command(
    #     update={
    #         "messages": [
    #             ToolMessage(
    #                 f"The weather for {location} is 70 degrees.", tool_call_id=tool_call_id
    #             )
    #         ]
    #     }
    # )


@tool
def calculate_math(expression: str):
    """
    Calculate a simple math expression.
    Example: "2 + 3" or "10 * 5"
    """
    print(f"Calculating math for {expression}")
    try:
        # Simple mock calculation - in real scenario you'd use a proper math parser
        # This is just a placeholder for demonstration
        if "+" in expression:
            parts = expression.split("+")
            result = sum(float(part.strip()) for part in parts)
        elif "*" in expression:
            parts = expression.split("*")
            result = 1
            for part in parts:
                result *= float(part.strip())
        elif "-" in expression:
            parts = expression.split("-")
            result = float(parts[0].strip()) - float(parts[1].strip())
        elif "/" in expression:
            parts = expression.split("/")
            result = float(parts[0].strip()) / float(parts[1].strip())
        else:
            result = float(expression.strip())

        return f"The result of {expression} is {result}"
    except:
        return f"Could not calculate {expression}. Please use format like '2 + 3' or '10 * 5'"


# Create specialized agents
def create_weather_agent():
    """Create a specialized weather agent"""
    print("Creating weather agent")
    weather_agent = create_react_agent(
        model=model_groq,
        tools=[get_weather],
        prompt="You are a weather specialist. You are given a location and you need to return the weather for that location. No other information is needed. No extra text or explanation is needed. Just complete the task. OUTPUT: location = temperature (updated date and time)",
        name="weather_agent",
        response_format=WeatherAgentState,
    )
    return weather_agent


def create_calculator_agent():
    """Create a specialized calculator agent"""
    print("Creating calculator agent")
    return create_react_agent(
        model="openai:gpt-4o-mini",
        tools=[calculate_math],
        prompt="You are a math specialist. Help users with calculations and math problems.",
        name="calculator_agent",
    )


def create_supervisor_agent(tools):
    """Create a specialized supervisor agent"""
    print("Creating supervisor agent")
    return create_react_agent(
        model="openai:gpt-4o-mini",
        tools=tools,
        prompt="You are a supervisor managing a weather specialist and a math specialist. Assign tasks to the appropriate agent based on the user's request. For weather-related queries, use the weather_agent. For math calculations, use the calculator_agent. You can also provide general assistance when needed.",
        name="supervisor_agent",
    )

def pre_hook_supervisor_node(state: MessagesState, config: RunnableConfig):
    print(f"Pre-hook supervisor: {state}")
    
    return state


def compile_workflow(workflow: StateGraph):
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
    """Create the multi-agent system with supervisor"""
    # Create specialized agents
    weather_agent = create_weather_agent()
    calculator_agent = create_calculator_agent()

    supervisor_workflow = create_supervisor(
        agents=[weather_agent, calculator_agent],  # type: ignore
        model=model,
        prompt=FINCODER_PROMPT,
        add_handoff_messages=False,
        add_handoff_back_messages=True,
        supervisor_name="fincoder_agent",
    )
    supervisor_workflow = compile_workflow(supervisor_workflow)
    # Create general workflow
    general_workflow = StateGraph(AgentState)
    general_workflow.add_node("pre_hook_supervisor_node", pre_hook_supervisor_node)
    general_workflow.add_node("fincoder_agent", supervisor_workflow)
    
    general_workflow.add_edge(START, "pre_hook_supervisor_node")
    general_workflow.add_edge("pre_hook_supervisor_node", "fincoder_agent")
    general_workflow.add_edge("fincoder_agent", END)
    
    general_workflow.set_entry_point("pre_hook_supervisor_node")
    
    # Compile the general workflow
    graph = compile_workflow(general_workflow)

    return graph


# Create the multi-agent system
graph = create_multi_agent_system()
