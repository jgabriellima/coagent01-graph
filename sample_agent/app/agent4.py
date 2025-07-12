from typing_extensions import Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.types import Command
from langgraph_supervisor import create_supervisor

# from copilotkit import CopilotKitState
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState, AgentStateWithStructuredResponse
from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
from typing import Annotated
from langgraph.types import Command, interrupt
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool, InjectedToolCallId, BaseTool
import os
from langgraph.graph import StateGraph, MessagesState
from langgraph.constants import START, END
from pydantic import BaseModel
import operator
from langchain_core.messages import BaseMessage

model = init_chat_model("openai:gpt-4o-mini", temperature=0)
model_groq = model #init_chat_model("groq:llama-3.1-8b-instant", temperature=0)

FINCODER_PROMPT = """

You are a supervisor managing a weather specialist and a math specialist. 
Assign tasks to the appropriate agent based on the user's request. 
- For weather-related queries, use the weather_agent. Input: location (e.g. "New York")
- For math calculations, use the calculator_agent. Input: expression (e.g. "2 + 3")
- For any other question that is not related to weather or math, use the ask_user tool.

Tools:
- ask_user: This tool is used to ask the user any question about things you need to know. Input: question_to_user
- weather_agent: This tool is used to get the weather for a given location. Input: location (e.g. "New York")
- calculator_agent: This tool is used to calculate a simple math expression. Input: expression (e.g. "2 + 3")

Note:
- Before start, make a plan of what you need to do.
"""

class CalculatorAgentState(AgentState):
    expression: str
    result: str

class WeatherAgentOutput(BaseModel):
    location: str
    temperature: str
    date: str
    time: str
    
class WeatherAgentState(AgentStateWithStructuredResponse):
    location: str = ""
    temperature: str
    date: str = ""
    time: str = ""
    tool_call_id: str = ""

# class AgentState(CopilotKitState):
class SupervisorState(AgentState):
    """
    Here we define the state of the agent

    In this instance, we're inheriting from CopilotKitState, which will bring in
    the CopilotKitState fields. We're also adding a custom field, `language`,
    which will be used to set the language of the agent.
    """

    calculator_agent_data: CalculatorAgentState = {}
    weather_agent_data: WeatherAgentState = {}
    # your_custom_agent_state: str = ""


@tool
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
                    f"The weather for {location} is 70 degrees.", tool_call_id=tool_call_id
                )
            ]
        }
    )


@tool
def calculate_math(expression: str):
    """
    Calculate a simple math expression.
    Example: "2 + 3" or "10 * 5"
    """
    print(f"Calculating math for {expression}")
    try:
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


def get_last_message_with_tool_call_id(messages):
    """
    Retorna a última mensagem da lista que possui o atributo 'tool_call_id'.
    """
    for msg in reversed(messages):
        if hasattr(msg, "tool_call_id") or (isinstance(msg, dict) and "tool_call_id" in msg):
            return msg
    
    return None

# Create specialized agents
# def create_weather_subgraph():
#     """Create a specialized weather agent"""
#     print("Creating weather agent")
    
#     def node_hook(state: WeatherAgentState, config: RunnableConfig):
#         print(f"\n\nWeather agent state: {state.keys()}\n\n")
        
#         return Command(
#             update={
#                 "weather_agent_data": state,
#                 "messages": state["messages"]
#             }
#         )
        
#     weather_agent = create_react_agent(
#         model=model_groq,
#         tools=[get_weather],
#         prompt="You are a weather specialist. You are given a location and you need to return the weather for that location. No other information is needed. No extra text or explanation is needed. Just complete the task. OUTPUT: location = temperature (updated date and time)",
#         name="weather_agent",
#         state_schema=WeatherAgentState,
#         debug=True,
#         post_model_hook=node_hook,
#     )
    
#     return weather_agent


