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
        """Extract information from a graph node/agent"""
        agent_info = {
            "name": node_name,
            "capabilities": [],
            "tools": [],
            "prompt_info": None,
        }

        try:
            # Try to extract agent function or class
            if hasattr(node_data, "func"):
                func = node_data.func
                agent_info["capabilities"].append(f"Function: {func.__name__}")

                # Try to extract docstring
                if func.__doc__:
                    agent_info["prompt_info"] = func.__doc__.strip()

            # Enhanced agent info extraction based on known patterns
            node_name_lower = node_name.lower()
            
            # Alice agent (math specialist)
            if "alice" in node_name_lower:
                agent_info["capabilities"] = ["mathematical_calculations", "numeric_operations", "arithmetic_solving", "expression_evaluation"]
                agent_info["tools"] = ["calculate_math"]
                agent_info["prompt_info"] = "Alice, expert in mathematics and numeric calculations"
            
            # Bob agent (weather specialist)
            elif "bob" in node_name_lower:
                agent_info["capabilities"] = ["weather_reporting", "location_based_services", "climate_information", "pirate_communication"]
                agent_info["tools"] = ["get_weather", "ask_user"]
                agent_info["prompt_info"] = "Bob, the pirate weather specialist"
            
            # Main agent (coordinator)
            elif "main" in node_name_lower:
                agent_info["capabilities"] = ["task_coordination", "agent_routing", "user_interaction", "workflow_management"]
                agent_info["tools"] = ["ask_user"]
                agent_info["prompt_info"] = "Main Agent, responsible for coordinating tasks and managing user interaction"
            
            # Fallback to generic patterns
            else:
                if "math" in node_name_lower or "calculate" in node_name_lower:
                    agent_info["capabilities"].extend(
                        ["mathematical calculations", "arithmetic operations"]
                    )
                    agent_info["tools"].append("calculate_math")

                if "weather" in node_name_lower or "climate" in node_name_lower:
                    agent_info["capabilities"].extend(
                        ["weather information", "climate data"]
                    )
                    agent_info["tools"].append("get_weather")

                if "coordinator" in node_name_lower or "supervisor" in node_name_lower:
                    agent_info["capabilities"].extend(
                        ["task coordination", "user interaction"]
                    )
                    agent_info["tools"].append("ask_user")

        except Exception as e:
            print(f"⚠️  Error extracting agent info for {node_name}: {e}")

        return agent_info

    def _generate_workflow_description(self, context: Dict[str, Any]) -> str:
        """Generate comprehensive workflow description"""

        agents = context.get("agents", {})
        capabilities = context.get("capabilities", [])

        if not agents:
            return "Generic workflow system"

        agent_descriptions = []
        for agent_name, agent_info in agents.items():
            caps = ", ".join(agent_info.get("capabilities", []))
            if caps:
                agent_descriptions.append(f"{agent_name} ({caps})")
            else:
                agent_descriptions.append(agent_name)

        description = f"Multi-agent system with {len(agents)} agents: {', '.join(agent_descriptions)}"

        if capabilities:
            unique_caps = list(set(capabilities))
            description += f". System capabilities include: {', '.join(unique_caps)}"

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

    @abstractmethod
    async def generate_synthetic_dataset(
        self,
        workflow: Optional[Union[CompiledStateGraph, Runnable]] = None,
        num_scenarios: int = None,
    ) -> List[SyntheticExample]:
        """Generate synthetic dataset - must be implemented by subclasses"""
        pass
