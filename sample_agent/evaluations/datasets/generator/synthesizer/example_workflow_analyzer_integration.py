#!/usr/bin/env python3
"""
WorkflowAnalyzer Integration Example
===================================

Demonstrates how to integrate the WorkflowAnalyzer utility with synthetic data generation.
Shows practical usage across different contexts: development, synthetic data generation,
and workflow optimization.
"""

import asyncio
from pathlib import Path
import sys
from typing import Dict, Any, List

# Add path to import dependencies
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from sample_agent.agents.swarm.graph import create_multi_agent_system_swarm_mode
from sample_agent.analysis import WorkflowAnalyzer, WorkflowAnalysisConfig, analyze_workflow
from sample_agent.evaluations.datasets.generator.synthesizer import (
    CustomSynthesizer,
    DeepEvalSynthesizer,
    SynthesizerConfig,
    ExecutionMode,
)


async def example_workflow_analysis_for_synthetic_data():
    """Example: Using WorkflowAnalyzer to enhance synthetic data generation"""
    
    print("🔬 Workflow Analysis for Synthetic Data Generation")
    print("=" * 60)
    
    # Create workflow
    workflow = create_multi_agent_system_swarm_mode()
    
    # Configure detailed analysis
    analysis_config = WorkflowAnalysisConfig(
        include_detailed_agents=True,
        include_workflow_insights=True,
        include_complexity_assessment=True,
        save_to_file=True,
        output_file=Path("workflow_analysis_for_synthetic_data.json")
    )
    
    # Analyze workflow
    print("🔍 Analyzing workflow structure...")
    analyzer = WorkflowAnalyzer(analysis_config)
    analysis = analyzer.analyze_workflow(workflow)
    
    # Extract insights for data generation
    print("\n📊 Extracting synthetic data generation insights...")
    insights = analysis.get("workflow_insights", {})
    detailed_agents = analysis.get("detailed_agents", {})
    complexity = analysis.get("complexity_assessment", {})
    
    print(f"   • Agent Count: {insights.get('agent_count', 0)}")
    print(f"   • Complexity Level: {insights.get('complexity_level', 'unknown')}")
    print(f"   • Collaboration Pattern: {insights.get('collaboration_pattern', 'unknown')}")
    
    # Generate scenarios based on analysis
    print("\n🎭 Generating scenarios based on workflow analysis...")
    scenarios = generate_scenarios_from_analysis(analysis)
    
    print(f"   • Generated {len(scenarios)} scenarios")
    for i, scenario in enumerate(scenarios[:3]):  # Show first 3
        print(f"   • Scenario {i+1}: {scenario['complexity']} - {scenario['target_agents']}")
    
    # Use analysis to configure synthesizer
    print("\n⚙️ Configuring synthesizer based on analysis...")
    synth_config = create_synthesizer_config_from_analysis(analysis)
    
    # Run synthetic data generation
    print("\n🔄 Running synthetic data generation...")
    synthesizer = CustomSynthesizer(synth_config, mode=ExecutionMode.SYNTHETIC)
    
    examples = await synthesizer.generate_synthetic_dataset(
        workflow=workflow, 
        num_scenarios=3
    )
    
    print(f"   ✅ Generated {len(examples)} synthetic examples")
    
    return analysis, examples


