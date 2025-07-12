from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model

from sample_agent.agents.bob_agent import build_bob_agent
from pprint import pprint


def tool_for_testing():
    """
    This is a tool for testing.
    """
    
    def handle_tool_call(tool_call_id: str):
        return "The weather in Campeche is sunny"
    
    return handle_tool_call


if __name__ == "__main__":
    state = {
        "location": "Campeche",
        "weather": "",
        "temperature": 0,
        "thread_mode": "task_only",
        "task_type": "weather",
        "constraints": ["Avoid slang", "Do not speculate future weather"],
    }

    bob_agent = build_bob_agent(model=init_chat_model("openai:gpt-4o-mini", temperature=0), handoff_tools=[tool_for_testing], state=state)

    thread_config = {"configurable": {"thread_id": "demo-123"}}

    response = bob_agent.invoke(
        {"messages": [HumanMessage(content="What is the weather in Campeche?")]},
        thread_config,
    )

    for message in response["messages"]:
        pprint(message.pretty_print())

    pprint(f"Structured response: {response["structured_response"]}")

    # print(bob_agent.get_state(thread_config))
