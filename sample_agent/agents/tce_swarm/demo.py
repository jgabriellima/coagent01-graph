#!/usr/bin/env python3
"""
TCE-PA Swarm System Demo
End-to-end demonstration of the production-grade multi-agent system
"""

import sys
import os
import datetime
from langchain_core.messages import HumanMessage
from pprint import pprint

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sample_agent.agents.tce_swarm.graph import tce_swarm_graph, health_check
from sample_agent.agents.tce_swarm.states import TCESwarmState


def run_demo():
    """Run comprehensive demo of the TCE swarm system"""
    
    print("=" * 80)
    print("🏛️  TCE-PA SWARM SYSTEM DEMO")
    print("=" * 80)
    
    # System health check
    print("\n🔍 1. SYSTEM HEALTH CHECK")
    print("-" * 40)
    health_status = health_check(tce_swarm_graph)
    pprint(health_status)
    
    if health_status["status"] != "healthy":
        print("❌ System is not healthy. Exiting demo.")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Legislação - Consulta sobre Teletrabalho",
            "query": "O teletrabalho pode ser estendido ou prorrogado no TCE-PA?",
            "expected_agent": "TCE_RAG_Agent",
            "description": "Deve ser roteado para o RAG Agent para buscar na base de conhecimento"
        },
        {
            "name": "Acordão - Consulta específica",
            "query": "Qual é o tema do Acórdão nº 192?",
            "expected_agent": "TCE_RAG_Agent",
            "description": "Deve ser roteado para o RAG Agent para buscar acordão específico"
        },
        {
            "name": "Expediente - Consulta processual",
            "query": "Do que trata o expediente 004506/2023?",
            "expected_agent": "TCE_Search_Agent",
            "description": "Deve ser roteado para o Search Agent para buscar no eTCE"
        },
        {
            "name": "Busca Web - Informações atuais",
            "query": "Últimas notícias sobre teletrabalho no TCE-PA",
            "expected_agent": "TCE_Search_Agent",
            "description": "Deve ser roteado para o Search Agent para busca web"
        },
        {
            "name": "Saudação - Interação inicial",
            "query": "Bom dia, qual seu nome?",
            "expected_agent": "TCE_Main_Agent",
            "description": "Deve ser tratado pelo Main Agent diretamente"
        }
    ]
    
    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 {i}. {test_case['name'].upper()}")
        print("-" * 50)
        print(f"Query: {test_case['query']}")
        print(f"Expected Agent: {test_case['expected_agent']}")
        print(f"Description: {test_case['description']}")
        
        try:
            # Create thread configuration
            thread_config = {
                "configurable": {
                    "thread_id": f"demo_test_{i}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            }
            
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=test_case['query'])],
                "username": "Demo User",
                "user_id": "demo_001",
                "current_date": datetime.datetime.now().isoformat(),
                "query": test_case['query'],
                "thread_mode": "demo",
                "task_type": "test_case"
            }
            
            # Run the workflow
            print("\n📤 Sending query to system...")
            response = tce_swarm_graph.invoke(initial_state, thread_config)
            
            # Display results
            print("\n📥 System Response:")
            print(f"Active Agent: {response.get('active_agent', 'Unknown')}")
            print(f"Query Type: {response.get('query_type', 'Unknown')}")
            print(f"Routing Decision: {response.get('routing_decision', 'Unknown')}")
            
            # Display final message
            if response.get('messages'):
                final_message = response['messages'][-1]
                print(f"\n💬 Final Response:")
                print(f"Content: {final_message.content[:200]}...")
                print(f"Type: {type(final_message).__name__}")
            
            # Display state information
            state_info = {
                "rag_result": response.get('rag_result', ''),
                "search_result": response.get('search_result', ''),
                "etce_results": len(response.get('etce_results', [])),
                "web_results": len(response.get('web_results', [])),
                "processing_time": response.get('processing_time', 0),
                "trace_id": response.get('trace_id', ''),
                "warnings": response.get('warnings', [])
            }
            
            print(f"\n📊 State Information:")
            for key, value in state_info.items():
                if value:  # Only show non-empty values
                    print(f"  {key}: {value}")
            
            # Validation
            actual_agent = response.get('active_agent', 'Unknown')
            if actual_agent == test_case['expected_agent']:
                print(f"\n✅ SUCCESS: Correctly routed to {actual_agent}")
            else:
                print(f"\n⚠️  NOTICE: Expected {test_case['expected_agent']}, got {actual_agent}")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 80)
    
    # System statistics
    print("\n📈 SYSTEM STATISTICS")
    print("-" * 40)
    
    try:
        # Get system metadata
        metadata = tce_swarm_graph.metadata
        print(f"System: {metadata.get('system_name', 'Unknown')}")
        print(f"Version: {metadata.get('version', 'Unknown')}")
        print(f"Architecture: {metadata.get('architecture', 'Unknown')}")
        print(f"Agents: {', '.join(metadata.get('agents', []))}")
        print(f"Created: {metadata.get('created_at', 'Unknown')}")
        
        # Capabilities
        capabilities = metadata.get('capabilities', {})
        print(f"\nCapabilities:")
        for cap, enabled in capabilities.items():
            status = "✅" if enabled else "❌"
            print(f"  {status} {cap}")
        
        # Tags
        tags = metadata.get('tags', [])
        print(f"\nTags: {', '.join(tags)}")
        
    except Exception as e:
        print(f"Error getting system statistics: {e}")
    
    print("\n🎉 Demo completed successfully!")
    print("=" * 80)


def interactive_demo():
    """Run interactive demo where user can input queries"""
    
    print("=" * 80)
    print("🏛️  TCE-PA INTERACTIVE DEMO")
    print("=" * 80)
    print("Type 'quit' to exit, 'help' for examples")
    
    # Example queries
    examples = [
        "O teletrabalho pode ser estendido no TCE-PA?",
        "Do que trata o expediente 004506/2023?",
        "Qual é o tema do Acórdão nº 192?",
        "Últimas notícias sobre o TCE-PA",
        "Bom dia, qual seu nome?"
    ]
    
    while True:
        try:
            query = input("\n🤖 Digite sua consulta: ").strip()
            
            if query.lower() == 'quit':
                print("👋 Encerrando demo interativo...")
                break
            
            if query.lower() == 'help':
                print("\n📋 Exemplos de consultas:")
                for i, example in enumerate(examples, 1):
                    print(f"  {i}. {example}")
                continue
            
            if not query:
                continue
            
            # Create thread configuration
            thread_config = {
                "configurable": {
                    "thread_id": f"interactive_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            }
            
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "username": "Interactive User",
                "user_id": "interactive_001",
                "current_date": datetime.datetime.now().isoformat(),
                "query": query,
                "thread_mode": "interactive",
                "task_type": "user_query"
            }
            
            print(f"\n🔄 Processando: {query}")
            response = tce_swarm_graph.invoke(initial_state, thread_config)
            
            # Display response
            if response.get('messages'):
                final_message = response['messages'][-1]
                print(f"\n💬 Chatcontas: {final_message.content}")
            
            # Display routing info
            print(f"\n📊 Info: Agent={response.get('active_agent', 'Unknown')}, "
                  f"Type={response.get('query_type', 'Unknown')}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Encerrando demo interativo...")
            break
        except Exception as e:
            print(f"\n❌ Erro: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        run_demo() 