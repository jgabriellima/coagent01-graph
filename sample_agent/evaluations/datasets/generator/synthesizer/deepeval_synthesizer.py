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
    """DeepEval-based synthetic data generator"""

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

        # Use workflow analysis if available
        if workflow_context:
            agents = list(workflow_context.get("agents", {}).keys())
            capabilities = workflow_context.get("capabilities", [])
            tools = workflow_context.get("tools", [])

            default_task = f"Multi-agent workflow execution with {len(agents)} agents: {', '.join(agents)}"
            default_scenario = f"Agents coordinate to execute tools ({', '.join(tools)}), handle user requests, and manage state. Capabilities: {', '.join(capabilities)}"
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

        # Use workflow analysis if available
        if workflow_context:
            workflow_desc = workflow_context.get("workflow_description", "")
            default_task = (
                f"Generate structured conversation outputs for {workflow_desc}"
            )
            default_scenario = f"User-assistant interactions with structured JSON responses for {workflow_desc}"
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
        """Generate synthetic dataset with optional workflow analysis and custom descriptions"""

        num_scenarios = num_scenarios or self.config.num_scenarios

        # Analyze workflow if provided
        workflow_context = None
        if workflow:
            print(f"🔍 Analyzing workflow structure for better generation...")
            workflow_context = self.analyze_workflow_structure(workflow)

        # Setup synthesizer with combined context
        if not self.synthesizer:
            self.setup_agentic_synthesizer(
                task_description=task_description,
                scenario=scenario, 
                workflow_context=workflow_context
            )

        print(f"🔄 Generating {num_scenarios} synthetic examples with DeepEval...")

        # Generate synthetic data
        self.synthesizer.generate_goldens_from_scratch(num_goldens=num_scenarios)

        # Convert to standard format
        examples = []
        for i, golden in enumerate(self.synthesizer.synthetic_goldens):

            # Prepare input data
            input_data = {"messages": [{"role": "user", "content": golden.input}]}

            # Parse expected output
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

            # Create synthetic example
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
                },
            )
            examples.append(example)

        print(f"📊 Generated {len(examples)} synthetic examples")

        # Persist dataset to LangSmith
        print(f"💾 Persisting dataset to LangSmith...")
        await self.persist_dataset(examples)

        return examples

    def _parse_expected_output(self, raw_output: str) -> Dict[str, Any]:
        """Parse and standardize expected output"""
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
                    pass

            # Fallback: create standard structure
            return {"messages": [{"role": "assistant", "content": str(raw_output)}]}

        except Exception as e:
            print(f"⚠️  Error parsing output: {e}")
            return {"messages": [{"role": "assistant", "content": str(raw_output)}]}


# Example usage
async def main():
    """Example usage of DeepEval Synthesizer"""

    config = SynthesizerConfig(
        project_name="deepeval-synthetic-test",
        tags=["synthetic", "deepeval", "demo"],
        trace_metadata={"environment": "test", "version": "1.0"},
        num_scenarios=5,
    )

    synthesizer = DeepEvalSynthesizer(config)

    # Generate synthetic dataset (can optionally provide workflow for analysis)
    examples = await synthesizer.generate_synthetic_dataset(num_scenarios=5)

    # Show sample outputs
    print("\n📝 Sample Generated Examples:")
    for i, example in enumerate(examples[:2]):  # Show first 2
        print(f"\n   Example {i+1}:")
        print(f"   Input: {example.input_data}")
        print(f"   Expected Output Keys: {list(example.expected_output.keys())}")
        print(f"   Tags: {example.metadata['tags']}")

    print(f"\n{'='*60}")
    print("📊 SYNTHESIS SUMMARY")
    print(f"{'='*60}")
    print(f"Generated examples: {len(examples)}")
    print(f"Examples persisted to LangSmith project: {config.project_name}")
    print("🏷️  Dynamic tags applied for filtering and organization")
    print(f"{'='*60}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
