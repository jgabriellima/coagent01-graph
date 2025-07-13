#!/usr/bin/env python3
"""
Workflow Analyzer
================

Simple workflow analysis utility to extract node names, tools, and agent prompts from LangGraph workflows.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field


@dataclass
class WorkflowAnalysisConfig:
    """Configuration for workflow analysis."""
    save_to_file: bool = True
    output_file: Optional[Path] = None


class ToolInfo(BaseModel):
    """Information about a tool available to an agent."""
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")


class NodeInfo(BaseModel):
    """Information about a workflow node."""
    name: str = Field(description="Node name")
    node_type: str = Field(description="Type of node")
    tools: List[ToolInfo] = Field(description="Tools available to this node")
    prompt: Optional[str] = Field(description="Agent prompt if it's a react agent")


class WorkflowAnalysis(BaseModel):
    """Analysis result of a workflow."""
    total_nodes: int = Field(description="Total number of nodes")
    nodes: List[NodeInfo] = Field(description="List of nodes with their information")


class WorkflowAnalyzer:
    """
    Simple workflow analyzer to extract essential information from LangGraph workflows.
    """
    
    def __init__(self, config: WorkflowAnalysisConfig = None):
        """Initialize the workflow analyzer."""
        self.config = config or WorkflowAnalysisConfig()
    
    def analyze_workflow(self, workflow) -> WorkflowAnalysis:
        """
        Analyze a compiled LangGraph workflow and extract node information.
        
        Args:
            workflow: Compiled LangGraph workflow
            
        Returns:
            WorkflowAnalysis: Analysis result with node information
        """
        # Get the graph from the workflow
        graph = workflow.get_graph()
        
        # Extract node information
        nodes = self._extract_nodes_info(graph, workflow)
        
        # Create analysis result
        analysis = WorkflowAnalysis(
            total_nodes=len(nodes),
            nodes=nodes
        )
        
        # Save to file if configured
        if self.config.save_to_file:
            self._save_analysis(analysis)
        
        return analysis
    
    def _extract_nodes_info(self, graph, workflow) -> List[NodeInfo]:
        """Extract information from all nodes in the graph."""
        nodes_info = []
        
        # Get all nodes from the graph
        for node_id in graph.nodes:
            # Skip special nodes
            if node_id in ["__start__", "__end__"]:
                continue
            
            node_info = self._analyze_node(node_id, graph, workflow)
            nodes_info.append(node_info)
        
        return nodes_info
    
    def _analyze_node(self, node_id: str, graph, workflow) -> NodeInfo:
        """Analyze a single node to extract its information."""
        # Get the node object from the graph
        node_obj = graph.nodes.get(node_id)
        
        # Extract basic node information
        node_info = NodeInfo(
            name=node_id,
            node_type=self._get_node_type(node_obj),
            tools=[],
            prompt=None
        )
        
        # Try to extract tools and prompt from the node
        try:
            # Get the actual runnable data from the node
            runnable_data = getattr(node_obj, 'data', None)
            if runnable_data:
                # Check if this is a CompiledStateGraph (subgraph)
                if hasattr(runnable_data, 'nodes') and hasattr(runnable_data, 'builder'):
                    # This is a subgraph - extract tools and prompts from its nodes
                    tools, prompt = self._extract_from_subgraph(runnable_data)
                    node_info.tools = tools
                    node_info.prompt = prompt
                else:
                    # This is a regular runnable - extract directly
                    tools = self._extract_tools_from_node(runnable_data)
                    node_info.tools = tools
                    
                    prompt = self._extract_prompt_from_node(runnable_data)
                    node_info.prompt = prompt
        
        except Exception as e:
            # If extraction fails, log and continue
            print(f"Warning: Could not extract details from node {node_id}: {e}")
        
        return node_info
    
    def _extract_from_subgraph(self, subgraph) -> tuple[List[ToolInfo], Optional[str]]:
        """Extract tools and prompts from a subgraph."""
        tools = []
        prompt = None
        
        try:
            # Get the builder to access the original graph structure
            builder = getattr(subgraph, 'builder', None)
            if builder:
                # Access the nodes dict from the builder
                nodes_dict = getattr(builder, 'nodes', {})
                
                for node_name, node_spec in nodes_dict.items():
                    # Get the runnable from the StateNodeSpec
                    runnable = getattr(node_spec, 'runnable', None)
                    if runnable:
                        # Extract tools from the runnable
                        node_tools = self._extract_tools_from_runnable(runnable)
                        tools.extend(node_tools)
                        
                        # Extract prompt from the runnable (keep the first one found)
                        if not prompt:
                            node_prompt = self._extract_prompt_from_runnable(runnable)
                            if node_prompt:
                                prompt = node_prompt
        
        except Exception as e:
            print(f"Warning: Could not extract from subgraph: {e}")
        
        return tools, prompt
    
    def _extract_tools_from_runnable(self, runnable) -> List[ToolInfo]:
        """Extract tools from a runnable object."""
        tools = []
        
        try:
            # Check if it's a ToolNode (has tools_by_name)
            if hasattr(runnable, 'tools_by_name'):
                tools_dict = runnable.tools_by_name
                for tool_name, tool_obj in tools_dict.items():
                    tool_info = ToolInfo(
                        name=tool_name,
                        description=getattr(tool_obj, 'description', 'No description available')
                    )
                    tools.append(tool_info)
            
            # Check if the runnable has tools attribute
            elif hasattr(runnable, 'tools') and runnable.tools:
                for tool in runnable.tools:
                    tool_info = ToolInfo(
                        name=getattr(tool, 'name', str(tool)),
                        description=getattr(tool, 'description', 'No description available')
                    )
                    tools.append(tool_info)
            
            # Check if it's a bind_tools result (common pattern)
            elif hasattr(runnable, 'bound') and hasattr(runnable, 'kwargs'):
                bound_tools = runnable.kwargs.get('tools', [])
                for tool in bound_tools:
                    tool_info = ToolInfo(
                        name=getattr(tool, 'name', str(tool)),
                        description=getattr(tool, 'description', 'No description available')
                    )
                    tools.append(tool_info)
            
            # Check if it's a sequence/chain with tools
            elif hasattr(runnable, 'steps'):
                for step in runnable.steps:
                    if hasattr(step, 'tools') and step.tools:
                        for tool in step.tools:
                            tool_info = ToolInfo(
                                name=getattr(tool, 'name', str(tool)),
                                description=getattr(tool, 'description', 'No description available')
                            )
                            tools.append(tool_info)
            
            # Check for tools in runnable dict
            elif hasattr(runnable, '__dict__'):
                for attr_name, attr_value in runnable.__dict__.items():
                    if 'tool' in attr_name.lower() and isinstance(attr_value, dict):
                        # This might be a tools dictionary
                        for tool_name, tool_obj in attr_value.items():
                            if hasattr(tool_obj, 'name') or hasattr(tool_obj, '__name__'):
                                tool_info = ToolInfo(
                                    name=getattr(tool_obj, 'name', getattr(tool_obj, '__name__', str(tool_obj))),
                                    description=getattr(tool_obj, 'description', 'No description available')
                                )
                                tools.append(tool_info)
                    elif 'tool' in attr_name.lower() and hasattr(attr_value, '__iter__') and not isinstance(attr_value, str):
                        try:
                            for tool in attr_value:
                                if hasattr(tool, 'name'):
                                    tool_info = ToolInfo(
                                        name=tool.name,
                                        description=getattr(tool, 'description', 'No description available')
                                    )
                                    tools.append(tool_info)
                        except:
                            continue
        
        except Exception as e:
            print(f"Warning: Could not extract tools from runnable: {e}")
        
        return tools
    
    def _extract_prompt_from_runnable(self, runnable) -> Optional[str]:
        """Extract prompt from a runnable object."""
        try:
            # Check if it's a RunnableCallable with a func
            if hasattr(runnable, 'func') and hasattr(runnable.func, '__name__'):
                func_name = runnable.func.__name__
                if 'agent' in func_name.lower():
                    # This might be the agent function - try to get its docstring
                    func_doc = getattr(runnable.func, '__doc__', None)
                    if func_doc:
                        return func_doc.strip()
            
            # Check common attributes where prompts might be stored
            prompt_attrs = ['prompt', 'system_prompt', 'system_message', 'template']
            
            for attr in prompt_attrs:
                if hasattr(runnable, attr):
                    prompt_value = getattr(runnable, attr)
                    if prompt_value:
                        return str(prompt_value)
            
            # Check in nested structures
            if hasattr(runnable, '__dict__'):
                for attr_name, attr_value in runnable.__dict__.items():
                    if 'prompt' in attr_name.lower() and attr_value:
                        return str(attr_value)
            
            # Check if it's a composed runnable with prompt
            if hasattr(runnable, 'first') and hasattr(runnable.first, 'template'):
                return str(runnable.first.template)
            
            # Check if it's a sequence/chain with prompt
            if hasattr(runnable, 'steps') and runnable.steps:
                for step in runnable.steps:
                    if hasattr(step, 'template'):
                        return str(step.template)
                    if hasattr(step, 'messages'):
                        messages = []
                        for msg in step.messages:
                            if hasattr(msg, 'content'):
                                messages.append(f"{msg.__class__.__name__}: {msg.content}")
                            elif hasattr(msg, 'template'):
                                messages.append(f"{msg.__class__.__name__}: {msg.template}")
                        if messages:
                            return "\n".join(messages)
            
            # Check for messages in case of ChatPromptTemplate
            if hasattr(runnable, 'messages'):
                messages = []
                for msg in runnable.messages:
                    if hasattr(msg, 'content'):
                        messages.append(f"{msg.__class__.__name__}: {msg.content}")
                    elif hasattr(msg, 'template'):
                        messages.append(f"{msg.__class__.__name__}: {msg.template}")
                if messages:
                    return "\n".join(messages)
        
        except Exception as e:
            print(f"Warning: Could not extract prompt from runnable: {e}")
        
        return None
    
    def _extract_tools_from_node(self, runnable_data) -> List[ToolInfo]:
        """Extract tools from a runnable data object."""
        # Use the new method for consistency
        return self._extract_tools_from_runnable(runnable_data)
    
    def _extract_prompt_from_node(self, runnable_data) -> Optional[str]:
        """Extract prompt from a runnable data object."""
        # Use the new method for consistency
        return self._extract_prompt_from_runnable(runnable_data)
    
    def _get_node_type(self, node_obj) -> str:
        """Determine the type of a node based on its object."""
        if not node_obj:
            return "unknown"
        
        # Try to get the actual runnable data
        runnable_data = getattr(node_obj, 'data', None)
        if runnable_data:
            data_type = str(type(runnable_data))
            
            # Look for common patterns in the type string
            if 'CompiledStateGraph' in data_type:
                return "subgraph"
            elif 'Agent' in data_type or 'agent' in data_type:
                return "agent"
            elif 'Tool' in data_type or 'tool' in data_type:
                return "tool"
            elif 'Runnable' in data_type or 'runnable' in data_type:
                return "runnable"
            elif 'Executor' in data_type or 'executor' in data_type:
                return "executor"
        
        # Fallback to node type
        node_type = str(type(node_obj))
        if 'Node' in node_type:
            return "node"
        
        return "unknown"
    
    def _save_analysis(self, analysis: WorkflowAnalysis) -> None:
        """Save analysis to file."""
        output_file = self.config.output_file or Path("workflow_analysis.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis.model_dump(), f, indent=2, ensure_ascii=False)
        
        print(f"📁 Analysis saved to: {output_file}")
    
    def print_analysis(self, analysis: WorkflowAnalysis) -> None:
        """Print analysis in a formatted way."""
        print("🔍 WORKFLOW ANALYSIS")
        print("=" * 50)
        print(f"Total Nodes: {analysis.total_nodes}")
        print()
        
        for node in analysis.nodes:
            print(f"📦 Node: {node.name}")
            print(f"   Type: {node.node_type}")
            print(f"   Tools: {len(node.tools)}")
            
            if node.tools:
                for tool in node.tools:
                    print(f"     🔧 {tool.name}: {tool.description}")
            
            if node.prompt:
                print(f"   Prompt: {node.prompt[:100]}{'...' if len(node.prompt) > 100 else ''}")
            
            print() 