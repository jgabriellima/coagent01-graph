# Usage Examples Consolidation

## Problem Identified

We had **3 redundant example files** doing similar things:
- `simple_usage.py` (140 lines) - Basic usage examples
- `pipeline_examples.py` (259 lines) - Complex orchestration with abstractions
- `clean_usage.py` (266 lines) - Swarm-specific examples

**Total: 665 lines of redundant code**

## Issues with Previous Approach

### ❌ `pipeline_examples.py` - Against Core Philosophy
```python
# Created orchestration abstractions
def run_daily_jobs(project_name, agent_tags, jobs_to_run):
def example_swarm_pipeline(project_name):
def example_basic_pipeline(project_name):
```

These functions could be **confused with core architecture**, violating our **"base vs usage"** principle.

### ❌ Redundancy 
All 3 files showed similar patterns:
- Tag filtering: `tags=["Alice-Agent"]`
- Time filtering: `start_time`, `end_time`
- Error analysis: `error=True`
- Framework usage: `framework="deepeval"`

## Solution: Single Consolidated File

### ✅ `usage_examples.py` - Clean Architecture
```python
# Shows patterns, not abstractions
def basic_usage():
    dataset_id = build_dataset(...)
    return dataset_id

def tag_filtering():
    dataset_id = build_dataset(tags=["Alice-Agent"])
    return dataset_id

def daily_job_example():
    # Pattern for daily jobs - user implements their own orchestration
    performance_dataset = build_dataset(...)
    error_dataset = build_dataset(...)
    return performance_dataset, error_dataset
```

## Key Principles Maintained

### ✅ Base vs Usage Separation
- **Base**: Only `build_dataset()` function
- **Usage**: User responsibility to implement daily/weekly/orchestration

### ✅ No Orchestration Abstractions
- Shows **patterns**, not **functions**
- User copies and modifies for their needs
- No confusion with core architecture

### ✅ Clean Examples
- Direct usage of `build_dataset()`
- Clear, focused examples
- All common scenarios covered

## Files After Cleanup

**Core (Essential):**
- `generic_builder.py` - Implementation
- `__init__.py` - Interface exports
- `usage_examples.py` - Single example file

**Documentation:**
- `README.md` - Overview
- `FILTERS.md` - Filter reference

**Removed:**
- ❌ `simple_usage.py` - Redundant
- ❌ `pipeline_examples.py` - Against philosophy
- ❌ `clean_usage.py` - Redundant

## Benefits

1. **Reduced Complexity**: 3 files → 1 file
2. **Clear Philosophy**: No orchestration abstractions
3. **Easier Maintenance**: Single source of examples
4. **User Freedom**: Copy patterns, implement own orchestration
5. **Reduced Confusion**: Clear separation of base vs usage

## Usage

```python
# Copy patterns from usage_examples.py
from sample_agent.evaluations.datasets.builders import build_dataset

# Daily job (your implementation)
def my_daily_job():
    return build_dataset(
        project_name="my-project",
        dataset_name="daily_eval",
        tags=["my-agent"],
        start_time=today,
        end_time=today + timedelta(days=1)
    )
```

**Remember**: These are **patterns, not abstractions**. Copy and modify for your specific needs. 