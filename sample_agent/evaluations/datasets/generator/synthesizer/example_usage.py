#!/usr/bin/env python3
"""
Example Usage of Synthetic Data Generators
------------------------------------------

Demonstrates how to use both CustomSynthesizer and DeepEvalSynthesizer
for synthetic data generation with automatic LangSmith tracing.
"""

import asyncio
from pathlib import Path
import sys

# Add path to import agents
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from sample_agent.agents.swarm.graph import create_multi_agent_system_swarm_mode
from sample_agent.evaluations.datasets.generator.synthesizer import (
    BaseSynthesizer,
    CustomSynthesizer,
    DeepEvalSynthesizer,
    SynthesizerConfig
)


async def example_custom_synthesizer():
    """Example using CustomSynthesizer with automatic workflow analysis"""
    
    print("🔄 Running CustomSynthesizer Example")
    print("=" * 50)
    
    # Configuration
    config = SynthesizerConfig(
        project_name="custom-synthesizer-demo",
        tags=["demo", "custom", "swarm"],
        trace_metadata={
            "environment": "development",
            "version": "1.0",
            "synthesis_type": "custom"
        },
        num_scenarios=3
    )
    
    # Initialize synthesizer
    synthesizer = CustomSynthesizer(config)
    
    # Create real workflow
    workflow = create_multi_agent_system_swarm_mode()
    
    # Generate synthetic dataset (automatically analyzes workflow structure)
    examples = await synthesizer.generate_synthetic_dataset(
        workflow=workflow,
        num_scenarios=3
    )
    
    print(f"\n📊 CustomSynthesizer Results:")
    print(f"   - Generated examples: {len(examples)}")
    print(f"   - LangSmith project: {config.project_name}")
    
    # Show workflow analysis results
    if examples:
        workflow_analysis = examples[0].metadata.get("workflow_analysis", {})
        print(f"\n🔍 Workflow Analysis:")
        print(f"   - Type: {workflow_analysis.get('type', 'Unknown')}")
        print(f"   - Agents detected: {list(workflow_analysis.get('agents', {}).keys())}")
        print(f"   - Capabilities: {len(workflow_analysis.get('capabilities', []))}")
        
        print(f"\n📝 Sample Scenario:")
        example = examples[0]
        print(f"   - Complexity: {example.metadata.get('complexity')}")
        print(f"   - Target agents: {example.metadata.get('target_agents', [])}")
        print(f"   - Required tools: {example.metadata.get('required_tools', [])}")
    
    return examples


async def example_deepeval_synthesizer():
    """Example using DeepEvalSynthesizer for dataset generation"""
    
    print("\n🔄 Running DeepEvalSynthesizer Example")
    print("=" * 50)
    
    # Configuration
    config = SynthesizerConfig(
        project_name="deepeval-synthesizer-demo",
        tags=["demo", "deepeval", "agentic"],
        trace_metadata={
            "environment": "development",
            "version": "1.0",
            "synthesis_type": "deepeval"
        },
        num_scenarios=5
    )
    
    # Initialize synthesizer
    synthesizer = DeepEvalSynthesizer(config)
    
    # Generate synthetic dataset with optional workflow analysis
    examples = await synthesizer.generate_synthetic_dataset(num_scenarios=5)
    
    print(f"\n📊 DeepEvalSynthesizer Results:")
    print(f"   - Generated examples: {len(examples)}")
    print(f"   - LangSmith project: {config.project_name}")
    print(f"   - Automatically persisted to LangSmith")
    
    # Show sample outputs
    print("\n📝 Sample Generated Examples:")
    for i, example in enumerate(examples[:2]):  # Show first 2
        print(f"\n   Example {i+1}:")
        print(f"   Input: {example.input_data}")
        print(f"   Output format: {list(example.expected_output.keys())}")
        print(f"   Tags: {example.metadata['tags'][:3]}...")  # Show first 3 tags
    
    print(f"\n🏷️  Dynamic tagging applied for LangSmith filtering")
    
    return examples