def generate_scenarios_from_analysis(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate scenarios based on workflow analysis results"""
    
    detailed_agents = analysis.get("detailed_agents", {})
    complexity = analysis.get("complexity_assessment", {})
    
    scenarios = []
    
    # Generate scenarios based on agent capabilities
    for agent_name, agent_info in detailed_agents.items():
        capabilities = agent_info.get("capabilities", [])
        tools = agent_info.get("tools", [])
        
        # Simple scenario
        scenarios.append({
            "complexity": "simple",
            "target_agents": [agent_name],
            "description": f"Simple task using {agent_name}",
            "capabilities_needed": capabilities[:1],
            "tools_needed": tools[:1]
        })
        
        # Complex scenario involving multiple capabilities
        if len(capabilities) > 1:
            scenarios.append({
                "complexity": "complex",
                "target_agents": [agent_name],
                "description": f"Complex task requiring multiple capabilities from {agent_name}",
                "capabilities_needed": capabilities,
                "tools_needed": tools
            })
    
    # Multi-agent scenarios
    if len(detailed_agents) > 1:
        agent_names = list(detailed_agents.keys())
        scenarios.append({
            "complexity": "complex",
            "target_agents": agent_names,
            "description": "Multi-agent coordination scenario",
            "capabilities_needed": [],
            "tools_needed": []
        })
    
    return scenarios


def create_synthesizer_config_from_analysis(analysis: Dict[str, Any]) -> SynthesizerConfig:
    """Create synthesizer configuration based on workflow analysis"""
    
    insights = analysis.get("workflow_insights", {})
    complexity = analysis.get("complexity_assessment", {})
    
    # Base configuration
    project_name = f"synthetic-data-{insights.get('workflow_type', 'unknown').lower().replace(' ', '-')}"
    
    # Dynamic tags based on analysis
    tags = ["synthetic", "workflow-analysis-enhanced"]
    tags.append(f"complexity:{insights.get('complexity_level', 'unknown')}")
    tags.append(f"agents:{insights.get('agent_count', 0)}")
    tags.append(f"collaboration:{insights.get('collaboration_pattern', 'unknown').lower().replace(' ', '-')}")
    
    # Metadata based on analysis
    metadata = {
        "workflow_type": insights.get("workflow_type", "unknown"),
        "complexity_level": insights.get("complexity_level", "unknown"),
        "agent_count": insights.get("agent_count", 0),
        "total_capabilities": insights.get("total_capabilities", 0),
        "total_tools": insights.get("total_tools", 0),
        "collaboration_pattern": insights.get("collaboration_pattern", "unknown"),
        "scalability_assessment": insights.get("scalability_assessment", "unknown"),
        "analysis_timestamp": analysis.get("timestamp", "unknown")
    }
    
    # Adjust number of scenarios based on complexity
    complexity_level = insights.get("complexity_level", "medium")
    if complexity_level == "low":
        num_scenarios = 5
    elif complexity_level == "medium":
        num_scenarios = 10
    else:  # high
        num_scenarios = 15
    
    return SynthesizerConfig(
        project_name=project_name,
        tags=tags,
        trace_metadata=metadata,
        num_scenarios=num_scenarios
    )


async def example_development_workflow_inspection():
    """Example: Using WorkflowAnalyzer during development"""
    
    print("\n🛠️ Development Workflow Inspection")
    print("=" * 60)
    
    # Create workflow
    workflow = create_multi_agent_system_swarm_mode()
    
    # Quick analysis for development
    print("🔍 Quick workflow inspection...")
    analysis = analyze_workflow(
        workflow=workflow,
        config=WorkflowAnalysisConfig(
            include_detailed_agents=True,
            include_workflow_insights=False,
            include_complexity_assessment=False,
            save_to_file=False
        ),
        print_report=False
    )
    
    # Development-focused insights
    print("\n📋 Development Insights:")
    agents = analysis.get("agents", {})
    print(f"   • Agents: {len(agents)}")
    
    for agent_name, agent_info in agents.items():
        capabilities = agent_info.get("capabilities", [])
        tools = agent_info.get("tools", [])
        print(f"   • {agent_name}: {len(capabilities)} capabilities, {len(tools)} tools")
    
    print(f"   • Total capabilities: {len(analysis.get('capabilities', []))}")
    print(f"   • Total tools: {len(analysis.get('tools', []))}")
    
    return analysis


async def example_optimization_insights():
    """Example: Using WorkflowAnalyzer for optimization insights"""
    
    print("\n⚡ Workflow Optimization Insights")
    print("=" * 60)
    
    # Create workflow
    workflow = create_multi_agent_system_swarm_mode()
    
    # Analysis focused on optimization
    print("🔍 Analyzing for optimization opportunities...")
    analysis = analyze_workflow(
        workflow=workflow,
        config=WorkflowAnalysisConfig(
            include_detailed_agents=False,
            include_workflow_insights=True,
            include_complexity_assessment=True,
            save_to_file=False
        ),
        print_report=False
    )
    
    # Extract optimization insights
    print("\n🚀 Optimization Insights:")
    insights = analysis.get("workflow_insights", {})
    complexity = analysis.get("complexity_assessment", {})
    
    print(f"   • Scalability: {insights.get('scalability_assessment', 'unknown')}")
    print(f"   • Collaboration Pattern: {insights.get('collaboration_pattern', 'unknown')}")
    print(f"   • Overall Complexity: {complexity.get('overall_complexity', 'unknown')}")
    
    # Show recommendations
    recommendations = complexity.get("optimization_recommendations", [])
    if recommendations:
        print("\n📋 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    return analysis


async def example_comparative_analysis():
    """Example: Comparing different workflow configurations"""
    
    print("\n📊 Comparative Workflow Analysis")
    print("=" * 60)
    
    # Create workflows (in real scenario, you'd have different configurations)
    workflow1 = create_multi_agent_system_swarm_mode()
    # workflow2 = create_different_workflow_configuration()  # Hypothetical
    
    # Analyze first workflow
    print("🔍 Analyzing Workflow 1...")
    analysis1 = analyze_workflow(
        workflow=workflow1,
        config=WorkflowAnalysisConfig(save_to_file=False),
        print_report=False
    )
    
    # In real scenario, you'd analyze workflow2 as well
    # analysis2 = analyze_workflow(workflow2, ...)
    
    # Comparative insights
    print("\n📋 Comparative Analysis:")
    insights1 = analysis1.get("workflow_insights", {})
    complexity1 = analysis1.get("complexity_assessment", {})
    
    print(f"   Workflow 1:")
    print(f"   • Agents: {insights1.get('agent_count', 0)}")
    print(f"   • Complexity: {insights1.get('complexity_level', 'unknown')}")
    print(f"   • Scalability: {insights1.get('scalability_assessment', 'unknown')}")
    
    # You would compare with workflow2 here
    print(f"   \n   Comparison would show differences in:")
    print(f"   • Agent coordination efficiency")
    print(f"   • Tool utilization patterns")
    print(f"   • Complexity management")
    
    return analysis1


async def example_enhanced_deepeval_generation():
    """Example: Using WorkflowAnalyzer to enhance DeepEval generation"""
    
    print("\n🤖 Enhanced DeepEval Generation")
    print("=" * 60)
    
    # Create workflow
    workflow = create_multi_agent_system_swarm_mode()
    
    # Analyze workflow first
    print("🔍 Analyzing workflow for DeepEval enhancement...")
    analysis = analyze_workflow(
        workflow=workflow,
        config=WorkflowAnalysisConfig(save_to_file=False),
        print_report=False
    )
    
    # Extract information for enhanced generation
    insights = analysis.get("workflow_insights", {})
    detailed_agents = analysis.get("detailed_agents", {})
    
    # Create enhanced task description
    agent_names = list(detailed_agents.keys())
    task_description = f"Multi-agent system with {len(agent_names)} agents: {', '.join(agent_names)}"
    
    # Create enhanced scenario
    capabilities = analysis.get("capabilities", [])
    tools = analysis.get("tools", [])
    scenario = f"Agents coordinate using {len(tools)} tools to handle user requests. System complexity: {insights.get('complexity_level', 'unknown')}"
    
    # Configure synthesizer
    config = SynthesizerConfig(
        project_name="enhanced-deepeval-demo",
        tags=["deepeval", "enhanced", "workflow-analysis"],
        trace_metadata={"enhancement_type": "workflow_analysis"},
        num_scenarios=3
    )
    
    # Generate with enhanced descriptions
    print("🔄 Generating with enhanced descriptions...")
    synthesizer = DeepEvalSynthesizer(config)
    
    examples = await synthesizer.generate_synthetic_dataset(
        workflow=workflow,
        num_scenarios=3,
        task_description=task_description,
        scenario=scenario
    )
    
    print(f"   ✅ Generated {len(examples)} enhanced examples")
    
    return analysis, examples


async def main():
    """Run all examples"""
    
    print("🚀 WorkflowAnalyzer Integration Examples")
    print("=" * 80)
    
    # Run examples
    try:
        # Main example: Synthetic data generation
        analysis1, examples1 = await example_workflow_analysis_for_synthetic_data()
        
        # Development inspection
        analysis2 = await example_development_workflow_inspection()
        
        # Optimization insights
        analysis3 = await example_optimization_insights()
        
        # Comparative analysis
        analysis4 = await example_comparative_analysis()
        
        # Enhanced DeepEval generation
        analysis5, examples5 = await example_enhanced_deepeval_generation()
        
        print("\n✅ All examples completed successfully!")
        print(f"   • Total analyses performed: 5")
        print(f"   • Total synthetic examples generated: {len(examples1) + len(examples5)}")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 