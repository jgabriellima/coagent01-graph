#!/usr/bin/env python3
"""
Usage examples for the WorkflowAnalyzer
"""

from sample_agent.analysis.workflow_analyzer import (
    WorkflowAnalyzer,
    WorkflowAnalysisConfig,
)
from pathlib import Path


def analyze_tce_swarm_workflow():
    """Example: Analyze the TCE Swarm workflow."""
    try:
        # Import the workflow
        from sample_agent.agents.tce_swarm.graph import tce_swarm_graph

        # Create the workflow
        workflow = tce_swarm_graph

        # Create analyzer with custom config
        config = WorkflowAnalysisConfig(
            save_to_file=True, output_file=Path("tce_swarm_analysis.json")
        )
        analyzer = WorkflowAnalyzer(config)

        # Analyze the workflow
        analysis = analyzer.analyze_workflow(workflow)

        # Print results
        analyzer.print_analysis(analysis)

        return analysis

    except Exception as e:
        print(f"Error analyzing TCE Swarm workflow: {e}")
        return None


if __name__ == "__main__":
    print("🔍 Analyzing workflows...")

    # Analyze TCE Swarm workflow
    print("\n1. TCE Swarm Workflow:")
    analyze_tce_swarm_workflow()
