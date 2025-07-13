#!/usr/bin/env python3
"""
Workflow Analysis Usage Examples
===============================

Example usage of the WorkflowAnalyzer for generating technical blueprints.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sample_agent.analysis import WorkflowAnalyzer, WorkflowAnalysisConfig
from sample_agent.agents.swarm.graph import create_multi_agent_system_swarm_mode


def example_structured_llm_analysis():
    """
    Example: Generate comprehensive workflow blueprint using GPT-4o
    
    This demonstrates:
    - Agent role analysis via LLM
    - Tool extraction and handoff detection
    - Technical blueprint generation
    - Structured output with Pydantic models
    """
    
    print("🔧 WORKFLOW BLUEPRINT GENERATION EXAMPLE")
    print("=" * 60)
    
    # Create workflow
    workflow = create_multi_agent_system_swarm_mode()
    
    # Configure blueprint generation
    config = WorkflowAnalysisConfig(
        save_to_file=True,
        output_file=Path("workflow_blueprint_example.json")
    )
    
    # Generate blueprint
    print("🤖 Generating technical blueprint...")
    analyzer = WorkflowAnalyzer(config)
    
    try:
        blueprint = analyzer.analyze_workflow(workflow)
        
        print(f"\n📊 BLUEPRINT SUMMARY:")
        print(f"• Workflow Type: {blueprint.workflow_type}")
        print(f"• Description: {blueprint.description}")
        print(f"• Agents: {blueprint.agent_count}")
        print(f"• Total Tools: {blueprint.total_tools}")
        
        print(f"\n🤖 AGENT BREAKDOWN:")
        for agent_name, agent_bp in blueprint.agents.items():
            print(f"\n{agent_name}:")
            print(f"  • Role: {agent_bp.role}")
            print(f"  • Tools: {len(agent_bp.tools)}")
            print(f"  • Handoffs: {len(agent_bp.handoffs)}")
            
            # Show handoff targets
            if agent_bp.handoffs:
                print(f"  • Can handoff to: {', '.join(agent_bp.handoffs)}")
            
            # Show tool types
            regular_tools = [t for t in agent_bp.tools if not t.is_handoff]
            handoff_tools = [t for t in agent_bp.tools if t.is_handoff]
            
            if regular_tools:
                print(f"  • Regular tools: {len(regular_tools)}")
            if handoff_tools:
                print(f"  • Handoff tools: {len(handoff_tools)}")
        
        print(f"\n💡 BLUEPRINT INSIGHTS:")
        print(f"• Blueprint successfully generated using GPT-4o")
        print(f"• All agent roles analyzed via LLM structured output")
        print(f"• Tool classifications completed automatically")
        print(f"• Handoff relationships extracted successfully")
        
        return blueprint
        
    except Exception as e:
        print(f"❌ Blueprint generation failed: {e}")
        raise


if __name__ == "__main__":
    example_structured_llm_analysis() 