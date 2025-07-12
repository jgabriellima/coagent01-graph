#!/usr/bin/env python3
"""
Custom Synthetic Data Generator with Dual Modes
-----------------------------------------------

Agnostic synthesizer with two distinct execution modes:
1. SYNTHETIC MODE: Analyzes workflow structure and generates synthetic datasets (no execution)
2. EXECUTION MODE: Generates scenarios and executes real workflows for trace collection

Both modes leverage automatic workflow analysis for intelligent scenario generation.
"""

import uuid
import json
import asyncio
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable
from langgraph.graph.state import CompiledStateGraph

from .base import (
    BaseSynthesizer,
    SynthesizerConfig,
    SyntheticExample,
    DatasetPersistence,
)


class ExecutionMode(Enum):
    """Execution modes for CustomSynthesizer"""

    SYNTHETIC = "synthetic"  # Analyze workflow + generate synthetic data (no execution)
    EXECUTION = "execution"  # Generate scenarios + execute real workflow


class CustomSynthesizer(BaseSynthesizer):
    """Custom synthesizer with dual execution modes"""

    def __init__(
        self,
        config: SynthesizerConfig,
        mode: ExecutionMode = ExecutionMode.EXECUTION,
        persistence: DatasetPersistence = None,
    ):
        super().__init__(config, persistence)
        self.mode = mode

    async def generate_synthetic_from_analysis(
        self, workflow: Union[CompiledStateGraph, Runnable], num_scenarios: int = None
    ) -> List[SyntheticExample]:
        """
        SYNTHETIC MODE: Analyze workflow structure and generate synthetic datasets without execution.

        This mode:
        1. Analyzes workflow structure to understand capabilities
        2. Generates realistic scenarios based on workflow analysis
        3. Creates synthetic responses using LLM (no real execution)
        4. Returns structured synthetic examples
        """

        print(f"🔍 [SYNTHETIC MODE] Analyzing workflow structure...")
        workflow_context = self.analyze_workflow_structure(workflow)

        print(f"📊 Workflow Analysis:")
        print(f"   - Type: {workflow_context.get('type')}")
        print(f"   - Agents: {list(workflow_context.get('agents', {}).keys())}")
        print(f"   - Capabilities: {len(workflow_context.get('capabilities', []))}")
        print(
            f"   - Description: {workflow_context.get('workflow_description', 'N/A')}"
        )

        print(f"🔄 Generating synthetic scenarios based on workflow analysis...")
        scenarios = await self.generate_scenarios_from_workflow(
            workflow_context, num_scenarios
        )

        if not scenarios:
            print("❌ No scenarios generated")
            return []

        print(f"🤖 Generating synthetic responses for {len(scenarios)} scenarios...")

        synthetic_examples = []
        for i, scenario in enumerate(scenarios):
            scenario_id = f"synthetic-{i+1}-{uuid.uuid4().hex[:8]}"

            # Prepare input data
            input_data = {
                "messages": [{"role": "user", "content": scenario["user_input"]}],
                **scenario.get("context", {}),
            }

            print(
                f"   🎭 Generating synthetic response {i+1}/{len(scenarios)} ({scenario.get('complexity', 'unknown')})"
            )

            # Generate synthetic response using LLM based on workflow analysis
            synthetic_output = await self._generate_synthetic_response(
                scenario, workflow_context, scenario_id
            )

            if synthetic_output:
                # Create synthetic example with analysis metadata
                synthetic_example = SyntheticExample(
                    input_data=input_data,
                    expected_output=synthetic_output,
                    metadata={
                        "scenario_id": scenario_id,
                        "execution_mode": "synthetic",
                        "complexity": scenario.get("complexity", "medium"),
                        "expected_behavior": scenario.get("expected_behavior", ""),
                        "target_agents": scenario.get("target_agents", []),
                        "required_tools": scenario.get("required_tools", []),
                        "generation_timestamp": datetime.now().isoformat(),
                        "project_name": self.config.project_name,
                        "tags": self.config.tags
                        + [
                            "mode:synthetic",
                            f"complexity:{scenario.get('complexity', 'unknown')}",
                            f"scenario:{scenario_id}",
                        ],
                        "workflow_analysis": workflow_context,
                        **self.config.trace_metadata,
                    },
                )
                synthetic_examples.append(synthetic_example)
                print(f"   ✅ Synthetic response {i+1} generated")
            else:
                print(f"   ❌ Synthetic response {i+1} failed")

        print(
            f"📊 Generated {len(synthetic_examples)} synthetic examples (no execution)"
        )
        return synthetic_examples

    async def _generate_synthetic_response(
        self,
        scenario: Dict[str, Any],
        workflow_context: Dict[str, Any],
        scenario_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Generate synthetic response based on scenario and workflow analysis"""

        agents = workflow_context.get("agents", {})
        capabilities = workflow_context.get("capabilities", [])
        tools = workflow_context.get("tools", [])

        prompt = f"""
Based on the following workflow analysis and user scenario, generate a realistic synthetic response:

WORKFLOW CONTEXT:
- Agents: {list(agents.keys())}
- Capabilities: {capabilities}
- Tools: {tools}
- Description: {workflow_context.get('workflow_description', '')}

USER SCENARIO:
- Input: {scenario['user_input']}
- Expected behavior: {scenario['expected_behavior']}
- Target agents: {scenario.get('target_agents', [])}
- Required tools: {scenario.get('required_tools', [])}

Generate a realistic response that this workflow would produce, including:
1. Appropriate agent interactions
2. Tool usage patterns
3. State management
4. Realistic processing flow

Format as JSON:
{{
  "messages": [
    {{"role": "system", "content": "System message"}},
    {{"role": "assistant", "content": "Response", "tool_calls": [...]}},
    ...
  ],
  "agent_handoffs": ["agent1", "agent2"],
  "tools_used": ["tool1", "tool2"],
  "processing_steps": ["step1", "step2"],
  "final_state": {{"key": "value"}}
}}

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

            synthetic_response = json.loads(content)
            return self._standardize_output(synthetic_response)

        except Exception as e:
            print(f"⚠️  Synthetic response generation failed for {scenario_id}: {e}")
            return None

    async def generate_with_real_execution(
        self, workflow: Union[CompiledStateGraph, Runnable], num_scenarios: int = None
    ) -> List[SyntheticExample]:
        """
        EXECUTION MODE: Generate scenarios and execute real workflow for trace collection.

        This mode:
        1. Analyzes workflow structure for context
        2. Generates realistic test scenarios
        3. Executes real workflow for each scenario
        4. Captures real traces and execution results
        """

        print(f"🔍 [EXECUTION MODE] Analyzing workflow for scenario generation...")
        workflow_context = self.analyze_workflow_structure(workflow)

        print(f"📊 Workflow Analysis:")
        print(f"   - Type: {workflow_context.get('type')}")
        print(f"   - Agents: {list(workflow_context.get('agents', {}).keys())}")
        print(f"   - Capabilities: {len(workflow_context.get('capabilities', []))}")

        print(f"🔄 Generating test scenarios for real execution...")
        scenarios = await self.generate_scenarios_from_workflow(
            workflow_context, num_scenarios
        )

        if not scenarios:
            print("❌ No scenarios generated")
            return []

        print(f"🚀 Executing {len(scenarios)} scenarios on real workflow...")

        synthetic_examples = []
        for i, scenario in enumerate(scenarios):
            scenario_id = f"execution-{i+1}-{uuid.uuid4().hex[:8]}"

            # Prepare input data
            input_data = {
                "messages": [{"role": "user", "content": scenario["user_input"]}],
                **scenario.get("context", {}),
            }

            print(
                f"   ⏳ Executing scenario {i+1}/{len(scenarios)} ({scenario.get('complexity', 'unknown')})"
            )

            # Execute workflow with scenario metadata
            expected_output = await self.execute_workflow(
                workflow,
                input_data,
                scenario_id,
                {
                    "complexity": scenario.get("complexity"),
                    "target_agents": scenario.get("target_agents", []),
                    "required_tools": scenario.get("required_tools", []),
                    "expected_behavior": scenario.get("expected_behavior", ""),
                },
            )

            if expected_output:
                synthetic_example = SyntheticExample(
                    input_data=input_data,
                    expected_output=expected_output,
                    metadata={
                        "scenario_id": scenario_id,
                        "execution_mode": "real_execution",
                        "complexity": scenario.get("complexity", "medium"),
                        "expected_behavior": scenario.get("expected_behavior", ""),
                        "target_agents": scenario.get("target_agents", []),
                        "required_tools": scenario.get("required_tools", []),
                        "generation_timestamp": datetime.now().isoformat(),
                        "project_name": self.config.project_name,
                        "tags": self.config.tags
                        + [
                            "mode:execution",
                            f"complexity:{scenario.get('complexity', 'unknown')}",
                            f"scenario:{scenario_id}",
                        ],
                        "workflow_analysis": workflow_context,
                        **self.config.trace_metadata,
                    },
                )
                synthetic_examples.append(synthetic_example)
                print(f"   ✅ Scenario {i+1} executed successfully")
            else:
                print(f"   ❌ Scenario {i+1} execution failed")

        print(f"📊 Generated {len(synthetic_examples)} examples from real execution")
        return synthetic_examples

    async def execute_workflow(
        self,
        workflow: Union[CompiledStateGraph, Runnable],
        input_data: Dict[str, Any],
        scenario_id: str,
        scenario_metadata: Dict[str, Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """Execute workflow and return standardized output"""

        try:
            # Setup thread config with dynamic tags
            scenario_tags = self.config.tags.copy()
            if scenario_metadata:
                scenario_tags.extend(
                    [
                        f"complexity:{scenario_metadata.get('complexity', 'unknown')}",
                        f"scenario:{scenario_id}",
                    ]
                )
                if scenario_metadata.get("target_agents"):
                    scenario_tags.extend(
                        [
                            f"agent:{agent}"
                            for agent in scenario_metadata["target_agents"]
                        ]
                    )
                if scenario_metadata.get("required_tools"):
                    scenario_tags.extend(
                        [f"tool:{tool}" for tool in scenario_metadata["required_tools"]]
                    )

            thread_config = {
                "configurable": {
                    "thread_id": f"custom-{scenario_id}",
                },
                "tags": scenario_tags,
                "metadata": {
                    **self.config.trace_metadata,
                    "scenario_id": scenario_id,
                    "execution_type": "custom_synthesizer",
                    **(scenario_metadata or {}),
                },
            }

            # Execute workflow
            if isinstance(workflow, CompiledStateGraph):
                result = await workflow.ainvoke(input_data, thread_config)
            else:
                result = await workflow.ainvoke(input_data, thread_config)

            # Standardize output format
            standardized_output = self._standardize_output(result)
            return standardized_output

        except Exception as e:
            print(f"⚠️  Execution failed for {scenario_id}: {e}")
            return None

    async def generate_synthetic_dataset(
        self,
        workflow: Optional[Union[CompiledStateGraph, Runnable]] = None,
        num_scenarios: int = None,
    ) -> List[SyntheticExample]:
        """
        Generate synthetic dataset using the configured execution mode.

        - SYNTHETIC mode: Analyzes workflow + generates synthetic data (no execution)
        - EXECUTION mode: Generates scenarios + executes real workflow
        """

        if workflow is None:
            raise ValueError(
                "CustomSynthesizer requires a workflow. Provide a CompiledStateGraph or Runnable."
            )

        print(f"🎯 CustomSynthesizer running in {self.mode.value.upper()} mode")

        if self.mode == ExecutionMode.SYNTHETIC:
            return await self.generate_synthetic_from_analysis(workflow, num_scenarios)
        elif self.mode == ExecutionMode.EXECUTION:
            return await self.generate_with_real_execution(workflow, num_scenarios)
        else:
            raise ValueError(f"Unknown execution mode: {self.mode}")


# Example usage demonstrating both modes
async def main():
    """Example usage of Custom Synthesizer in both modes"""

    # Mock workflow for demonstration
    class MockWorkflow:
        async def ainvoke(self, input_data, config):
            # Simulate processing
            await asyncio.sleep(0.1)
            return {
                "messages": input_data.get("messages", []),
                "response": "Mock response to user input",
                "metadata": {"processed": True},
                "custom_state": {"task_completed": True},
            }

    mock_workflow = MockWorkflow()

    # Configuration
    config = SynthesizerConfig(
        project_name="custom-dual-mode-test",
        tags=["synthetic", "custom", "demo"],
        trace_metadata={"environment": "test", "version": "1.0"},
        num_scenarios=2,
    )

    print("🚀 Testing CustomSynthesizer Dual Modes")
    print("=" * 60)

    # Test SYNTHETIC mode (analyze workflow + generate synthetic data, no execution)
    print("\n🎭 SYNTHETIC MODE TEST")
    print("-" * 30)
    synthetic_synthesizer = CustomSynthesizer(config, mode=ExecutionMode.SYNTHETIC)
    synthetic_examples = await synthetic_synthesizer.generate_synthetic_dataset(
        workflow=mock_workflow, num_scenarios=2
    )

    # Test EXECUTION mode (generate scenarios + execute real workflow)
    print("\n🚀 EXECUTION MODE TEST")
    print("-" * 30)
    execution_synthesizer = CustomSynthesizer(config, mode=ExecutionMode.EXECUTION)
    execution_examples = await execution_synthesizer.generate_synthetic_dataset(
        workflow=mock_workflow, num_scenarios=2
    )

    print(f"\n{'='*60}")
    print("📊 DUAL MODE SUMMARY")
    print(f"{'='*60}")
    print(f"SYNTHETIC mode examples: {len(synthetic_examples)}")
    print(f"EXECUTION mode examples: {len(execution_examples)}")
    print(f"Total examples: {len(synthetic_examples) + len(execution_examples)}")
    print(f"Project: {config.project_name}")
    print("=" * 60)
    print("Key Differences:")
    print("• SYNTHETIC: Workflow analysis → LLM generation (no real execution)")
    print("• EXECUTION: Workflow analysis → Real execution + trace collection")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
