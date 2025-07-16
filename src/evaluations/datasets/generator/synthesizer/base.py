#!/usr/bin/env python3
"""
Base Synthesizer Interface
--------------------------

Unified interface for all synthetic data generators with workflow analysis capabilities.
"""

import os
import json
import uuid
import inspect
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Protocol
from dataclasses import dataclass
from datetime import datetime
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from langsmith import Client
from langchain_core.runnables import Runnable
from langgraph.graph.state import CompiledStateGraph


@dataclass
class SynthesizerConfig:
    """Configuration for synthetic data generation"""

    project_name: str
    tags: List[str]
    trace_metadata: Dict[str, Any]
    model_name: str = "openai:gpt-4o-mini"
    temperature: float = 0.7
    num_scenarios: int = 20


@dataclass
class SyntheticExample:
    """A single synthetic example"""

    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    metadata: Dict[str, Any]


class DatasetPersistence(Protocol):
    """Protocol for dataset persistence providers"""

    async def save_dataset(
        self, examples: List[SyntheticExample], project_name: str
    ) -> bool:
        """Save synthetic dataset to persistence provider"""
        ...


class LangSmithPersistence:
    """LangSmith-specific persistence implementation"""

    def __init__(self):
        self.client = None
        self.setup_client()

    def setup_client(self):
        """Setup LangSmith client"""
        try:
            self.client = Client()
            print("✅ LangSmith persistence client configured")
        except Exception as e:
            print(f"⚠️  LangSmith client setup failed: {e}")

    async def save_dataset(
        self, examples: List[SyntheticExample], project_name: str
    ) -> bool:
        """Save synthetic dataset to LangSmith"""
        if not self.client:
            print("❌ No LangSmith client available")
            return False

        try:
            # Create dataset name with timestamp
            dataset_name = (
                f"{project_name}-synthetic-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Prepare examples for LangSmith
            dataset_examples = []
            for example in examples:
                dataset_examples.append(
                    {
                        "inputs": example.input_data,
                        "outputs": example.expected_output,
                        "metadata": example.metadata,
                    }
                )

            # Create dataset
            dataset = self.client.create_dataset(
                dataset_name=dataset_name,
                description=f"Synthetic dataset for {project_name}",
            )

            # Add examples to dataset
            self.client.create_examples(
                inputs=[ex["inputs"] for ex in dataset_examples],
                outputs=[ex["outputs"] for ex in dataset_examples],
                metadata=[ex["metadata"] for ex in dataset_examples],
                dataset_id=dataset.id,
            )

            print(
                f"✅ Saved {len(examples)} examples to LangSmith dataset: {dataset_name}"
            )
            return True

        except Exception as e:
            print(f"❌ Failed to save dataset to LangSmith: {e}")
            return False


class BaseSynthesizer(ABC):
    """Base class for all synthetic data generators"""

    def __init__(
        self, config: SynthesizerConfig, persistence: DatasetPersistence = None
    ):
        self.config = config
        self.persistence = persistence or LangSmithPersistence()
        self.model = init_chat_model(config.model_name, temperature=config.temperature)
        self.setup_langsmith()

    def setup_langsmith(self):
        """Setup LangSmith for trace collection"""
        os.environ["LANGSMITH_PROJECT"] = self.config.project_name
        os.environ["LANGCHAIN_TRACING_V2"] = "true"

        try:
            self.langsmith_client = Client()
            print(f"✅ LangSmith configured - Project: {self.config.project_name}")
        except Exception as e:
            print(f"⚠️  LangSmith setup failed: {e}")
            self.langsmith_client = None

    def analyze_workflow_structure(
        self, workflow: Union[CompiledStateGraph, Runnable]
    ) -> Dict[str, Any]:
        """Analyze workflow structure to extract context information"""

        if isinstance(workflow, CompiledStateGraph):
            return self._analyze_compiled_graph(workflow)
        else:
            return self._analyze_runnable(workflow)

    def _analyze_compiled_graph(self, graph: CompiledStateGraph) -> Dict[str, Any]:
        """Analyze CompiledStateGraph structure"""
        context = {
            "type": "CompiledStateGraph",
            "agents": {},
            "capabilities": [],
            "tools": [],
            "workflow_description": "",
        }

        try:
            # Try different ways to access nodes
            nodes = None

            # Method 1: Direct access to nodes attribute
            if hasattr(graph, "nodes"):
                nodes = graph.nodes

            # Method 2: Access via builder
            elif hasattr(graph, "builder") and hasattr(graph.builder, "nodes"):
                nodes = graph.builder.nodes

            # Method 3: Access via internal graph
            elif hasattr(graph, "graph") and hasattr(graph.graph, "nodes"):
                nodes = graph.graph.nodes

            # Method 4: Get graph representation
            elif hasattr(graph, "get_graph"):
                try:
                    graph_repr = graph.get_graph()
                    if hasattr(graph_repr, "nodes"):
                        nodes = graph_repr.nodes
                except Exception:
                    pass

            if nodes:
                context["node_count"] = len(nodes)

                # Analyze each node
                for node_name, node_data in nodes.items():
                    if node_name not in ["__start__", "__end__"]:
                        agent_info = self._extract_agent_info(node_name, node_data)
                        if agent_info:
                            context["agents"][node_name] = agent_info
                            context["capabilities"].extend(
                                agent_info.get("capabilities", [])
                            )
                            context["tools"].extend(agent_info.get("tools", []))

            # Extract state schema
            if hasattr(graph, "state_schema"):
                context["state_fields"] = (
                    list(graph.state_schema.__annotations__.keys())
                    if hasattr(graph.state_schema, "__annotations__")
                    else []
                )

            # Generate workflow description
            context["workflow_description"] = self._generate_workflow_description(
                context
            )

        except Exception as e:
            print(f"⚠️  Error analyzing graph structure: {e}")
            context["workflow_description"] = "Multi-agent workflow system"

        return context

    def _analyze_runnable(self, runnable: Runnable) -> Dict[str, Any]:
        """Analyze generic Runnable structure"""
        context = {
            "type": "Runnable",
            "class_name": runnable.__class__.__name__,
            "capabilities": [],
            "workflow_description": "",
        }

        # Try to extract information from runnable
        if hasattr(runnable, "steps"):
            context["steps"] = len(runnable.steps)

        if hasattr(runnable, "llm"):
            context["has_llm"] = True

        context["workflow_description"] = f"{context['class_name']} workflow system"

        return context

    def _extract_agent_info(self, node_name: str, node_data: Any) -> Dict[str, Any]:
        """Extract information from a graph node/agent through deep introspection"""
        agent_info = {
            "name": node_name,
            "capabilities": [],
            "tools": [],
            "prompt_info": None,
            "raw_data": {},
        }

        try:
            # Deep introspection of node structure
            raw_info = self._deep_extract_node_info(node_data)
            agent_info["raw_data"] = raw_info
            
            # Extract basic info first
            if hasattr(node_data, "func"):
                func = node_data.func
                agent_info["capabilities"].append(f"executes_{func.__name__}")
                
                if func.__doc__:
                    agent_info["prompt_info"] = func.__doc__.strip()

            # Extract tools and capabilities from raw data
            tools_found = self._extract_tools_from_raw_data(raw_info)
            capabilities_found = self._extract_capabilities_from_raw_data(raw_info)
            prompt_content = self._extract_prompt_content_from_raw_data(raw_info)
            
            if tools_found:
                agent_info["tools"].extend(tools_found)
            if capabilities_found:
                agent_info["capabilities"].extend(capabilities_found)
            if prompt_content and not agent_info["prompt_info"]:
                agent_info["prompt_info"] = prompt_content

            # If we have meaningful data, use LLM to enhance analysis
            if agent_info["prompt_info"] or agent_info["tools"] or len(agent_info["capabilities"]) > 1:
                enhanced_info = self._llm_analyze_agent_info(agent_info)
                if enhanced_info:
                    agent_info.update(enhanced_info)

            return agent_info

        except Exception as e:
            print(f"⚠️  Error extracting agent info for {node_name}: {e}")
            agent_info["capabilities"] = [f"node_execution"]
            return agent_info

    def _generate_workflow_description(self, context: Dict[str, Any]) -> str:
        """Generate comprehensive workflow description using LLM analysis"""
        agents = context.get("agents", {})
        capabilities = context.get("capabilities", [])

        if not agents:
            return "Generic workflow system"

        # Enhanced agent descriptions using LLM analysis results
        agent_descriptions = []
        for agent_name, agent_info in agents.items():
            # Use enhanced descriptions if available
            if agent_info.get("agent_purpose"):
                agent_descriptions.append(f"{agent_name}: {agent_info['agent_purpose']}")
            elif agent_info.get("role_description"):
                agent_descriptions.append(f"{agent_name} ({agent_info['role_description']})")
            else:
                # Fallback to capabilities
                caps = ", ".join(agent_info.get("capabilities", []))
                if caps and caps != "node_execution":
                    agent_descriptions.append(f"{agent_name} ({caps})")
                else:
                    agent_descriptions.append(agent_name)

        description = f"Multi-agent workflow system with {len(agents)} specialized agents: {'. '.join(agent_descriptions)}"

        # Add system-level capabilities if meaningful
        if capabilities:
            unique_caps = [cap for cap in set(capabilities) if cap != "node_execution"]
            if unique_caps:
                description += f". Core system capabilities: {', '.join(unique_caps)}"

        return description

    async def generate_scenarios_from_workflow(
        self, workflow_context: Dict[str, Any], num_scenarios: int = None
    ) -> List[Dict[str, Any]]:
        """Generate scenarios based on workflow structure analysis"""
        num_scenarios = num_scenarios or self.config.num_scenarios

        prompt = f"""
Based on the following workflow analysis, generate {num_scenarios} diverse test scenarios:

WORKFLOW ANALYSIS:
- Type: {workflow_context.get('type', 'Unknown')}
- Description: {workflow_context.get('workflow_description', 'Generic workflow')}
- Agents: {list(workflow_context.get('agents', {}).keys())}
- Capabilities: {workflow_context.get('capabilities', [])}
- Available Tools: {workflow_context.get('tools', [])}

AGENT DETAILS:
{json.dumps(workflow_context.get('agents', {}), indent=2)}

Generate realistic user scenarios that would exercise this workflow system:
- Vary complexity (simple to complex)
- Include edge cases
- Exercise different agents and capabilities
- Create realistic user interaction patterns
- Test tool usage scenarios

Format as JSON array:
[
  {{
    "user_input": "realistic user request that matches workflow capabilities",
    "expected_behavior": "what should happen in the workflow",
    "complexity": "simple|medium|complex|edge",
    "target_agents": ["list", "of", "agents", "expected", "to", "be", "involved"],
    "required_tools": ["list", "of", "tools", "expected", "to", "be", "used"],
    "context": {{"key": "value"}}
  }}
]

Return only valid JSON.
"""

        try:
            response = await self.model.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # Clean JSON from markdown
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]

            scenarios = json.loads(content)
            return scenarios

        except Exception as e:
            print(f"⚠️  Scenario generation failed: {e}")
            return []

    def _standardize_output(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize output to expected format"""
        standardized = {"messages": raw_output.get("messages", [])}

        # Add custom state data (everything except messages)
        for key, value in raw_output.items():
            if key != "messages":
                standardized[key] = value

        return standardized

    async def persist_dataset(self, examples: List[SyntheticExample]) -> bool:
        """Persist synthetic dataset using configured persistence provider"""
        return await self.persistence.save_dataset(examples, self.config.project_name)

    def _deep_extract_node_info(self, node_data: Any) -> Dict[str, Any]:
        """Deep extraction of all available information from a node, focusing on actual agent tools"""
        raw_info = {
            "type": str(type(node_data)),
            "attributes": {},
            "methods": [],
            "nested_data": {},
            "tools": [],
            "capabilities": [],
        }
        
        try:
            # Extract all attributes - but filter out LangGraph infrastructure
            if hasattr(node_data, "__dict__"):
                for attr_name, attr_value in node_data.__dict__.items():
                    if not attr_name.startswith("_") and attr_name not in [
                        "metadata", "tags", "triggers", "channels", "retry_policy", 
                        "mapper", "cache_policy", "subgraphs", "bound", "writers"
                    ]:
                        raw_info["attributes"][attr_name] = self._safe_extract_value(attr_value)
            
            # Extract methods
            raw_info["methods"] = [method for method in dir(node_data) 
                                  if callable(getattr(node_data, method, None)) and not method.startswith("_")]
            
            # Try to extract nested CompiledStateGraph data
            actual_func = None
            
            # For PregelNode objects, look for the actual function
            if hasattr(node_data, "func") and node_data.func:
                actual_func = node_data.func
            elif hasattr(node_data, "_func"):
                actual_func = node_data._func
            elif hasattr(node_data, "bound"):
                # Look deeper into bound objects
                bound_obj = node_data.bound
                
                # Check if bound object has builder with original nodes
                if hasattr(bound_obj, "builder") and hasattr(bound_obj.builder, "nodes"):
                    builder_nodes = bound_obj.builder.nodes
                    
                    # For 'tools' node, extract tools from compiled node
                    if "tools" in builder_nodes:
                        compiled_nodes = bound_obj.nodes
                        if "tools" in compiled_nodes:
                            tools_node = compiled_nodes["tools"]
                            
                            # Check if compiled tools node has bound tools
                            if hasattr(tools_node, "bound"):
                                bound_str = str(tools_node.bound)
                                # Parse tools_by_name from bound string
                                if "tools_by_name=" in bound_str:
                                    tools_section = bound_str.split("tools_by_name=")[1].split("}")[0] + "}"
                                    try:
                                        # Extract tool names from the dictionary-like structure
                                        import re
                                        tool_names = re.findall(r"'([^']+)':\s*StructuredTool", tools_section)
                                        for tool_name in tool_names:
                                            raw_info["tools"].append(tool_name)
                                    except:
                                        pass
                
                if hasattr(bound_obj, "func"):
                    actual_func = bound_obj.func
                elif hasattr(bound_obj, "_func"):
                    actual_func = bound_obj._func
            
            if actual_func:
                raw_info["nested_data"]["function_name"] = actual_func.__name__
                raw_info["nested_data"]["function_doc"] = actual_func.__doc__
                
                # Try to get closure variables (tools, model bindings, etc.)
                if hasattr(actual_func, "__closure__") and actual_func.__closure__:
                    closure_info = {}
                    for i, cell in enumerate(actual_func.__closure__):
                        try:
                            cell_content = cell.cell_contents
                            closure_info[f"closure_{i}"] = self._safe_extract_value(cell_content)
                            
                            # Look for tools in closure
                            if hasattr(cell_content, "__name__") and callable(cell_content):
                                raw_info["tools"].append(cell_content.__name__)
                            elif isinstance(cell_content, list):
                                # Look for tool lists
                                for item in cell_content:
                                    if hasattr(item, "__name__") and callable(item):
                                        raw_info["tools"].append(item.__name__)
                        except:
                            closure_info[f"closure_{i}"] = "inaccessible"
                    raw_info["nested_data"]["closure"] = closure_info
                
                # Try introspection
                try:
                    import inspect
                    if hasattr(actual_func, "__code__"):
                        raw_info["nested_data"]["code_vars"] = actual_func.__code__.co_varnames
                        raw_info["nested_data"]["code_names"] = actual_func.__code__.co_names
                except:
                    pass
                    
        except Exception as e:
            raw_info["extraction_error"] = str(e)
            
        return raw_info
    
    def _safe_extract_value(self, value: Any) -> str:
        """Safely extract string representation of any value"""
        try:
            if hasattr(value, "__name__"):
                return f"{type(value).__name__}: {value.__name__}"
            elif hasattr(value, "__class__"):
                if len(str(value)) < 200:
                    return str(value)
                else:
                    return f"{type(value).__name__}: <large_object>"
            else:
                return str(value)[:200]
        except:
            return f"{type(value).__name__}: <unreadable>"
    
    def _extract_tools_from_raw_data(self, raw_info: Dict[str, Any]) -> List[str]:
        """Extract tool names from raw node data using generic introspection"""
        tools = []
        
        # First, use tools already extracted in deep extraction
        tools.extend(raw_info.get("tools", []))
        
        # Look for function/tool-like objects in attributes
        for attr_name, attr_value in raw_info.get("attributes", {}).items():
            attr_str = str(attr_value)
            
            # Look for function signatures or callable objects
            if "function" in attr_str.lower() or "callable" in attr_str.lower():
                # Extract function name if available
                if ":" in attr_str:
                    potential_name = attr_str.split(":")[-1].strip()
                    if potential_name and not potential_name.startswith("<"):
                        tools.append(potential_name)
                elif hasattr(attr_value, "__name__"):
                    tools.append(getattr(attr_value, "__name__"))
        
        # Look for tools in closure data
        closure_data = raw_info.get("nested_data", {}).get("closure", {})
        for key, value in closure_data.items():
            value_str = str(value)
            # Look for function objects in closure
            if "function" in value_str.lower():
                if hasattr(value, "__name__"):
                    tools.append(getattr(value, "__name__"))
        
        # Look in code names for potential tool functions
        code_names = raw_info.get("nested_data", {}).get("code_names", [])
        for name in code_names:
            # Filter out common Python keywords and built-ins
            if (name and 
                not name.startswith("_") and 
                name not in ["self", "args", "kwargs", "return", "None", "True", "False"]):
                tools.append(name)
        
        # Look in function code variables for tool references
        code_vars = raw_info.get("nested_data", {}).get("code_vars", [])
        for var in code_vars:
            # Look for variables that might be tool references
            if (var and 
                not var.startswith("_") and 
                var not in ["self", "args", "kwargs", "state", "config"] and
                ("tool" in var.lower() or var.endswith("_fn") or var.endswith("_func"))):
                tools.append(var)
        
        return list(set(tools))  # Remove duplicates
    
    def _extract_capabilities_from_raw_data(self, raw_info: Dict[str, Any]) -> List[str]:
        """Extract capabilities from raw node data using completely generic introspection"""
        capabilities = []
        
        # Extract capabilities from function/method names
        function_name = raw_info.get("nested_data", {}).get("function_name", "")
        if function_name and function_name not in ["__call__", "invoke", "run"]:
            # Use the actual function name as a capability
            capabilities.append(f"executes_{function_name}")
        
        # Extract capabilities directly from tool names (completely generic)
        tools = raw_info.get("tools", [])
        for tool in tools:
            # Simply use the tool name as a capability (generic approach)
            capability_name = tool.lower().replace("_", " ").strip()
            if capability_name:
                capabilities.append(capability_name)
        
        # Look for meaningful attribute names that indicate capabilities (but skip infrastructure)
        for attr_name, attr_value in raw_info.get("attributes", {}).items():
            # Use attribute names that look like capabilities
            if (not attr_name.startswith("_") and 
                attr_name not in ["func", "config", "state"] and
                len(attr_name) > 2):
                # Convert attribute name to capability format
                capability_name = attr_name.lower().replace("_", " ").strip()
                if capability_name:
                    capabilities.append(capability_name)
        
        # Extract from code names (potential capability indicators)
        code_names = raw_info.get("nested_data", {}).get("code_names", [])
        for name in code_names:
            # Filter meaningful names that could represent capabilities
            if (name and 
                not name.startswith("_") and 
                name not in ["self", "args", "kwargs", "return", "None", "True", "False", "state", "config"] and
                len(name) > 2):
                capabilities.append(name)
        
        # If no specific capabilities found, add a generic one
        if not capabilities:
            capabilities.append("node_execution")
        
        return list(set(capabilities))
    
    def _extract_prompt_content_from_raw_data(self, raw_info: Dict[str, Any]) -> str:
        """Extract prompt/description content from raw node data"""
        # Look for function docstring first
        func_doc = raw_info.get("nested_data", {}).get("function_doc")
        if func_doc and len(func_doc.strip()) > 0:
            return func_doc.strip()
        
        # Look for prompt-related attributes
        for attr_name, attr_value in raw_info.get("attributes", {}).items():
            if "prompt" in attr_name.lower() or "description" in attr_name.lower():
                return str(attr_value)
        
        return None
    
    def _llm_analyze_agent_info(self, agent_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM to analyze and enhance agent information in a generic way"""
        try:
            analysis_prompt = f"""
Analyze the following agent/node information and provide enhanced details:

NODE/AGENT: {agent_info['name']}
DESCRIPTION/PROMPT: {agent_info.get('prompt_info', 'No description available')}
DETECTED TOOLS: {agent_info.get('tools', [])}
DETECTED CAPABILITIES: {agent_info.get('capabilities', [])}
RAW INTROSPECTION DATA: {str(agent_info.get('raw_data', {}))[:500]}

Based on ONLY the information provided above, analyze and extract:
1. What specific capabilities this node/agent has (based on actual evidence)
2. What tools or functions it appears to use (based on actual evidence)
3. Its likely role in the overall workflow (based on actual evidence)
4. A concise description of its purpose (based on actual evidence)

IMPORTANT: Do not make assumptions about specific domains (math, weather, etc.). 
Only infer capabilities based on the actual evidence provided.
Be generic and avoid domain-specific assumptions.

Respond in JSON format:
{{
  "capabilities": ["list", "of", "evidence-based", "capabilities"],
  "tools": ["list", "of", "detected", "tools"],
  "role_description": "evidence-based role description",
  "agent_purpose": "what this agent does based on evidence"
}}

Focus on being accurate and generic based only on the available evidence.
"""
            
            # Skip LLM analysis for now due to async complexity in sync context
            # TODO: Implement proper async handling or make this method async
            print("🔍 LLM analysis skipped (async handling needed)")
            return None
            
        except Exception as e:
            print(f"⚠️  LLM analysis failed: {e}")
            return None

    @abstractmethod
    async def generate_synthetic_dataset(
        self,
        workflow: Optional[Union[CompiledStateGraph, Runnable]] = None,
        num_scenarios: int = None,
    ) -> List[SyntheticExample]:
        """Generate synthetic dataset - must be implemented by subclasses"""
        pass