def create_weather_subgraph():
    """Create a specialized weather agent"""
    print("Creating weather agent")
    
    
    weather_agent = create_react_agent(
        model=model_groq,
        tools=[get_weather],
        prompt="You are a weather specialist. You are given a location and you need to return the weather for that location. No other information is needed. No extra text or explanation is needed. Just complete the task. OUTPUT: location = temperature (updated date and time)",
        name="weather_agent",
        state_schema=WeatherAgentState
    )
    
    def node_hook(state: WeatherAgentState, config: RunnableConfig):
        print(f"Weather agent state: {state}")
        
        return Command(
            graph=Command.PARENT,
            update={
                "weather_agent_data": state,
                "messages": state["messages"] # [-1] fica em loop infinito [-2] é uma tool message, nao da pra injetar no parent
            }
        )
    
    weather_workflow = StateGraph(WeatherAgentState)
    weather_workflow.add_node("weather_agent", weather_agent)
    weather_workflow.add_node("node_hook", node_hook)
    #
    weather_workflow.add_edge(START, "weather_agent")
    weather_workflow.add_edge("weather_agent", "node_hook") 
    weather_workflow.add_edge("node_hook", END) 
    # weather_workflow.add_edge("weather_agent", END)
    #
    weather_workflow.set_entry_point("weather_agent")
    weather_workflow = weather_workflow.compile(name="weather_workflow")
    
    return weather_workflow


def create_calculator_agent():
    """Create a specialized calculator agent"""
    print("Creating calculator agent")
    return create_react_agent(
        model="openai:gpt-4o-mini",
        tools=[calculate_math],
        prompt="You are a math specialist. Help users with calculations and math problems. Be concise and to the point. no extra text or explanation is needed. Just complete the task. OUTPUT: expression = result",
        name="calculator_agent",
    )

def pre_hook_supervisor_node(state: SupervisorState, config: RunnableConfig):
    print(f"Pre-hook supervisor: {state}")
    
    return state


def post_hook_supervisor_node(state: SupervisorState, config: RunnableConfig):
    print(f"Post-hook supervisor: {state}")
    
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
    

@tool(description="This tool is used to ask the user any question. Its important always ask for things to make sure you're using the right information.")
def ask_user(question_to_user: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    user_response = interrupt({
        "type": "question",
        "question": question_to_user,
        "tool_call_id": tool_call_id,
    })
    print(f"User response: {user_response}")

    return f"The user answered with: {user_response.values()}"


def create_multi_agent_system():
    """Create the multi-agent system with supervisor"""
    # Create specialized agents
    weather_agent = create_weather_subgraph()
    calculator_agent = create_calculator_agent()

    supervisor_workflow = create_supervisor(
        agents=[weather_agent, calculator_agent],
        tools=[ask_user],
        model=model,
        prompt=FINCODER_PROMPT,
        add_handoff_messages=False,
        add_handoff_back_messages=True,
        state_schema=SupervisorState
    )
    supervisor_workflow = compile_workflow(supervisor_workflow)
    # Create general workflow
    general_workflow = StateGraph(SupervisorState)
    general_workflow.add_node("pre_hook_supervisor_node", pre_hook_supervisor_node)
    general_workflow.add_node("fincoder_supervisor_workflow", supervisor_workflow)
    general_workflow.add_node("post_hook_supervisor_node", post_hook_supervisor_node)
    
    general_workflow.add_edge(START, "pre_hook_supervisor_node")
    general_workflow.add_edge("pre_hook_supervisor_node", "fincoder_supervisor_workflow")
    general_workflow.add_edge("fincoder_supervisor_workflow", "post_hook_supervisor_node")
    general_workflow.add_edge("post_hook_supervisor_node", END)
    
    general_workflow.set_entry_point("pre_hook_supervisor_node")
    
    # Compile the general workflow
    graph = compile_workflow(general_workflow)

    return graph


# Create the multi-agent system
graph = create_multi_agent_system()
