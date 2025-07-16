# Dataset Filtering Guide

## Overview

The generic dataset builder now supports **full LangSmith filtering** with a **simplified interface**.

## Quick Start

### Daily Evaluation (Most Common)
```python
from evaluations.datasets.builders import build_daily_dataset

# Build dataset for today only
dataset_id = build_daily_dataset(
    project_name="your-project",
    dataset_name="daily_eval_20250101",
    framework="deepeval"
)
```

### Custom Date Range
```python
from evaluations.datasets.builders import build_dataset
from datetime import datetime, timedelta

today = datetime.now()
week_ago = today - timedelta(days=7)

dataset_id = build_dataset(
    project_name="your-project",
    dataset_name="weekly_eval",
    framework="deepeval",
    config_name="agentic",
    start_time=week_ago,
    end_time=today
)
```

### Tag-Based Filtering (New!)
```python
# Filter for specific agent
dataset_id = build_dataset(
    project_name="swarm-project",
    dataset_name="alice_only",
    framework="deepeval",
    tags=["Alice-Agent"]
)

# Filter for complete swarm system
dataset_id = build_dataset(
    project_name="swarm-project",
    dataset_name="swarm_system",
    framework="deepeval", 
    tags=["main-swarm"]
)
```

## Available Filters

### Time-based Filters
- `start_time` - Filter traces after this time
- `end_time` - Filter traces before this time  
- `target_date` - For daily datasets (convenience)

### Tag Filters (New!)
- `tags=["Alice-Agent"]` - Filter by specific agent tags
- `tags=["main-swarm"]` - Filter by system-wide tags
- `tags=["Alice-Agent", "Bob-Agent"]` - Multiple tags (OR logic)

### Content Filters
- `filter` - LangSmith filter string (e.g., `'has(tool_calls)'`)
- `trace_filter` - Filter on root run attributes
- `tree_filter` - Filter on any run in trace tree

### Status Filters
- `error=True` - Only failed runs
- `error=False` - Only successful runs
- `is_root=True` - Only root traces

### Limit & Selection
- `limit=1000` - Maximum number of traces
- `run_type="chain"` - Type of runs to include

## Common Use Cases

### 1. Daily Evaluation Job
```python
# Most common - evaluate today's traces
build_daily_dataset(
    project_name="swarm-project",
    dataset_name="daily_20250101",
    framework="deepeval"
)
```

### 2. Error Analysis
```python
# Analyze failed runs from last 3 days
build_dataset(
    project_name="swarm-project",
    dataset_name="errors_analysis",
    framework="deepeval",
    start_time=datetime.now() - timedelta(days=3),
    error=True,
    limit=500
)
```

### 3. Tool Usage Analysis
```python
# Analyze traces with tool calls
build_dataset(
    project_name="swarm-project",
    dataset_name="tool_usage",
    framework="deepeval",
    filter='has(tool_calls)',
    is_root=True
)
```

### 4. Agent-Specific Analysis
```python
# Analyze specific agent performance
build_dataset(
    project_name="swarm-project",
    dataset_name="alice_math",
    framework="deepeval",
    tags=["Alice-Agent"],
    filter='has(math_expression)',
    start_time=datetime.now() - timedelta(days=1)
)
```

## For Your Swarm Setup

Your multi-agent swarm has:
- **Alice** (math) - filter: `'has(math_expression)'`
- **Bob** (weather) - filter: `'has(weather)'`  
- **Main_Agent** (coordination) - filter: `'has(agent_handoffs)'`

```python
# Example: Daily evaluation for Alice
build_dataset(
    project_name="swarm-project",
    dataset_name="alice_daily",
    framework="deepeval",
    tags=["Alice-Agent"],
    filter='has(math_expression)',
    start_time=datetime.now().replace(hour=0, minute=0, second=0)
)
```

## Integration with Cron Jobs

```bash
# Daily at 2 AM
0 2 * * * python -c "from evaluations.datasets.builders.simple_usage import daily_evaluation_job; daily_evaluation_job('your-project')"

# Weekly on Sundays at 6 AM  
0 6 * * 0 python -c "from evaluations.datasets.builders.simple_usage import weekly_evaluation_job; weekly_evaluation_job('your-project')"
```

## Key Benefits

✅ **Simple**: Single `build_dataset()` function  
✅ **Tag-based**: Filter by agent tags (`tags=["Alice-Agent"]`)  
✅ **Flexible**: All LangSmith filters supported  
✅ **Efficient**: Filter at source, not after fetching  
✅ **Production-ready**: Built for scheduled jobs  

No more complex pre-processing - filter exactly what you need! 