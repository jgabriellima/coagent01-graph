# Multi-Agent Swarm System Demo
# Este script demonstra um sistema multi-agente usando LangGraph com padrão Swarm

from typing_extensions import Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.types import Command
from langgraph_supervisor import create_supervisor

from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import (
    AgentState,
    AgentStateWithStructuredResponse,
)
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
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import (
    create_handoff_tool,
    create_swarm,
    SwarmState,
    add_active_agent_router,
)

# =============================================================================
# 1. CONFIGURAÇÃO INICIAL
# =============================================================================

# Configuração dos modelos
model = init_chat_model("openai:gpt-4o-mini", temperature=0)
model_groq = model  # Para fallback se necessário

print("✅ Importações e modelos configurados")

# =============================================================================
# 2. DEFINIÇÃO DE TOOLS ESPECIALIZADAS
# =============================================================================

def get_weather(location: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """
    Get the weather for a given location.
    """
    print(f"🌤️ Getting weather for {location}")

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
    """
    Calculate a simple math expression.
    Example: "2 + 3" or "10 * 5"
    """
    print(f"🧮 Calculating math for {expression}")
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
    except:
        return f"Could not calculate {expression}. Please use format like '2 + 3' or '10 * 5'"

def ask_user(question_to_user: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """This tool is used to ask the user any question. Its important always ask for things to make sure you're using the right information."""
    user_response = interrupt(
        {
            "type": "question",
            "question": question_to_user,
            "tool_call_id": tool_call_id,
        }
    )
    print(f"👤 User response: {user_response}")

    return f"The user answered with: {user_response.values()}"

print("🔧 Tools configuradas: get_weather, calculate_math, ask_user")

# =============================================================================
# 3. ESTADOS DOS AGENTES E CONFIGURAÇÃO DO WORKFLOW
# =============================================================================

# Estados dos agentes
class FullState(AgentState):
    temperature: float
    location: str
    weather: str
    math_expression: str
    math_result: str

class FullSwarmState(SwarmState, FullState):
    temperature: float
    location: str
    weather: str
    math_expression: str
    math_result: str

# Função de compilação com MemoryCheckpointer
def compile_workflow(workflow: StateGraph):
    """Compila o workflow com MemoryCheckpointer para inspeção de estado"""
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

print("📋 Estados definidos e função de compilação configurada")

# =============================================================================
# 4. CRIAÇÃO DOS AGENTES ESPECIALIZADOS
# =============================================================================

def create_main_agent():
    """Cria o Main Agent - Coordenador Principal"""
    main_agent_model = init_chat_model("openai:gpt-4o-mini", temperature=0)
    main_agent_tools = [
        ask_user,
        create_handoff_tool(
            agent_name="Alice",
            description="Transfer to Alice, she can help with any math",
        ),
        create_handoff_tool(
            agent_name="Bob", description="Transfer to Bob, he can help with weather"
        ),
    ]
    main_agent_model_bind_tools = main_agent_model.bind_tools(
        main_agent_tools,
        parallel_tool_calls=False,
    )

    main_agent = create_react_agent(
        main_agent_model_bind_tools,
        main_agent_tools,
        prompt="""You are the Main Coordination Agent responsible for task orchestration and completion.

CORE RESPONSIBILITIES:
1. Analyze incoming tasks and develop a strategic execution plan
2. Gather necessary information from users when requirements are unclear
3. Delegate specialized tasks to appropriate expert agents
4. Coordinate between agents to ensure seamless task completion

WORKFLOW PROCESS:
1. ANALYZE: Break down the user's request and identify required expertise
2. PLAN: Structure a clear strategy outlining steps and agent assignments
3. GATHER: Use `ask_user` tool to collect missing information before proceeding
4. DELEGATE: Hand off specific, well-defined subtasks to specialized agents
5. COORDINATE: Monitor progress and facilitate inter-agent communication

HANDOFF PROTOCOL:
- Always provide clear, specific instructions when transferring tasks
- Include relevant context and expected deliverables
- Ensure each agent receives the exact information needed for their specialization

Remember: Strategic planning before action ensures optimal task completion.""",
        name="main_agent",
        state_schema=FullState,
    )
    
    print("🎯 Main Agent (Coordenador) criado")
    return main_agent

def create_alice_agent():
    """Cria Alice - Especialista em Matemática"""
    alice_model = init_chat_model("openai:gpt-4o-mini", temperature=0)
    alice_tools = [
        calculate_math,
        create_handoff_tool(
            agent_name="Bob", description="Transfer to Bob, he can help with weather"
        ),
        create_handoff_tool(
            agent_name="main_agent",
            description="Use this tool to send or ask the user for information to complete the task.",
        ),
    ]
    alice_model_bind_tools = alice_model.bind_tools(
        alice_tools,
        parallel_tool_calls=False,
    )

    alice = create_react_agent(
        alice_model_bind_tools,
        alice_tools,
        prompt="You are Alice, an calculator expert. you are given a math expression and you need to calculate the result. If you need to ask the user for information, handoff to the main_agent.",
        name="Alice",
        state_schema=FullState
    )
    
    print("🧮 Alice (Especialista em Matemática) criada")
    return alice

def create_bob_agent():
    """Cria Bob - Especialista em Clima (Pirata)"""
    bob_model = init_chat_model("openai:gpt-4o-mini", temperature=0)
    bob_tools = [
        ask_user,
        get_weather,
        create_handoff_tool(
            agent_name="Alice",
            description="Transfer to Alice, she can help with any math or any calculation",
        ),
        create_handoff_tool(
            agent_name="main_agent",
            description="Use this tool to send or ask the user for information to complete the task.",
        ),
    ]
    bob_model_bind_tools = bob_model.bind_tools(
        bob_tools,
        parallel_tool_calls=False,
    )

    bob = create_react_agent(
        bob_model_bind_tools,
        bob_tools,
        prompt="You are Bob, you speak like a pirate and you are a weather specialist. You are given a location and you need to return the weather for that location using the `get_weather` tool. If you need any user information, handoff back to the main_agent. To get the number that the user is thinking handoff back to the main_agent.",
        name="Bob",
        state_schema=FullState
    )
    
    print("🏴‍☠️ Bob (Especialista em Clima - Pirata) criado")
    return bob

# =============================================================================
# 5. CONSTRUÇÃO DO WORKFLOW MULTI-AGENTE
# =============================================================================

def create_multi_agent_system():
    """Cria o sistema multi-agente completo"""
    # Criar agentes
    main_agent = create_main_agent()
    alice = create_alice_agent()
    bob = create_bob_agent()
    
    # Criação do workflow
    workflow = (
        StateGraph(FullSwarmState)
        .add_node(
            main_agent,
            destinations=(
                "Alice",
                "Bob",
            ),
        )
        .add_node(alice, destinations=("main_agent", "Bob"))
        .add_node(bob, destinations=("main_agent", "Alice"))
    )

    # Adiciona o roteador para rastrear agente ativo
    workflow = add_active_agent_router(
        builder=workflow,
        route_to=["main_agent", "Alice", "Bob"],
        default_active_agent="main_agent",
    )

    # Compila o grafo com MemoryCheckpointer
    graph = compile_workflow(workflow)

    print("🚀 Workflow multi-agente criado e compilado com MemoryCheckpointer")
    print(f"📊 Nodes no grafo: {list(graph.get_graph().nodes.keys())}")
    
    return graph

# =============================================================================
# 6. EXEMPLO DE EXECUÇÃO: CLIMA + CÁLCULO
# =============================================================================

def run_campeche_example(graph):
    """
    Executa o exemplo: "Qual a temperatura atual no Campeche? 
    Agora pegue essa temperatura e multiplique pelo numero que eu estou pensando e me retorne o final."
    """
    # Configuração do thread para rastreamento
    thread_config = {"configurable": {"thread_id": "demo-campeche-calc"}}

    # Input inicial
    initial_input = {
        "messages": [
            HumanMessage(
                content="Qual a temperatura atual no Campeche? Agora pegue essa temperatura e multiplique pelo numero que eu estou pensando e me retorne o final."
            )
        ]
    }

    print("🎬 Iniciando execução do exemplo...")
    print(f"💬 Input: {initial_input['messages'][0].content}")
    print("\n" + "="*60)
    
    # Execução step-by-step para observar o fluxo
    step_count = 0
    current_state = initial_input

    try:
        for step in graph.stream(current_state, thread_config, stream_mode="values"):
            step_count += 1
            print(f"\n🚶‍♂️ STEP {step_count}:")
            print(f"🎯 Active Agent: {step.get('active_agent', 'Unknown')}")
            
            # Estado atual detalhado
            print(f"📍 Location: {step.get('location', 'N/A')}")
            print(f"🌡️ Temperature: {step.get('temperature', 'N/A')}")
            print(f"🧮 Math Expression: {step.get('math_expression', 'N/A')}")
            print(f"🔢 Math Result: {step.get('math_result', 'N/A')}")
            
            # Última mensagem
            if 'messages' in step and step['messages']:
                last_message = step['messages'][-1]
                print(f"💬 Message Type: {type(last_message).__name__}")
                
                if hasattr(last_message, 'content') and last_message.content:
                    content = str(last_message.content)
                    if len(content) > 200:
                        content = content[:200] + "..."
                    print(f"💬 Content: {content}")
                
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    for tool_call in last_message.tool_calls:
                        print(f"🔧 Tool Call: {tool_call.get('name', 'Unknown')}")
                        print(f"📋 Args: {tool_call.get('args', {})}")
            
            print("─" * 50)
            
            # Verifica se precisa de interrupção (pergunta ao usuário)
            current_state = step
            
            # Limita execução para evitar loop infinito
            if step_count > 10:
                print("⚠️ Limitando execução em 10 steps para segurança")
                break

    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n✅ Execução concluída após {step_count} steps")
    
    return thread_config

# =============================================================================
# 7. INSPEÇÃO DO ESTADO DO CHECKPOINTER
# =============================================================================

def inspect_checkpointer_state(graph, thread_config):
    """Inspeciona o estado salvo no checkpointer"""
    try:
        saved_state = graph.get_state(thread_config)
        print("💾 ESTADO SALVO NO CHECKPOINTER:")
        print("─" * 40)
        
        if saved_state and saved_state.values:
            state_values = saved_state.values
            
            print(f"🎯 Active Agent: {state_values.get('active_agent', 'N/A')}")
            print(f"📍 Location: {state_values.get('location', 'N/A')}")
            print(f"🌡️ Temperature: {state_values.get('temperature', 'N/A')}")
            print(f"🧮 Math Expression: {state_values.get('math_expression', 'N/A')}")
            print(f"🔢 Math Result: {state_values.get('math_result', 'N/A')}")
            print(f"📅 Date: {state_values.get('date', 'N/A')}")
            print(f"⏰ Time: {state_values.get('time', 'N/A')}")
            
            # Contagem de mensagens
            if 'messages' in state_values:
                print(f"💬 Total Messages: {len(state_values['messages'])}")
                
                # Últimas 3 mensagens
                print("\n📝 ÚLTIMAS MENSAGENS:")
                for i, msg in enumerate(state_values['messages'][-3:], 1):
                    msg_type = type(msg).__name__
                    content = getattr(msg, 'content', 'No content')
                    if len(str(content)) > 150:
                        content = str(content)[:150] + "..."
                    print(f"  {i}. {msg_type}: {content}")
        
        # Metadados do checkpoint
        if saved_state and saved_state.metadata:
            print(f"\n🔖 Checkpoint Metadata:")
            print(f"   Step: {saved_state.metadata.get('step', 'N/A')}")
            print(f"   Source: {saved_state.metadata.get('source', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Erro ao acessar estado do checkpointer: {e}")

    print("\n" + "="*60)

# =============================================================================
# 8. SIMULAÇÃO DE RESPOSTA DO USUÁRIO
# =============================================================================

def continue_with_user_input(graph, thread_config, user_input, max_steps=5):
    """Continua a execução com input do usuário"""
    print(f"🎭 Continuando com resposta do usuário: '{user_input}'")
    
    try:
        # Continua a partir do estado atual
        step_count = 0
        for step in graph.stream({"user_input": str(user_input)}, thread_config, stream_mode="values"):
            step_count += 1
            print(f"\n🚶‍♂️ CONTINUATION STEP {step_count}:")
            print(f"🎯 Active Agent: {step.get('active_agent', 'Unknown')}")
            print(f"🔢 Math Result: {step.get('math_result', 'N/A')}")
            
            if 'messages' in step and step['messages']:
                last_message = step['messages'][-1]
                if hasattr(last_message, 'content'):
                    content = str(last_message.content)
                    if len(content) > 200:
                        content = content[:200] + "..."
                    print(f"💬 Content: {content}")
            
            if step_count >= max_steps:
                break
                
    except Exception as e:
        print(f"⚠️ Erro na continuação: {e}")

# =============================================================================
# 9. ANÁLISE FINAL DO ESTADO
# =============================================================================

def analyze_final_state(graph, thread_config):
    """Análise final do estado"""
    # Estado final completo
    final_state = graph.get_state(thread_config)

    print("📊 ANÁLISE FINAL DO ESTADO:")
    print("═" * 50)

    if final_state and final_state.values:
        values = final_state.values
        
        print(f"🏁 Estado Final:")
        print(f"   🎯 Agente Ativo: {values.get('active_agent', 'N/A')}")
        print(f"   📍 Localização: {values.get('location', 'N/A')}")
        print(f"   🌡️ Temperatura: {values.get('temperature', 'N/A')}")
        print(f"   🧮 Expressão Matemática: {values.get('math_expression', 'N/A')}")
        print(f"   🔢 Resultado do Cálculo: {values.get('math_result', 'N/A')}")
        
        print(f"\n📈 Estatísticas:")
        print(f"   💬 Total de Mensagens: {len(values.get('messages', []))}")
        
        # Fluxo de agentes
        agent_flow = []
        for msg in values.get('messages', []):
            if hasattr(msg, 'name') and msg.name:
                agent_flow.append(msg.name)
        
        if agent_flow:
            print(f"   🔄 Fluxo de Agentes: {' → '.join(set(agent_flow))}")
        
        print(f"\n🎯 RESULTADO ESPERADO:")
        if values.get('temperature') and values.get('math_result'):
            temp = values.get('temperature', '').replace(' degrees', '')
            try:
                temp_num = float(temp)
                result = values.get('math_result', 0)
                print(f"   🌡️ Temperatura do Campeche: {temp}°")
                print(f"   🔢 Número pensado: {result/temp_num if temp_num != 0 else 'N/A'}")
                print(f"   ✅ Resultado Final: {temp}° × número = {result}")
            except:
                print(f"   ⚠️ Não foi possível calcular o resultado final")
        else:
            print(f"   ⚠️ Execução incompleta - execute as funções acima primeiro")

    print("\n" + "═" * 50)
    print("🎉 Demonstração do Sistema Multi-Agente Concluída!")

# =============================================================================
# 10. UTILITÁRIOS PARA DEBUGGING
# =============================================================================

def reset_conversation(thread_id="demo-reset"):
    """Reset conversation state for new testing"""
    new_config = {"configurable": {"thread_id": thread_id}}
    print(f"🔄 Conversação resetada com thread_id: {thread_id}")
    return new_config

def inspect_state_details(graph, config):
    """Inspeciona detalhes do estado atual"""
    try:
        state = graph.get_state(config)
        if state and state.values:
            print("🔍 DETALHES DO ESTADO:")
            for key, value in state.values.items():
                if key != 'messages':
                    print(f"   {key}: {value}")
            
            if 'messages' in state.values:
                print(f"\n📨 Mensagens ({len(state.values['messages'])}):")
                for i, msg in enumerate(state.values['messages'][-5:], 1):
                    print(f"   {i}. {type(msg).__name__}: {str(msg)[:100]}...")
        else:
            print("⚠️ Nenhum estado encontrado")
    except Exception as e:
        print(f"❌ Erro ao inspecionar estado: {e}")

print("🛠️ Utilitários de debugging configurados")

# =============================================================================
# 11. FUNÇÃO PRINCIPAL PARA EXECUTAR TUDO
# =============================================================================

def main():
    """Função principal que executa toda a demonstração"""
    print("🚀 INICIANDO DEMONSTRAÇÃO DO SISTEMA MULTI-AGENTE")
    print("═" * 60)
    
    # 1. Criar sistema multi-agente
    graph = create_multi_agent_system()
    
    # 2. Executar exemplo do Campeche
    thread_config = run_campeche_example(graph)
    
    # 3. Inspecionar estado do checkpointer
    inspect_checkpointer_state(graph, thread_config)
    
    # 4. Simular resposta do usuário (número 3)
    user_number = 3
    print(f"\n🎭 Simulando resposta do usuário: '{user_number}'")
    continue_with_user_input(graph, thread_config, user_number)
    
    # 5. Análise final
    analyze_final_state(graph, thread_config)
    
    print("\n💡 FUNÇÕES DISPONÍVEIS PARA USO POSTERIOR:")
    print("   - reset_conversation(thread_id)")
    print("   - inspect_state_details(graph, config)")
    print("   - continue_with_user_input(graph, thread_config, user_input)")
    
    return graph, thread_config

if __name__ == "__main__":
    # Executar demonstração completa
    graph, thread_config = main() 