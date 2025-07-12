#!/usr/bin/env python3
"""
DeepEval Synthetic Data Generator
--------------------------------

LLM-based synthetic data generation using DeepEval framework.
Generates synthetic datasets with dynamic tags for LangSmith tracing.
"""

import json
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime

from deepeval.synthesizer import Synthesizer
from deepeval.synthesizer.config import StylingConfig
from langsmith import Client
from langchain_core.runnables import Runnable
from langgraph.graph.state import CompiledStateGraph

from .base import (
    BaseSynthesizer,
    SynthesizerConfig,
    SyntheticExample,
    DatasetPersistence,
)


class DeepEvalSynthesizer(BaseSynthesizer):
    """DeepEval-based synthetic data generator with optional workflow analysis"""

    def __init__(
        self, config: SynthesizerConfig, persistence: DatasetPersistence = None
    ):
        super().__init__(config, persistence)
        self.synthesizer = None

    def setup_agentic_synthesizer(
        self,
        task_description: str = None,
        scenario: str = None,
        workflow_context: Dict[str, Any] = None,
    ):
        """Setup synthesizer for agentic workflows with tool calls"""

        # Use workflow analysis if available for enhanced generation
        if workflow_context:
            agents = list(workflow_context.get("agents", {}).keys())
            capabilities = workflow_context.get("capabilities", [])
            tools = workflow_context.get("tools", [])

            default_task = f"Multi-agent workflow execution with {len(agents)} agents: {', '.join(agents)}"
            default_scenario = f"Agents coordinate to execute tools ({', '.join(tools)}), handle user requests, and manage state. Capabilities: {', '.join(capabilities)}"
            
            print(f"   🎯 Enhanced with workflow context: {len(agents)} agents, {len(tools)} tools")
        else:
            default_task = (
                "Multi-agent workflow execution with tool calls and coordination"
            )
            default_scenario = "Agents coordinate to execute tools, handle user requests, and manage state"

        styling_config = StylingConfig(
            input_format="User request plus agentic context (available tools, memory, state)",
            expected_output_format="""
            {
              "messages": [ 
                { "role": "system", "content": "..." },
                { "role": "assistant", "content": "...", "tool_calls": [ { "name": "...", "args": {...} } ] }
              ],
              "custom_state_data": {...}
            }
            """,
            task=task_description or default_task,
            scenario=scenario or default_scenario,
        )

        self.synthesizer = Synthesizer(styling_config=styling_config)

    def setup_conversational_synthesizer(
        self,
        task_description: str = None,
        scenario: str = None,
        workflow_context: Dict[str, Any] = None,
    ):
        """Setup synthesizer for conversational AI applications"""

        # Use workflow analysis if available for enhanced generation
        if workflow_context:
            workflow_desc = workflow_context.get("workflow_description", "")
            default_task = (
                f"Generate structured conversation outputs for {workflow_desc}"
            )
            default_scenario = f"User-assistant interactions with structured JSON responses for {workflow_desc}"
            
            print(f"   🎯 Enhanced with workflow description: {workflow_desc}")
        else:
            default_task = (
                "Generate structured conversation outputs for AI applications"
            )
            default_scenario = (
                "User-assistant interactions with structured JSON responses"
            )

        styling_config = StylingConfig(
            input_format="User message in a conversation",
            expected_output_format="""
            {
              "messages": [ 
                { "role": "system", "content": "..." },
                { "role": "assistant", "content": "..." }
              ]
            }
            """,
            task=task_description or default_task,
            scenario=scenario or default_scenario,
        )

        self.synthesizer = Synthesizer(styling_config=styling_config)

    async def generate_synthetic_dataset(
        self,
        workflow: Optional[Union[CompiledStateGraph, Runnable]] = None,
        num_scenarios: int = None,
        task_description: str = None,
        scenario: str = None,
    ) -> List[SyntheticExample]:
        """
        Generate synthetic dataset with optional workflow analysis and custom descriptions.
        
        Args:
            workflow: Optional workflow for automatic structure analysis
            num_scenarios: Number of synthetic examples to generate
            task_description: Custom task description (enhances generation quality)
            scenario: Custom scenario description (enhances generation quality)
            
        Returns:
            List of synthetic examples with standardized format
        """

        num_scenarios = num_scenarios or self.config.num_scenarios

        print(f"🤖 DeepEvalSynthesizer starting generation...")
        print(f"   📊 Target scenarios: {num_scenarios}")
        
        # Analyze workflow if provided for enhanced generation
        workflow_context = None
        if workflow:
            print(f"🔍 Analyzing workflow structure for better generation...")
            workflow_context = self.analyze_workflow_structure(workflow)
            
            print(f"📊 Workflow Analysis Results:")
            print(f"   - Type: {workflow_context.get('type', 'Unknown')}")
            print(f"   - Agents: {list(workflow_context.get('agents', {}).keys())}")
            print(f"   - Capabilities: {len(workflow_context.get('capabilities', []))}")
            print(f"   - Tools: {len(workflow_context.get('tools', []))}")
        else:
            print(f"📝 Using generic generation (no workflow analysis)")

        # Setup synthesizer with combined context
        if not self.synthesizer:
            try:
                self.setup_agentic_synthesizer(
                    task_description=task_description,
                    scenario=scenario, 
                    workflow_context=workflow_context
                )
                print(f"   ✅ DeepEval synthesizer configured")
            except Exception as e:
                print(f"   ❌ Failed to setup synthesizer: {e}")
                raise

        print(f"🔄 Generating {num_scenarios} synthetic examples with DeepEval...")

        try:
            # Generate synthetic data
            self.synthesizer.generate_goldens_from_scratch(num_goldens=num_scenarios)
            
            if not self.synthesizer.synthetic_goldens:
                print(f"   ⚠️  No synthetic examples generated")
                return []
                
            print(f"   ✅ Generated {len(self.synthesizer.synthetic_goldens)} raw examples")
            
        except Exception as e:
            print(f"   ❌ DeepEval generation failed: {e}")
            return []

        # Convert to standard format with enhanced metadata
        examples = []
        for i, golden in enumerate(self.synthesizer.synthetic_goldens):
            try:
                print(f"   🔄 Processing example {i+1}/{len(self.synthesizer.synthetic_goldens)}")

                # Prepare input data
                input_data = {"messages": [{"role": "user", "content": golden.input}]}

                # Parse expected output with improved error handling
                expected_output = self._parse_expected_output(golden.expected_output)

                # Generate dynamic tags for this example
                example_tags = self.config.tags.copy()
                example_tags.extend(
                    ["generator:deepeval", f"example:{i+1}", f"synthetic:generated"]
                )

                # Add workflow-specific tags if available
                if workflow_context:
                    example_tags.extend(
                        [
                            f"workflow:{workflow_context.get('type', 'unknown')}",
                            f"agents:{len(workflow_context.get('agents', {}))}",
                        ]
                    )
                    if workflow_context.get("agents"):
                        example_tags.extend(
                            [
                                f"agent:{agent}"
                                for agent in workflow_context["agents"].keys()
                            ]
                        )

                # Add custom description tags if provided
                if task_description:
                    example_tags.append("enhanced:task_description")
                if scenario:
                    example_tags.append("enhanced:scenario")

                # Create synthetic example with comprehensive metadata
                example = SyntheticExample(
                    input_data=input_data,
                    expected_output=expected_output,
                    metadata={
                        "scenario_id": f"deepeval-{i+1}",
                        "generator": "DeepEvalSynthesizer",
                        "project_name": self.config.project_name,
                        "tags": example_tags,
                        "trace_metadata": self.config.trace_metadata,
                        "generation_timestamp": datetime.now().isoformat(),
                        "input_text": golden.input,
                        "raw_output": golden.expected_output,
                        "workflow_analysis": workflow_context,
                        "custom_task_description": task_description,
                        "custom_scenario": scenario,
                        "generation_context": {
                            "workflow_enhanced": workflow_context is not None,
                            "task_enhanced": task_description is not None,
                            "scenario_enhanced": scenario is not None
                        }
                    },
                )
                examples.append(example)
                
            except Exception as e:
                print(f"   ⚠️  Failed to process example {i+1}: {e}")
                continue

        print(f"📊 Generated {len(examples)} synthetic examples")
        
        if len(examples) == 0:
            print(f"   ❌ No valid examples generated")
            return []

        # Persist dataset to LangSmith with error handling
        try:
            print(f"💾 Persisting dataset to LangSmith...")
            await self.persist_dataset(examples)
            print(f"   ✅ Dataset persisted successfully")
        except Exception as e:
            print(f"   ⚠️  Persistence failed (examples still returned): {e}")

        return examples

    def _parse_expected_output(self, raw_output: str) -> Dict[str, Any]:
        """Parse and standardize expected output with improved error handling"""
        try:
            # Try to parse as JSON first
            if isinstance(raw_output, str):
                # Clean potential markdown formatting
                cleaned = raw_output.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:-3]
                elif cleaned.startswith("```"):
                    cleaned = cleaned[3:-3]

                try:
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, dict):
                        return self._standardize_output(parsed)
                except json.JSONDecodeError:
                    # Continue to fallback
                    pass

            # Fallback: create standard structure
            return {"messages": [{"role": "assistant", "content": str(raw_output)}]}

        except Exception as e:
            print(f"      ⚠️  Error parsing output, using fallback: {e}")
            return {"messages": [{"role": "assistant", "content": str(raw_output)}]}
