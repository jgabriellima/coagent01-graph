#!/usr/bin/env python3
"""
Example Usage of Synthetic Data Generators
------------------------------------------

Demonstrates how to use both CustomSynthesizer and DeepEvalSynthesizer
with all available features including dual modes, workflow analysis, and custom descriptions.
"""

import asyncio
from pathlib import Path
import sys
from typing import List

# Add path to import agents
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from sample_agent.agents.swarm.graph import create_multi_agent_system_swarm_mode
from sample_agent.evaluations.datasets.generator.synthesizer import (
    BaseSynthesizer,
    CustomSynthesizer,
    DeepEvalSynthesizer,
    SynthesizerConfig,
    ExecutionMode
)


async def example_custom_synthesizer_dual_modes():
    """Example using CustomSynthesizer with both SYNTHETIC and EXECUTION modes"""
    
    print("🔄 Running CustomSynthesizer Dual Modes Example")
    print("=" * 60)
    
    # Configuration
    config = SynthesizerConfig(
        project_name="custom-dual-modes-demo",
        tags=["demo", "custom", "dual-modes"],
        trace_metadata={
            "environment": "development",
            "version": "1.0",
            "synthesis_type": "custom_dual"
        },
        num_scenarios=2
    )
    
    # Create real workflow
    workflow = create_multi_agent_system_swarm_mode()
    
    # SYNTHETIC MODE: Analysis + LLM generation (no execution)
    print("\n🎭 SYNTHETIC MODE Example")
    print("-" * 30)
    
    synthetic_synthesizer = CustomSynthesizer(config, mode=ExecutionMode.SYNTHETIC)
    synthetic_examples = await synthetic_synthesizer.generate_synthetic_dataset(
        workflow=workflow,
        num_scenarios=2
    )
    
    print(f"\n📊 SYNTHETIC Mode Results:")
    print(f"   - Generated examples: {len(synthetic_examples)}")
    print(f"   - Mode: {synthetic_examples[0].metadata.get('execution_mode') if synthetic_examples else 'N/A'}")
    print(f"   - No real workflow execution performed")
    
    # EXECUTION MODE: Analysis + real execution + traces  
    print("\n🚀 EXECUTION MODE Example")
    print("-" * 30)
    
    execution_synthesizer = CustomSynthesizer(config, mode=ExecutionMode.EXECUTION)
    execution_examples = await execution_synthesizer.generate_synthetic_dataset(
        workflow=workflow,
        num_scenarios=2
    )
    
    print(f"\n📊 EXECUTION Mode Results:")
    print(f"   - Generated examples: {len(execution_examples)}")
    print(f"   - Mode: {execution_examples[0].metadata.get('execution_mode') if execution_examples else 'N/A'}")
    print(f"   - Real workflow execution performed")
    
    # Show key differences
    print(f"\n🔍 Key Differences:")
    print(f"   • SYNTHETIC: Fast generation, simulated responses, no infrastructure load")
    print(f"   • EXECUTION: Real traces, actual performance data, system validation")
    
    return synthetic_examples, execution_examples


