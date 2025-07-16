#!/usr/bin/env python3
"""
Workflow Analysis Test
=====================

Test script for the workflow analysis utility.
Demonstrates how to use the WorkflowAnalyzer for generating technical blueprints.

Usage:
    python test_workflow_analysis.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.analysis import WorkflowAnalyzer, WorkflowAnalysisConfig
from src.agents.swarm.graph import create_multi_agent_system_swarm_mode


async def test_workflow_analysis():
    """Test the workflow analysis utility with GPT-4o blueprint generation"""
    
    print("🚀 Testing Workflow Blueprint Generation...")
    
    # Create workflow
    print("📝 Creating multi-agent workflow...")
    workflow = create_multi_agent_system_swarm_mode()
    
    # Configure analysis
    config = WorkflowAnalysisConfig(
        save_to_file=True,
        output_file=Path("workflow_blueprint.json")
    )
    
    # Generate blueprint
    print("🔧 Generating technical blueprint...")
    analyzer = WorkflowAnalyzer(config)
    
    try:
        blueprint = analyzer.analyze_workflow(workflow)
        
        # Print blueprint
        analyzer.print_blueprint(blueprint)
        
        # Show summary
        print(f"\n✅ Blueprint generated successfully!")
        print(f"   • {blueprint.agent_count} agents analyzed")
        print(f"   • {blueprint.total_tools} total tools")
        print(f"   • Workflow type: {blueprint.workflow_type}")
        
        # Show agent details
        for agent_name, agent_bp in blueprint.agents.items():
            handoff_count = len(agent_bp.handoffs)
            tool_count = len(agent_bp.tools)
            print(f"   • {agent_name}: {tool_count} tools, {handoff_count} handoffs")
        
        return blueprint
        
    except Exception as e:
        print(f"❌ Blueprint generation failed: {e}")
        raise


def test_usage_example():
    """Test the main usage example"""
    
    print("\n🔬 Testing Usage Example...")
    
    # Import and run the main example
    from src.analysis.usage_examples import example_structured_llm_analysis
    
    try:
        analysis = example_structured_llm_analysis()
        print("✅ Usage example test completed!")
        return analysis
    except Exception as e:
        print(f"❌ Usage example failed: {e}")
        raise


if __name__ == "__main__":
    # Run async test
    asyncio.run(test_workflow_analysis())
    
    # Run usage example test
    test_usage_example() 