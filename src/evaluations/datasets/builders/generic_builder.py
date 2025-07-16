# evaluations/datasets/builders/generic_builder.py

from typing import Dict, List, Any, Optional, Callable
from langsmith import Client
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta


class EvaluationFramework(Enum):
    DEEPEVAL = "deepeval"
    AGENTEVALS = "agentevals"
    CUSTOM = "custom"


@dataclass
class DatasetConfig:
    """Configuration for dataset generation"""
    framework: EvaluationFramework
    input_fields: List[str]
    output_fields: List[str]
    metadata_fields: List[str]
    filter_tags: List[str]
    run_type: str = "chain"
    transform_fn: Optional[Callable] = None
    
    # LangSmith filters
    start_time: Optional[Any] = None
    end_time: Optional[Any] = None
    filter: Optional[str] = None
    trace_filter: Optional[str] = None
    tree_filter: Optional[str] = None
    is_root: Optional[bool] = None
    error: Optional[bool] = None
    limit: Optional[int] = None


class GenericDatasetBuilder:
    """Generic dataset builder for LangGraph traces compatible with evaluation frameworks"""
    
    def __init__(self, client: Optional[Client] = None):
        self.client = client or Client()
        
    def build_dataset(
        self, 
        project_name: str, 
        dataset_name: str,
        config: DatasetConfig,
        **additional_filters
    ) -> str:
        """Build evaluation dataset from LangSmith traces"""
        
        # Fetch traces
        traces = self._fetch_traces(project_name, config, **additional_filters)
        
        # Transform traces based on framework requirements
        processed_traces = self._process_traces(traces, config)
        
        # Create dataset
        dataset = self.client.create_or_update_dataset(name=dataset_name)
        
        # Add examples
        for trace in processed_traces:
            self.client.create_example(
                dataset_id=dataset.id,
                inputs=trace["inputs"],
                outputs=trace["outputs"],
                metadata=trace.get("metadata", {})
            )
        
        return dataset.id
    
    def _fetch_traces(self, project_name: str, config: DatasetConfig, **additional_filters) -> List[Dict]:
        """Fetch traces from LangSmith project with comprehensive filtering"""
        
        # Build filter parameters
        filter_params = {
            "project_name": project_name,
            "run_type": config.run_type,
        }
        
        # Add LangSmith filters from config
        if config.start_time:
            filter_params["start_time"] = config.start_time
        if config.filter:
            filter_params["filter"] = config.filter
        if config.trace_filter:
            filter_params["trace_filter"] = config.trace_filter
        if config.tree_filter:
            filter_params["tree_filter"] = config.tree_filter
        if config.is_root is not None:
            filter_params["is_root"] = config.is_root
        if config.error is not None:
            filter_params["error"] = config.error
        if config.limit:
            filter_params["limit"] = config.limit
        
        # Add additional filters (allows overriding)
        filter_params.update(additional_filters)
        
        # Fetch runs with filters
        runs = self.client.list_runs(**filter_params)
        
        # Apply tag filtering (if specified)
        if config.filter_tags:
            filtered_runs = []
            for run in runs:
                if self._should_include_run(run, config):
                    filtered_runs.append(run)
            return filtered_runs
        
        return list(runs)
    
    def _should_include_run(self, run, config: DatasetConfig) -> bool:
        """Check if run should be included based on tags"""
        if not config.filter_tags:
            return True
        
        run_tags = getattr(run, 'tags', []) or []
        return any(tag in run_tags for tag in config.filter_tags)
    
    def _process_traces(self, traces: List[Dict], config: DatasetConfig) -> List[Dict]:
        """Process traces based on evaluation framework requirements"""
        processed = []
        
        for trace in traces:
            # Extract inputs
            inputs = self._extract_fields(trace.inputs, config.input_fields)
            
            # Extract outputs
            outputs = self._extract_fields(trace.outputs, config.output_fields)
            
            # Extract metadata
            metadata = self._extract_metadata(trace, config)
            
            # Apply custom transformation if provided
            if config.transform_fn:
                inputs, outputs, metadata = config.transform_fn(inputs, outputs, metadata, trace)
            
            processed.append({
                "inputs": inputs,
                "outputs": outputs,
                "metadata": metadata
            })
        
        return processed
    
    def _extract_fields(self, data: Dict, field_names: List[str]) -> Dict:
        """Extract specified fields from data"""
        if not field_names:
            return data
        
        result = {}
        for field in field_names:
            if '.' in field:
                # Support nested field access
                value = self._get_nested_value(data, field.split('.'))
            else:
                value = data.get(field)
            
            if value is not None:
                result[field] = value
        
        return result
    
    def _get_nested_value(self, data: Dict, keys: List[str]) -> Any:
        """Get nested value from dictionary"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _extract_metadata(self, trace, config: DatasetConfig) -> Dict:
        """Extract metadata from trace"""
        metadata = {
            "trace_id": getattr(trace, 'id', None),
            "run_type": getattr(trace, 'run_type', None),
            "tags": getattr(trace, 'tags', []),
            "framework": config.framework.value
        }
        
        # Add custom metadata fields
        for field in config.metadata_fields:
            if hasattr(trace, field):
                metadata[field] = getattr(trace, field)
        
        return metadata


# Predefined configurations for common evaluation scenarios
DEEPEVAL_CONFIGS = {
    "agentic": DatasetConfig(
        framework=EvaluationFramework.DEEPEVAL,
        input_fields=["input", "query"],
        output_fields=["output", "response"],
        metadata_fields=["start_time", "end_time", "total_tokens"],
        filter_tags=["agentic", "agent"],
        run_type="chain"
    ),
    
    "tool_use": DatasetConfig(
        framework=EvaluationFramework.DEEPEVAL,
        input_fields=["input"],
        output_fields=["output", "tool_calls"],
        metadata_fields=["tools_used", "execution_time"],
        filter_tags=["tool_use", "function_calling"],
        run_type="chain"
    )
}

AGENTEVALS_CONFIGS = {
    "trajectory": DatasetConfig(
        framework=EvaluationFramework.AGENTEVALS,
        input_fields=["input", "messages"],
        output_fields=["output", "steps", "final_answer"],
        metadata_fields=["trajectory_length", "tools_used"],
        filter_tags=["trajectory", "multi_step"],
        run_type="chain"
    )
}


# Main interface functions

def build_dataset(
    project_name: str,
    dataset_name: str,
    framework: str = "deepeval",
    config_name: str = "agentic",
    tags: Optional[List[str]] = None,
    **filters
) -> str:
    """
    Build evaluation dataset with smart filtering
    
    Args:
        project_name: LangSmith project name
        dataset_name: Name for the dataset
        framework: "deepeval" or "agentevals"
        config_name: Configuration type ("agentic", "trajectory", "tool_use")
        tags: Filter by specific tags (e.g., ["Alice-Agent", "main-swarm"])
        **filters: Additional LangSmith filters (start_time, end_time, etc.)
    
    Returns:
        Dataset ID
    """
    builder = GenericDatasetBuilder()
    
    # Get configuration based on framework
    if framework == "deepeval":
        config = DEEPEVAL_CONFIGS.get(config_name)
    elif framework == "agentevals":
        config = AGENTEVALS_CONFIGS.get(config_name)
    else:
        raise ValueError(f"Unknown framework: {framework}. Use 'deepeval' or 'agentevals'")
    
    if not config:
        available_configs = list(DEEPEVAL_CONFIGS.keys()) if framework == "deepeval" else list(AGENTEVALS_CONFIGS.keys())
        raise ValueError(f"Unknown config: {config_name}. Available: {available_configs}")
    
    # Handle tags filtering
    if tags:
        # Convert tags to LangSmith filter format
        tags_filter = " OR ".join([f'has_tag("{tag}")' for tag in tags])
        
        # Combine with existing filter if present
        existing_filter = filters.get('filter', '')
        if existing_filter:
            filters['filter'] = f"({existing_filter}) AND ({tags_filter})"
        else:
            filters['filter'] = tags_filter
    
    return builder.build_dataset(project_name, dataset_name, config, **filters)

 