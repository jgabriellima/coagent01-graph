#!/usr/bin/env python3
"""
Workflow Analyzer
================

Simple and objective workflow analysis utility using proper LangGraph API methods.
Uses get_graph() and get_subgraphs() for structured workflow inspection.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from openai import OpenAI
from langgraph.graph.state import CompiledStateGraph



@dataclass
class WorkflowAnalysisConfig:
    """Configuration for workflow analysis."""
    save_to_file: bool = True
    output_file: Optional[Path] = None
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.1


class ToolInfo(BaseModel):
    """Information about a tool available to an agent."""
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    is_handoff: bool = Field(description="Whether this tool is a handoff to another agent")


class AgentBlueprint(BaseModel):
    """Simplified agent blueprint focused on core workflow elements."""
    role: str = Field(description="Agent role or function")
    role_description: str = Field(description="Detailed description of agent's role")
    tools: List[ToolInfo] = Field(description="Tools available to this agent")
    handoffs: List[str] = Field(description="Other agents this agent can handoff to")


class WorkflowBlueprint(BaseModel):
    """Technical blueprint of a multi-agent workflow."""
    workflow_type: str = Field(description="Type of workflow (e.g., 'Multi-Agent Swarm', 'Sequential', 'Hierarchical')")
    description: str = Field(description="Description of the workflow")
    agents: Dict[str, AgentBlueprint] = Field(description="Dictionary of agent name to agent blueprint")
    agent_count: int = Field(description="Total number of agents")
    total_tools: int = Field(description="Total number of tools across all agents")


class WorkflowAnalyzer:
    """
    Objective workflow analyzer using proper LangGraph API methods.
    
    Uses get_graph() and get_subgraphs() for structured workflow inspection.
    """
    
    def __init__(self, config: WorkflowAnalysisConfig = None):
        """Initialize the workflow analyzer."""
        self.config = config or WorkflowAnalysisConfig()
        self.client = OpenAI()
    
    def analyze_workflow(self, workflow) -> WorkflowBlueprint:
        """
        Analyze a compiled LangGraph workflow and generate a technical blueprint.
        
        Args:
            workflow: Compiled LangGraph workflow
            
        Returns:
            WorkflowBlueprint: Technical blueprint of the workflow
        """
        # Use proper LangGraph API methods
        graph: CompiledStateGraph = workflow.get_graph()
        
        # Extract basic graph structure
        graph_data = self._extract_graph_data(graph)
        
        # Check for subgraphs
        subgraph_data = self._extract_subgraph_data(workflow)
        
        # Generate blueprint using LLM
        blueprint = self._generate_blueprint_with_llm(graph_data, subgraph_data)
        
        # Save to file if configured
        if self.config.save_to_file:
            self._save_blueprint(blueprint)
        
        return blueprint
    
    def _extract_graph_data(self, graph) -> Dict[str, Any]:
        """Extract graph data using proper LangGraph API."""
        # Get graph structure
        nodes = list(graph.nodes.keys()) if hasattr(graph, 'nodes') else []
        edges = list(graph.edges) if hasattr(graph, 'edges') else []
        
        # Try to get additional graph information
        graph_info = {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
        
        # Try to get node data if available
        if hasattr(graph, 'nodes'):
            node_data = {}
            for node_id in nodes:
                node_info = graph.nodes.get(node_id, {})
                node_data[node_id] = {
                    "id": node_id,
                    "data": str(node_info) if node_info else "No data available"
                }
            graph_info["node_data"] = node_data
        
        return graph_info
    
    def _extract_subgraph_data(self, workflow) -> Dict[str, Any]:
        """Extract subgraph data using get_subgraphs()."""
        subgraph_data = {"has_subgraphs": False, "subgraphs": []}
        
        try:
            # Use get_subgraphs() method
            subgraphs = workflow.get_subgraphs()
            if subgraphs:
                subgraph_data["has_subgraphs"] = True
                subgraph_data["subgraphs"] = [
                    {"name": name, "type": str(type(subgraph))}
                    for name, subgraph in subgraphs.items()
                ]
        except Exception as e:
            subgraph_data["error"] = str(e)
        
        return subgraph_data
    
    def _generate_blueprint_with_llm(self, graph_data: Dict[str, Any], subgraph_data: Dict[str, Any]) -> WorkflowBlueprint:
        """Generate workflow blueprint using LLM analysis."""
        
        # Prepare context for LLM
        context = {
            "graph_structure": graph_data,
            "subgraph_info": subgraph_data
        }
        
        prompt = f"""
        Analyze the following LangGraph workflow structure and generate a technical blueprint.
        
        Graph Structure:
        {json.dumps(context, indent=2)}
        
        Based on this information, create a technical blueprint that identifies:
        1. The workflow type (e.g., 'Multi-Agent Swarm', 'Sequential', 'Hierarchical')
        2. A description of the workflow
        3. Each agent's role and role description
        4. Tools available to each agent
        5. Handoff relationships between agents
        
        Focus on extracting meaningful information from the node names and structure.
        For tools, infer based on common patterns (e.g., nodes ending with '_tool', 'search', 'execute').
        For handoffs, identify transitions between different agent nodes.
        
        Return a structured analysis focusing on the workflow's technical architecture.
        """
        
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": "You are a technical analyst specializing in multi-agent workflow architecture."},
                    {"role": "user", "content": prompt}
                ],
                response_format=WorkflowBlueprint,
                temperature=self.config.llm_temperature
            )
            
            return response.parsed
            
        except Exception as e:
            # Fallback blueprint if LLM fails
            return self._create_fallback_blueprint(graph_data)
    
    def _create_fallback_blueprint(self, graph_data: Dict[str, Any]) -> WorkflowBlueprint:
        """Create a basic fallback blueprint if LLM analysis fails."""
        
        nodes = graph_data.get("nodes", [])
        
        # Create basic agents from nodes
        agents = {}
        for node in nodes:
            if node not in ["__start__", "__end__"]:
                agents[node] = AgentBlueprint(
                    role=node.replace("_", " ").title(),
                    role_description=f"Agent responsible for {node} functionality",
                    tools=[],
                    handoffs=[]
                )
        
        return WorkflowBlueprint(
            workflow_type="Multi-Agent Workflow",
            description="LangGraph workflow with multiple agents",
            agents=agents,
            agent_count=len(agents),
            total_tools=0
        )
    
    def _save_blueprint(self, blueprint: WorkflowBlueprint) -> None:
        """Save blueprint to file."""
        output_file = self.config.output_file or Path("workflow_blueprint.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(blueprint.model_dump(), f, indent=2, ensure_ascii=False)
        
        print(f"📁 Blueprint saved to: {output_file}")
    
    def print_blueprint(self, blueprint: WorkflowBlueprint) -> None:
        """Print blueprint in a formatted way."""
        print("🏗️  WORKFLOW BLUEPRINT")
        print("=" * 50)
        print(f"Type: {blueprint.workflow_type}")
        print(f"Description: {blueprint.description}")
        print(f"Agents: {blueprint.agent_count}")
        print(f"Total Tools: {blueprint.total_tools}")
        print()
        
        for agent_name, agent in blueprint.agents.items():
            print(f"🤖 Agent: {agent_name}")
            print(f"   Role: {agent.role}")
            print(f"   Description: {agent.role_description}")
            print(f"   Tools: {len(agent.tools)}")
            if agent.tools:
                for tool in agent.tools:
                    handoff_indicator = " (handoff)" if tool.is_handoff else ""
                    print(f"     • {tool.name}{handoff_indicator}")
            print(f"   Handoffs: {len(agent.handoffs)}")
            if agent.handoffs:
                for handoff in agent.handoffs:
                    print(f"     → {handoff}")
            print() 