async def example_deepeval_with_enhancements():
    """Example using DeepEvalSynthesizer with all enhancement options"""
    
    print("\n🔄 Running DeepEvalSynthesizer Enhanced Example")
    print("=" * 60)
    
    # Configuration
    config = SynthesizerConfig(
        project_name="deepeval-enhanced-demo",
        tags=["demo", "deepeval", "enhanced"],
        trace_metadata={
            "environment": "development",
            "version": "1.0",
            "synthesis_type": "deepeval_enhanced"
        },
        num_scenarios=3
    )
    
    # Initialize synthesizer
    synthesizer = DeepEvalSynthesizer(config)
    workflow = create_multi_agent_system_swarm_mode()
    
    # Example 1: Basic generation (no enhancements)
    print("\n📝 Example 1: Basic Generation")
    print("-" * 30)
    
    basic_examples = await synthesizer.generate_synthetic_dataset(num_scenarios=2)
    print(f"   ✅ Generated {len(basic_examples)} basic examples")
    
    # Example 2: With workflow analysis enhancement
    print("\n🔍 Example 2: With Workflow Analysis")
    print("-" * 30)
    
    # Reset synthesizer for new configuration
    synthesizer.synthesizer = None
    
    workflow_examples = await synthesizer.generate_synthetic_dataset(
        workflow=workflow,
        num_scenarios=2
    )
    print(f"   ✅ Generated {len(workflow_examples)} workflow-enhanced examples")
    
    # Example 3: With custom task description and scenario
    print("\n🎯 Example 3: With Custom Descriptions")
    print("-" * 30)
    
    # Reset synthesizer for new configuration
    synthesizer.synthesizer = None
    
    custom_examples = await synthesizer.generate_synthetic_dataset(
        workflow=workflow,
        num_scenarios=2,
        task_description="Multi-agent system for mathematical calculations and weather information",
        scenario="Users request complex tasks requiring coordination between Alice (math) and Bob (weather) agents"
    )
    print(f"   ✅ Generated {len(custom_examples)} fully-enhanced examples")
    
    # Show enhancement comparison
    print(f"\n📊 Enhancement Comparison:")
    if basic_examples:
        basic_context = basic_examples[0].metadata.get('generation_context', {})
        print(f"   Basic: workflow={basic_context.get('workflow_enhanced')}, task={basic_context.get('task_enhanced')}")
    
    if custom_examples:
        enhanced_context = custom_examples[0].metadata.get('generation_context', {})
        print(f"   Enhanced: workflow={enhanced_context.get('workflow_enhanced')}, task={enhanced_context.get('task_enhanced')}")
        
        # Show enhanced tags
        enhanced_tags = [tag for tag in custom_examples[0].metadata['tags'] if tag.startswith('enhanced:')]
        print(f"   Enhanced tags: {enhanced_tags}")
    
    return basic_examples, workflow_examples, custom_examples


async def example_workflow_analysis_comparison():
    """Compare workflow analysis between synthesizers"""
    
    print("\n🔬 Workflow Analysis Comparison")
    print("=" * 60)
    
    workflow = create_multi_agent_system_swarm_mode()
    
    # CustomSynthesizer analysis
    print("🔧 CustomSynthesizer Analysis:")
    custom_config = SynthesizerConfig(
        project_name="analysis-comparison",
        tags=["analysis", "custom"],
        trace_metadata={"type": "analysis"},
        num_scenarios=1
    )
    
    custom_synthesizer = CustomSynthesizer(custom_config)
    custom_analysis = custom_synthesizer.analyze_workflow_structure(workflow)
    
    print(f"   - Type: {custom_analysis.get('type')}")
    print(f"   - Agents: {list(custom_analysis.get('agents', {}).keys())}")
    print(f"   - Capabilities: {len(custom_analysis.get('capabilities', []))}")
    
    # DeepEvalSynthesizer analysis
    print("\n🤖 DeepEvalSynthesizer Analysis:")
    deepeval_config = SynthesizerConfig(
        project_name="analysis-comparison",
        tags=["analysis", "deepeval"],
        trace_metadata={"type": "analysis"},
        num_scenarios=1
    )
    
    deepeval_synthesizer = DeepEvalSynthesizer(deepeval_config)
    deepeval_analysis = deepeval_synthesizer.analyze_workflow_structure(workflow)
    
    print(f"   - Type: {deepeval_analysis.get('type')}")
    print(f"   - Agents: {list(deepeval_analysis.get('agents', {}).keys())}")
    print(f"   - Capabilities: {len(deepeval_analysis.get('capabilities', []))}")
    
    print(f"\n✨ Both synthesizers use the same analysis engine from BaseSynthesizer")


async def example_unified_interface():
    """Demonstrate unified interface polymorphic usage"""
    
    print("\n🔗 Unified Interface Example")
    print("=" * 60)
    
    config = SynthesizerConfig(
        project_name="unified-interface-demo",
        tags=["demo", "unified"],
        trace_metadata={"demo_type": "polymorphic"},
        num_scenarios=2
    )
    
    workflow = create_multi_agent_system_swarm_mode()
    
    # List of synthesizers (polymorphic usage)
    synthesizers: List[BaseSynthesizer] = [
        CustomSynthesizer(config, mode=ExecutionMode.SYNTHETIC),
        CustomSynthesizer(config, mode=ExecutionMode.EXECUTION),
        DeepEvalSynthesizer(config)
    ]
    
    synthesizer_names = ["Custom-SYNTHETIC", "Custom-EXECUTION", "DeepEval"]
    
    print("🔄 Running all synthesizers with unified interface...")
    
    all_results = []
    for i, synthesizer in enumerate(synthesizers):
        print(f"\n   Testing {synthesizer_names[i]}:")
        
        try:
            if isinstance(synthesizer, CustomSynthesizer):
                # CustomSynthesizer requires workflow
                examples = await synthesizer.generate_synthetic_dataset(
                    workflow=workflow,
                    num_scenarios=1
                )
            else:
                # DeepEvalSynthesizer can work with or without workflow
                examples = await synthesizer.generate_synthetic_dataset(
                    workflow=workflow,
                    num_scenarios=1
                )
            
            print(f"      ✅ Generated {len(examples)} examples")
            all_results.append((synthesizer_names[i], examples))
            
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            all_results.append((synthesizer_names[i], []))
    
    print(f"\n📊 Unified Interface Results:")
    for name, examples in all_results:
        count = len(examples)
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {name}: {count} examples")
    
    print(f"\n🎯 All synthesizers implement BaseSynthesizer interface")


