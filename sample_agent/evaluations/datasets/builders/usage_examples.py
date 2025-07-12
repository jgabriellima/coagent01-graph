# evaluations/datasets/builders/usage_examples.py

"""
Usage Examples - Clean Architecture
Shows how to use build_dataset() for different scenarios
"""

from datetime import datetime, timedelta
from sample_agent.evaluations.datasets.builders import build_dataset


def basic_usage():
    """Basic dataset building"""
    
    # DeepEval - basic agentic evaluation
    dataset_id = build_dataset(
        project_name="my-project",
        dataset_name="basic_eval",
        framework="deepeval",
        config_name="agentic"
    )
    
    # AgentEvals - trajectory evaluation
    dataset_id = build_dataset(
        project_name="my-project",
        dataset_name="trajectory_eval",
        framework="agentevals",
        config_name="trajectory"
    )
    
    return dataset_id


def tag_filtering():
    """Tag-based filtering examples"""
    
    # Alice agent specific
    dataset_id = build_dataset(
        project_name="swarm-project",
        dataset_name="alice_eval",
        tags=["Alice-Agent"]
    )
    
    # Main swarm system
    dataset_id = build_dataset(
        project_name="swarm-project",
        dataset_name="swarm_eval",
        tags=["main-swarm"]
    )
    
    # Multiple tags (OR logic)
    dataset_id = build_dataset(
        project_name="swarm-project",
        dataset_name="agents_eval",
        tags=["Alice-Agent", "Bob-Agent"]
    )
    
    return dataset_id


def time_filtering():
    """Time-based filtering examples"""
    
    # Today only
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dataset_id = build_dataset(
        project_name="my-project",
        dataset_name="daily_eval",
        tags=["my-agent"],
        start_time=today,
        end_time=today + timedelta(days=1)
    )
    
    # Last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    dataset_id = build_dataset(
        project_name="my-project",
        dataset_name="weekly_eval",
        tags=["my-agent"],
        start_time=week_ago,
        end_time=datetime.now()
    )
    
    return dataset_id


def error_analysis():
    """Error analysis examples"""
    
    # Failed runs only
    dataset_id = build_dataset(
        project_name="my-project",
        dataset_name="error_analysis",
        tags=["my-agent"],
        error=True,
        limit=100
    )
    
    # Successful runs only  
    dataset_id = build_dataset(
        project_name="my-project",
        dataset_name="success_analysis",
        tags=["my-agent"],
        error=False,
        limit=1000
    )
    
    return dataset_id


def advanced_filtering():
    """Advanced filtering examples"""
    
    # Custom filter for math tasks
    dataset_id = build_dataset(
        project_name="my-project",
        dataset_name="math_tasks",
        tags=["Alice-Agent"],
        filter='has(math_expression) AND duration > 1000'
    )
    
    # Tool usage analysis
    dataset_id = build_dataset(
        project_name="my-project",
        dataset_name="tool_usage",
        framework="deepeval",
        config_name="tool_use",
        tags=["my-agent"],
        filter='has(tool_calls)'
    )
    
    return dataset_id


def swarm_examples():
    """Swarm-specific examples"""
    
    # Alice math evaluation
    alice_dataset = build_dataset(
        project_name="swarm-project",
        dataset_name="alice_math",
        tags=["Alice-Agent"],
        filter='has(math_expression)'
    )
    
    # Bob weather evaluation  
    bob_dataset = build_dataset(
        project_name="swarm-project",
        dataset_name="bob_weather",
        tags=["Bob-Agent"],
        filter='has(weather)'
    )
    
    # Main agent coordination
    main_dataset = build_dataset(
        project_name="swarm-project",
        dataset_name="main_coordination",
        tags=["Main-Agent"],
        filter='has(agent_handoffs)'
    )
    
    return alice_dataset, bob_dataset, main_dataset


def langgraph_examples():
    """LangGraph usage - works directly without transformation"""
    
    # Tool usage evaluation with LangGraph traces
    dataset_id = build_dataset(
        project_name="langgraph-project",
        dataset_name="langgraph_eval",
        framework="deepeval",
        config_name="tool_use",
        tags=["react-agent"]
    )
    
    # Trajectory evaluation with LangGraph traces
    dataset_id = build_dataset(
        project_name="langgraph-project",
        dataset_name="trajectory_eval",
        framework="agentevals",
        config_name="trajectory",
        tags=["swarm-agent"]
    )
    
    return dataset_id


# How to implement daily jobs using build_dataset()
def daily_job_example():
    """
    Example of how you would implement daily jobs
    Use this pattern in your own orchestration
    """
    
    project_name = "my-project"
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    date_str = today.strftime("%Y%m%d")
    
    # Daily performance
    performance_dataset = build_dataset(
        project_name=project_name,
        dataset_name=f"daily_performance_{date_str}",
        framework="deepeval",
        config_name="agentic",
        tags=["main-system"],
        start_time=today,
        end_time=today + timedelta(days=1),
        error=False,
        limit=1000
    )
    
    # Daily errors
    error_dataset = build_dataset(
        project_name=project_name,
        dataset_name=f"daily_errors_{date_str}",
        framework="deepeval",
        config_name="agentic",
        tags=["main-system"],
        start_time=today,
        end_time=today + timedelta(days=1),
        error=True,
        limit=200
    )
    
    # Tool usage
    tool_dataset = build_dataset(
        project_name=project_name,
        dataset_name=f"daily_tools_{date_str}",
        framework="deepeval",
        config_name="tool_use",
        tags=["tool-usage"],
        start_time=today,
        end_time=today + timedelta(days=1),
        filter="has(tool_calls)"
    )
    
    return performance_dataset, error_dataset, tool_dataset


if __name__ == "__main__":
    print("=== Usage Examples ===")
    print("Shows how to use build_dataset() for different scenarios")
    print()
    
    print("Available examples:")
    print("- basic_usage() - Basic framework usage")
    print("- tag_filtering() - Filter by agent tags")
    print("- time_filtering() - Filter by time ranges")
    print("- error_analysis() - Analyze failures/successes")
    print("- advanced_filtering() - Custom filters")
    print("- swarm_examples() - Multi-agent swarm")
    print("- langgraph_examples() - LangGraph integration")
    print("- daily_job_example() - Daily job pattern")
    print()
    
    print("Key principles:")
    print("✅ Use build_dataset() directly")
    print("✅ Implement your own orchestration")
    print("✅ Tag-based filtering: tags=['Alice-Agent']")
    print("✅ Time-based filtering: start_time, end_time")
    print("✅ Custom filters: filter='has(math_expression)'")
    print()
    
    print("Remember: These are patterns, not abstractions!")
    print("Copy and modify for your specific needs.") 