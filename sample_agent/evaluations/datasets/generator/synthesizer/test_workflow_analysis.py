#!/usr/bin/env python3
"""
Teste Isolado para Análise de Workflow
-------------------------------------

Este teste permite analisar a estrutura de workflows de forma isolada,
extraindo informações detalhadas sobre agentes, ferramentas, capacidades
e estrutura geral do workflow.

Uso:
    python test_workflow_analysis.py
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Union, List
from pprint import pprint

# Adicionar o diretório raiz do projeto ao sys.path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sample_agent.evaluations.datasets.generator.synthesizer.base import (
    BaseSynthesizer, 
    SynthesizerConfig
)
from sample_agent.agents.swarm.graph import create_multi_agent_system_swarm_mode
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables import Runnable


class WorkflowAnalyzer(BaseSynthesizer):
    """Synthesizer específico para análise de workflow"""
    
    def __init__(self, config: SynthesizerConfig = None):
        if config is None:
            config = SynthesizerConfig(
                project_name="workflow-analysis-test",
                tags=["analysis", "isolated-test"],
                trace_metadata={"test_type": "workflow_analysis"},
                num_scenarios=1
            )
        super().__init__(config)
    
    async def generate_synthetic_dataset(self, workflow=None, num_scenarios=None):
        """Não implementado - usado apenas para análise"""
        return []
    
    def analyze_workflow_detailed(self, workflow: Union[CompiledStateGraph, Runnable]) -> Dict[str, Any]:
        """Análise detalhada do workflow com informações expandidas"""
        
        print("🔍 Iniciando análise detalhada do workflow...")
        
        # Usar a função base para análise
        analysis = self.analyze_workflow_structure(workflow)
        
        # Adicionar informações expandidas
        detailed_analysis = {
            **analysis,
            "detailed_agents": self._get_detailed_agent_info(analysis),
            "workflow_insights": self._generate_workflow_insights(analysis),
            "complexity_assessment": self._assess_workflow_complexity(analysis),
            "testing_recommendations": self._generate_testing_recommendations(analysis)
        }
        
        return detailed_analysis
    
    def _get_detailed_agent_info(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extrair informações detalhadas dos agentes"""
        
        agents = analysis.get("agents", {})
        detailed_agents = {}
        
        for agent_name, agent_info in agents.items():
            detailed_agents[agent_name] = {
                "name": agent_name,
                "capabilities": agent_info.get("capabilities", []),
                "tools": agent_info.get("tools", []),
                "prompt_info": agent_info.get("prompt_info"),
                "role_description": self._infer_agent_role(agent_name, agent_info),
                "interaction_patterns": self._analyze_agent_interactions(agent_name, analysis)
            }
        
        return detailed_agents
    
    def _infer_agent_role(self, agent_name: str, agent_info: Dict[str, Any]) -> str:
        """Inferir o papel do agente baseado nas informações"""
        
        capabilities = agent_info.get("capabilities", [])
        tools = agent_info.get("tools", [])
        
        if "math" in agent_name.lower() or any("math" in cap.lower() for cap in capabilities):
            return "Mathematical computation specialist"
        elif "weather" in agent_name.lower() or any("weather" in tool.lower() for tool in tools):
            return "Weather information provider"
        elif "main" in agent_name.lower() or "supervisor" in agent_name.lower():
            return "Task coordinator and orchestrator"
        elif "assistant" in agent_name.lower():
            return "General purpose assistant"
        else:
            return f"Specialized agent with {len(capabilities)} capabilities"
    
    def _analyze_agent_interactions(self, agent_name: str, analysis: Dict[str, Any]) -> List[str]:
        """Analisar padrões de interação do agente"""
        
        interactions = []
        
        # Baseado no nome e ferramentas, inferir interações
        if "main" in agent_name.lower():
            interactions.append("Receives initial user requests")
            interactions.append("Delegates tasks to specialized agents")
            interactions.append("Coordinates multi-agent workflows")
        
        agents = analysis.get("agents", {})
        if len(agents) > 1:
            interactions.append(f"Collaborates with {len(agents) - 1} other agents")
        
        return interactions
    
    def _generate_workflow_insights(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gerar insights sobre o workflow"""
        
        agents = analysis.get("agents", {})
        capabilities = analysis.get("capabilities", [])
        tools = analysis.get("tools", [])
        
        return {
            "agent_count": len(agents),
            "total_capabilities": len(capabilities),
            "total_tools": len(tools),
            "workflow_type": self._classify_workflow_type(analysis),
            "complexity_level": self._assess_complexity_level(analysis),
            "collaboration_pattern": self._identify_collaboration_pattern(analysis)
        }
    
    def _classify_workflow_type(self, analysis: Dict[str, Any]) -> str:
        """Classificar o tipo de workflow"""
        
        agents = analysis.get("agents", {})
        
        if len(agents) == 1:
            return "Single-agent workflow"
        elif len(agents) <= 3:
            return "Small multi-agent system"
        elif len(agents) <= 10:
            return "Medium multi-agent system"
        else:
            return "Large multi-agent system"
    
    def _assess_complexity_level(self, analysis: Dict[str, Any]) -> str:
        """Avaliar nível de complexidade"""
        
        agents = analysis.get("agents", {})
        tools = analysis.get("tools", [])
        capabilities = analysis.get("capabilities", [])
        
        complexity_score = len(agents) * 2 + len(tools) + len(capabilities)
        
        if complexity_score <= 5:
            return "Low complexity"
        elif complexity_score <= 15:
            return "Medium complexity"
        else:
            return "High complexity"
    
    def _identify_collaboration_pattern(self, analysis: Dict[str, Any]) -> str:
        """Identificar padrão de colaboração"""
        
        agents = analysis.get("agents", {})
        
        if len(agents) == 1:
            return "No collaboration (single agent)"
        elif any("main" in name.lower() for name in agents.keys()):
            return "Hub-and-spoke (coordinator pattern)"
        else:
            return "Peer-to-peer collaboration"
    
    def _assess_workflow_complexity(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Avaliar complexidade do workflow"""
        
        agents = analysis.get("agents", {})
        tools = analysis.get("tools", [])
        capabilities = analysis.get("capabilities", [])
        
        return {
            "agent_complexity": {
                "count": len(agents),
                "assessment": "High" if len(agents) > 5 else "Medium" if len(agents) > 2 else "Low"
            },
            "tool_complexity": {
                "count": len(tools),
                "assessment": "High" if len(tools) > 10 else "Medium" if len(tools) > 5 else "Low"
            },
            "capability_complexity": {
                "count": len(capabilities),
                "assessment": "High" if len(capabilities) > 15 else "Medium" if len(capabilities) > 8 else "Low"
            },
            "overall_complexity": self._assess_complexity_level(analysis)
        }
    
    def _generate_testing_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gerar recomendações para testes"""
        
        agents = analysis.get("agents", {})
        tools = analysis.get("tools", [])
        
        recommendations = {
            "unit_tests": [],
            "integration_tests": [],
            "performance_tests": [],
            "edge_cases": []
        }
        
        # Recomendações para testes unitários
        for agent_name in agents.keys():
            recommendations["unit_tests"].append(f"Test {agent_name} individual capabilities")
        
        # Recomendações para testes de integração
        if len(agents) > 1:
            recommendations["integration_tests"].append("Test agent handoff mechanisms")
            recommendations["integration_tests"].append("Test multi-agent coordination")
        
        # Recomendações para ferramentas
        for tool in tools:
            recommendations["unit_tests"].append(f"Test {tool} tool functionality")
        
        # Recomendações para casos extremos
        recommendations["edge_cases"].append("Test with invalid inputs")
        recommendations["edge_cases"].append("Test with concurrent requests")
        
        if len(agents) > 1:
            recommendations["edge_cases"].append("Test with agent failures")
        
        return recommendations


def print_analysis_report(analysis: Dict[str, Any]) -> None:
    """Imprimir relatório de análise formatado"""
    
    print("\n" + "="*80)
    print("🔬 RELATÓRIO DE ANÁLISE DE WORKFLOW")
    print("="*80)
    
    # Informações básicas
    print(f"\n📊 INFORMAÇÕES BÁSICAS:")
    print(f"   • Tipo: {analysis.get('type', 'Desconhecido')}")
    print(f"   • Descrição: {analysis.get('workflow_description', 'N/A')}")
    
    # Insights do workflow
    insights = analysis.get("workflow_insights", {})
    if insights:
        print(f"\n💡 INSIGHTS DO WORKFLOW:")
        print(f"   • Número de agentes: {insights.get('agent_count', 0)}")
        print(f"   • Total de capacidades: {insights.get('total_capabilities', 0)}")
        print(f"   • Total de ferramentas: {insights.get('total_tools', 0)}")
        print(f"   • Tipo de workflow: {insights.get('workflow_type', 'N/A')}")
        print(f"   • Nível de complexidade: {insights.get('complexity_level', 'N/A')}")
        print(f"   • Padrão de colaboração: {insights.get('collaboration_pattern', 'N/A')}")
    
    # Agentes detalhados
    detailed_agents = analysis.get("detailed_agents", {})
    if detailed_agents:
        print(f"\n🤖 AGENTES DETALHADOS:")
        for agent_name, agent_info in detailed_agents.items():
            print(f"\n   📋 {agent_name}:")
            print(f"      • Papel: {agent_info.get('role_description', 'N/A')}")
            print(f"      • Capacidades: {len(agent_info.get('capabilities', []))}")
            print(f"      • Ferramentas: {agent_info.get('tools', [])}")
            
            interactions = agent_info.get('interaction_patterns', [])
            if interactions:
                print(f"      • Padrões de interação:")
                for interaction in interactions:
                    print(f"        - {interaction}")
    
    # Avaliação de complexidade
    complexity = analysis.get("complexity_assessment", {})
    if complexity:
        print(f"\n📈 AVALIAÇÃO DE COMPLEXIDADE:")
        print(f"   • Complexidade geral: {complexity.get('overall_complexity', 'N/A')}")
        
        agent_complexity = complexity.get('agent_complexity', {})
        if agent_complexity:
            print(f"   • Agentes: {agent_complexity.get('count', 0)} ({agent_complexity.get('assessment', 'N/A')})")
        
        tool_complexity = complexity.get('tool_complexity', {})
        if tool_complexity:
            print(f"   • Ferramentas: {tool_complexity.get('count', 0)} ({tool_complexity.get('assessment', 'N/A')})")
        
        capability_complexity = complexity.get('capability_complexity', {})
        if capability_complexity:
            print(f"   • Capacidades: {capability_complexity.get('count', 0)} ({capability_complexity.get('assessment', 'N/A')})")
    
    # Recomendações de testes
    recommendations = analysis.get("testing_recommendations", {})
    if recommendations:
        print(f"\n🧪 RECOMENDAÇÕES DE TESTES:")
        
        for test_type, tests in recommendations.items():
            if tests:
                print(f"\n   {test_type.replace('_', ' ').title()}:")
                for test in tests[:3]:  # Limitar a 3 para não sobrecarregar
                    print(f"      • {test}")
                if len(tests) > 3:
                    print(f"      • ... e mais {len(tests) - 3} recomendações")
    
    # Dados brutos (opcional)
    print(f"\n📋 CAPACIDADES IDENTIFICADAS:")
    capabilities = analysis.get("capabilities", [])
    if capabilities:
        for cap in capabilities[:10]:  # Limitar a 10
            print(f"   • {cap}")
        if len(capabilities) > 10:
            print(f"   • ... e mais {len(capabilities) - 10} capacidades")
    
    print(f"\n🔧 FERRAMENTAS IDENTIFICADAS:")
    tools = analysis.get("tools", [])
    if tools:
        for tool in tools:
            print(f"   • {tool}")
    else:
        print("   • Nenhuma ferramenta identificada")
    
    print("\n" + "="*80)


async def test_workflow_analysis():
    """Teste principal para análise de workflow"""
    
    print("🚀 Iniciando teste de análise de workflow...")
    
    # Criar analisador
    analyzer = WorkflowAnalyzer()
    
    # Criar workflow de exemplo
    print("📝 Criando workflow de exemplo...")
    workflow = create_multi_agent_system_swarm_mode()
    
    # Analisar workflow
    print("🔍 Analisando estrutura do workflow...")
    analysis = analyzer.analyze_workflow_detailed(workflow)
    
    # Imprimir relatório
    print_analysis_report(analysis)
    
    # Salvar análise em arquivo JSON (opcional)
    output_file = Path("workflow_analysis_result.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Análise salva em: {output_file}")
    print("✅ Teste de análise de workflow concluído!")


if __name__ == "__main__":
    asyncio.run(test_workflow_analysis()) 