async def combined_workflow_example():
    """Example of combined workflow using both synthesizers"""
    
    print("\n🔄 Running Combined Workflow Example")
    print("=" * 50)
    
    # Step 1: Generate synthetic dataset with DeepEval
    print("Step 1: Generate baseline synthetic dataset with DeepEval...")
    deepeval_config = SynthesizerConfig(
        project_name="combined-workflow",
        tags=["combined", "deepeval", "baseline"],
        trace_metadata={"step": "baseline_generation"},
        num_scenarios=3
    )
    
    deepeval_synthesizer = DeepEvalSynthesizer(deepeval_config)
    
    deepeval_examples = await deepeval_synthesizer.generate_synthetic_dataset(num_scenarios=3)
    print(f"   ✅ Generated {len(deepeval_examples)} baseline examples")
    
    # Step 2: Generate with real execution using Custom
    print("\nStep 2: Generate real execution examples with CustomSynthesizer...")
    custom_config = SynthesizerConfig(
        project_name="combined-workflow",
        tags=["combined", "custom", "real-execution"],
        trace_metadata={"step": "real_execution"},
        num_scenarios=3
    )
    
    custom_synthesizer = CustomSynthesizer(custom_config)
    workflow = create_multi_agent_system_swarm_mode()
    
    custom_examples = await custom_synthesizer.generate_synthetic_dataset(
        workflow=workflow,
        num_scenarios=3
    )
    
    print(f"   ✅ Generated {len(custom_examples)} real execution examples")
    
    # Step 3: Compare approaches
    print("\nStep 3: Comparison of approaches...")
    print(f"   📊 DeepEval: {len(deepeval_examples)} synthetic examples")
    print(f"   🔧 Custom: {len(custom_examples)} real execution examples")
    
    # Show tagging strategy
    if deepeval_examples and custom_examples:
        print(f"\n🏷️  Tag Strategy Comparison:")
        print(f"   DeepEval tags: {deepeval_examples[0].metadata['tags']}")
        print(f"   Custom tags: {custom_examples[0].metadata['tags'][:5]}...")  # Show first 5
    
    print(f"\n💡 Both approaches trace to same LangSmith project with different tags")
    print(f"   This allows easy filtering and comparison in LangSmith")


async def workflow_analysis_demo():
    """Demonstrate automatic workflow analysis capabilities"""
    
    print("\n🔬 Workflow Analysis Demo")
    print("=" * 50)
    
    config = SynthesizerConfig(
        project_name="workflow-analysis-demo",
        tags=["demo", "analysis"],
        trace_metadata={"demo_type": "analysis"},
        num_scenarios=1
    )
    
    synthesizer = CustomSynthesizer(config)
    workflow = create_multi_agent_system_swarm_mode()
    
    # Just analyze without generating scenarios
    print("🔍 Analyzing workflow structure...")
    workflow_context = synthesizer.analyze_workflow_structure(workflow)
    
    print(f"\n📊 Detailed Workflow Analysis:")
    print(f"   - Type: {workflow_context.get('type')}")
    print(f"   - Node count: {workflow_context.get('node_count', 'Unknown')}")
    print(f"   - State fields: {workflow_context.get('state_fields', [])}")
    print(f"   - Description: {workflow_context.get('workflow_description')}")
    
    print(f"\n🤖 Detected Agents:")
    agents = workflow_context.get('agents', {})
    for agent_name, agent_info in agents.items():
        print(f"   - {agent_name}:")
        print(f"     • Capabilities: {agent_info.get('capabilities', [])}")
        print(f"     • Tools: {agent_info.get('tools', [])}")
        if agent_info.get('prompt_info'):
            print(f"     • Prompt info: {agent_info['prompt_info'][:100]}...")
    
    print(f"\n✨ This analysis is used automatically to generate appropriate scenarios")


async def main():
    """Main function to run all examples"""
    
    print("🚀 Synthetic Data Generation Examples")
    print("=" * 60)
    
    try:
        # Run CustomSynthesizer example
        await example_custom_synthesizer()
        
        # Run DeepEvalSynthesizer example
        await example_deepeval_synthesizer()
        
        # Run combined workflow example
        await combined_workflow_example()
        
        # Demonstrate workflow analysis
        await workflow_analysis_demo()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("📈 Check LangSmith for automatic tracing with dynamic tags")
        print("🔍 Workflow analysis enables smart scenario generation")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 