async def example_production_workflow():
    """Production-ready workflow example with error handling"""
    
    print("\n🏭 Production Workflow Example")
    print("=" * 60)
    
    try:
        config = SynthesizerConfig(
            project_name="production-workflow-demo",
            tags=["production", "demo", "robust"],
            trace_metadata={
                "environment": "production",
                "version": "2.0",
                "workflow_type": "multi_synthesizer"
            },
            num_scenarios=3
        )
        
        workflow = create_multi_agent_system_swarm_mode()
        
        print("📋 Production Workflow Steps:")
        
        # Step 1: Generate baseline with DeepEval
        print("\n1️⃣ Generating baseline dataset...")
        deepeval_synthesizer = DeepEvalSynthesizer(config)
        
        baseline_examples = await deepeval_synthesizer.generate_synthetic_dataset(
            workflow=workflow,
            num_scenarios=3,
            task_description="Production-grade multi-agent system evaluation",
            scenario="Real-world user interactions requiring agent coordination"
        )
        
        print(f"   ✅ Baseline: {len(baseline_examples)} examples")
        
        # Step 2: Generate validation with real execution
        print("\n2️⃣ Generating validation dataset...")
        custom_synthesizer = CustomSynthesizer(config, mode=ExecutionMode.EXECUTION)
        
        validation_examples = await custom_synthesizer.generate_synthetic_dataset(
            workflow=workflow,
            num_scenarios=2
        )
        
        print(f"   ✅ Validation: {len(validation_examples)} examples")
        
        # Step 3: Generate synthetic for volume
        print("\n3️⃣ Generating volume dataset...")
        volume_synthesizer = CustomSynthesizer(config, mode=ExecutionMode.SYNTHETIC)
        
        volume_examples = await volume_synthesizer.generate_synthetic_dataset(
            workflow=workflow,
            num_scenarios=5
        )
        
        print(f"   ✅ Volume: {len(volume_examples)} examples")
        
        total_examples = len(baseline_examples) + len(validation_examples) + len(volume_examples)
        
        print(f"\n📊 Production Workflow Results:")
        print(f"   📈 Total examples: {total_examples}")
        print(f"   🎯 Baseline (DeepEval): {len(baseline_examples)}")
        print(f"   ✅ Validation (Real execution): {len(validation_examples)}")
        print(f"   📦 Volume (Synthetic): {len(volume_examples)}")
        print(f"   🔗 Project: {config.project_name}")
        
        print(f"\n🏷️  All examples tagged and traced to LangSmith for analysis")
        
    except Exception as e:
        print(f"❌ Production workflow failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function to run all enhanced examples"""
    
    print("🚀 Enhanced Synthetic Data Generation Examples")
    print("=" * 80)
    
    try:
        # Run CustomSynthesizer dual modes example
        await example_custom_synthesizer_dual_modes()
        
        # Run DeepEvalSynthesizer enhanced example
        await example_deepeval_with_enhancements()
        
        # Run workflow analysis comparison
        await example_workflow_analysis_comparison()
        
        # Run unified interface example
        await example_unified_interface()
        
        # Run production workflow example
        await example_production_workflow()
        
        print("\n" + "=" * 80)
        print("✅ All enhanced examples completed successfully!")
        print("🎭 CustomSynthesizer: SYNTHETIC vs EXECUTION modes demonstrated")
        print("🎯 DeepEvalSynthesizer: task_description & scenario parameters demonstrated") 
        print("🔍 Workflow analysis: Enhanced generation quality demonstrated")
        print("🔗 Unified interface: Polymorphic usage demonstrated")
        print("🏭 Production workflow: Robust multi-synthesizer pattern demonstrated")
        print("📈 Check LangSmith for comprehensive tracing with dynamic tags")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error running enhanced examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 