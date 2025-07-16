# sample_agent/evaluations/evaluators/tool_usage_relevance.py
from typing import Any, Dict, List, Optional, Union
from deepeval import evaluate
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase
from langsmith import Client as LangSmithClient
import json

from .base import BaseEvaluator


class ToolUsageRelevanceEvaluator(BaseEvaluator):
    """
    Evaluates tool usage relevance for agentic systems using DeepEval 3.2.6.
    
    Tool usage relevance measures how appropriately an agent selects and uses tools
    to accomplish its goals. This includes:
    - Tool selection appropriateness for the given context
    - Correct usage of tool parameters
    - Effectiveness of tool calls in achieving objectives
    - Efficiency of tool usage patterns
    
    Production-grade implementation with:
    - DeepEval ToolCorrectnessMetric integration
    - Support for complex multi-tool workflows
    - LangGraph-specific tool evaluation
    - Comprehensive error handling
    - LangSmith integration
    """
    
    def __init__(
        self,
        threshold: float = 0.7,
        model: str = "gpt-4o",
        include_reason: bool = True,
        strict_mode: bool = False,
        async_mode: bool = True,
        verbose_mode: bool = False,
        max_retries: int = 3,
        custom_model: Optional[Any] = None,
    ):
        """
        Initialize ToolUsageRelevanceEvaluator.
        
        Args:
            threshold: Minimum score threshold for passing evaluation
            model: Model to use for evaluation (e.g., "gpt-4o", "gpt-4o-mini")
            include_reason: Whether to include reasoning in the evaluation
            strict_mode: If True, enforces binary scoring (0 or 1)
            async_mode: Enable concurrent execution for better performance
            verbose_mode: Print intermediate steps for debugging
            max_retries: Maximum number of retry attempts on failure
            custom_model: Custom model instance for evaluation
        """
        self.threshold = threshold
        self.model = model
        self.include_reason = include_reason
        self.strict_mode = strict_mode
        self.async_mode = async_mode
        self.verbose_mode = verbose_mode
        self.max_retries = max_retries
        self.custom_model = custom_model
        
        # Initialize the DeepEval metric for tool usage evaluation
        self.metric = ToolCorrectnessMetric(
            threshold=threshold,
            model=custom_model or model,
            include_reason=include_reason,
            strict_mode=strict_mode,
            async_mode=async_mode,
            verbose_mode=verbose_mode,
        )
        
        # Initialize LangSmith client for logging
        self.langsmith_client = LangSmithClient()
    
    def name(self) -> str:
        return "tool_usage_relevance"
    
    def applicable_profiles(self) -> List[str]:
        return ["agentic", "rag"]
    
    def evaluate(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single example for tool usage relevance.
        
        Args:
            example: Example with 'id', 'inputs', 'outputs', and tool usage information
        
        Returns:
            Dictionary with evaluation results
        """
        try:
            # Extract tool usage data
            tool_usage_data = self._extract_tool_usage_data(example)
            if not tool_usage_data:
                return {
                    "example_id": example.get("id"),
                    "metric": self.name(),
                    "score": None,
                    "comment": "No tool usage data found for evaluation",
                    "value": None,
                    "error": "missing_tool_usage"
                }
            
            # Format tool usage for evaluation
            input_text = self._format_tool_usage_input(tool_usage_data)
            actual_output = self._generate_tool_usage_summary(tool_usage_data)
            
            # Create DeepEval test case
            test_case = LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                tools_called=tool_usage_data.get("tool_calls", [])
            )
            
            # Evaluate with retries
            for attempt in range(self.max_retries):
                try:
                    # Measure tool usage relevance
                    self.metric.measure(test_case)
                    
                    # Extract results
                    score = self.metric.score
                    reason = self.metric.reason if self.include_reason else None
                    
                    # Analyze tool usage patterns
                    tool_analysis = self._analyze_tool_usage_patterns(tool_usage_data)
                    
                    # Log to LangSmith if available
                    self._log_to_langsmith(example, score, reason)
                    
                    return {
                        "example_id": example.get("id"),
                        "metric": self.name(),
                        "score": score,
                        "comment": reason,
                        "value": {
                            "score": score,
                            "threshold": self.threshold,
                            "passed": score >= self.threshold if score is not None else False,
                            "model": self.model,
                            "tool_analysis": tool_analysis,
                            "tool_call_count": len(tool_usage_data.get("tool_calls", [])),
                            "unique_tools_used": len(set(
                                call.get("name", "unknown") if isinstance(call, dict) else str(call)
                                for call in tool_usage_data.get("tool_calls", [])
                            )),
                        },
                        "metadata": {
                            "evaluation_method": "deepeval_tool_correctness",
                            "version": "3.2.6",
                            "strict_mode": self.strict_mode,
                            "async_mode": self.async_mode,
                        }
                    }
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise e
                    continue
                    
        except Exception as e:
            return {
                "example_id": example.get("id"),
                "metric": self.name(),
                "score": None,
                "comment": f"Error during tool usage relevance evaluation: {str(e)}",
                "value": None,
                "error": str(e)
            }
    
    def evaluate_dataset(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate multiple examples for tool usage relevance.
        
        Args:
            examples: List of examples to evaluate
        
        Returns:
            List of evaluation results
        """
        results = []
        
        if self.async_mode:
            # Use DeepEval's bulk evaluation with async support
            test_cases = []
            valid_examples = []
            
            for example in examples:
                try:
                    tool_usage_data = self._extract_tool_usage_data(example)
                    if tool_usage_data:
                        input_text = self._format_tool_usage_input(tool_usage_data)
                        actual_output = self._generate_tool_usage_summary(tool_usage_data)
                        
                        test_case = LLMTestCase(
                            input=input_text,
                            actual_output=actual_output,
                            tools_called=tool_usage_data.get("tool_calls", [])
                        )
                        test_cases.append(test_case)
                        valid_examples.append(example)
                    else:
                        # Handle missing tool usage data
                        results.append({
                            "example_id": example.get("id"),
                            "metric": self.name(),
                            "score": None,
                            "comment": "No tool usage data found",
                            "value": None,
                            "error": "missing_tool_usage"
                        })
                except Exception as e:
                    results.append({
                        "example_id": example.get("id"),
                        "metric": self.name(),
                        "score": None,
                        "comment": f"Error preparing test case: {str(e)}",
                        "value": None,
                        "error": str(e)
                    })
            
            # Bulk evaluate valid test cases
            if test_cases:
                try:
                    evaluate(test_cases=test_cases, metrics=[self.metric])
                    
                    # Extract results
                    for i, (test_case, example) in enumerate(zip(test_cases, valid_examples)):
                        score = self.metric.score
                        reason = self.metric.reason if self.include_reason else None
                        
                        results.append({
                            "example_id": example.get("id"),
                            "metric": self.name(),
                            "score": score,
                            "comment": reason,
                            "value": {
                                "score": score,
                                "threshold": self.threshold,
                                "passed": score >= self.threshold if score is not None else False,
                                "model": self.model,
                            },
                            "metadata": {
                                "evaluation_method": "deepeval_tool_correctness_bulk",
                                "version": "3.2.6",
                                "batch_size": len(test_cases),
                            }
                        })
                        
                except Exception as e:
                    # Fall back to individual evaluation
                    for example in valid_examples:
                        results.append(self.evaluate(example))
        else:
            # Sequential evaluation
            for example in examples:
                results.append(self.evaluate(example))
        
        return results
    
    def _extract_tool_usage_data(self, example: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract tool usage data from the example."""
        # Try multiple possible locations for tool usage data
        tool_sources = [
            example.get("outputs", {}),
            example.get("tool_usage"),
            example.get("tool_calls"),
            example,
        ]
        
        tool_usage_data = {}
        
        for source in tool_sources:
            if isinstance(source, dict):
                # Extract tool calls
                if "tool_calls" in source:
                    tool_usage_data["tool_calls"] = source["tool_calls"]
                if "tools_called" in source:
                    tool_usage_data["tool_calls"] = source["tools_called"]
                # Extract intermediate steps that might contain tool usage
                if "intermediate_steps" in source:
                    intermediate_steps = source["intermediate_steps"]
                    tool_calls = []
                    for step in intermediate_steps:
                        if isinstance(step, dict):
                            if "tool" in step or "action" in step:
                                tool_calls.append(step)
                    if tool_calls:
                        tool_usage_data["tool_calls"] = tool_calls
            elif isinstance(source, list):
                # Direct list of tool calls
                tool_usage_data["tool_calls"] = source
        
        # Extract goal/context from inputs
        inputs = example.get("inputs", {})
        if isinstance(inputs, dict):
            tool_usage_data["goal"] = inputs.get("input", "") or inputs.get("query", "") or str(inputs)
        else:
            tool_usage_data["goal"] = str(inputs)
        
        # Extract final output
        outputs = example.get("outputs", {})
        if isinstance(outputs, dict):
            tool_usage_data["final_output"] = outputs.get("output", "") or outputs.get("final_output", "")
        else:
            tool_usage_data["final_output"] = str(outputs)
        
        # Return None if no tool calls found
        if not tool_usage_data.get("tool_calls"):
            return None
        
        return tool_usage_data
    
    def _format_tool_usage_input(self, tool_usage_data: Dict[str, Any]) -> str:
        """Format tool usage data into a readable input for evaluation."""
        goal = tool_usage_data.get("goal", "")
        tool_calls = tool_usage_data.get("tool_calls", [])
        
        input_parts = [f"Goal: {goal}"]
        
        if tool_calls:
            input_parts.append("Tools Used:")
            for i, tool_call in enumerate(tool_calls):
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get("name", tool_call.get("tool", "unknown"))
                    tool_args = tool_call.get("args", tool_call.get("arguments", {}))
                    tool_result = tool_call.get("result", tool_call.get("output", ""))
                    
                    tool_desc = f"  {i+1}. {tool_name}"
                    if tool_args:
                        tool_desc += f"({tool_args})"
                    if tool_result:
                        tool_desc += f" -> {tool_result}"
                    
                    input_parts.append(tool_desc)
                else:
                    input_parts.append(f"  {i+1}. {tool_call}")
        
        return "\n".join(input_parts)
    
    def _generate_tool_usage_summary(self, tool_usage_data: Dict[str, Any]) -> str:
        """Generate a summary of tool usage for evaluation."""
        tool_calls = tool_usage_data.get("tool_calls", [])
        final_output = tool_usage_data.get("final_output", "")
        
        parts = []
        
        # Summarize tool usage
        unique_tools = set()
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name", tool_call.get("tool", "unknown"))
                unique_tools.add(tool_name)
            else:
                unique_tools.add(str(tool_call))
        
        parts.append(f"Used {len(tool_calls)} tool calls across {len(unique_tools)} different tools.")
        
        if unique_tools:
            parts.append(f"Tools: {', '.join(unique_tools)}")
        
        if final_output:
            parts.append(f"Final output: {final_output}")
        
        return " ".join(parts)
    
    def _analyze_tool_usage_patterns(self, tool_usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in tool usage for additional insights."""
        tool_calls = tool_usage_data.get("tool_calls", [])
        
        analysis = {
            "total_tool_calls": len(tool_calls),
            "unique_tools": 0,
            "tool_diversity_ratio": 0.0,
            "has_successful_calls": False,
            "has_failed_calls": False,
            "most_used_tool": None,
            "tool_usage_distribution": {},
        }
        
        if not tool_calls:
            return analysis
        
        # Analyze tool usage patterns
        tool_counts = {}
        successful_calls = 0
        failed_calls = 0
        
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name", tool_call.get("tool", "unknown"))
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
                
                # Check for success indicators
                result = tool_call.get("result", tool_call.get("output", ""))
                error = tool_call.get("error", "")
                
                if error or (isinstance(result, str) and "error" in result.lower()):
                    failed_calls += 1
                else:
                    successful_calls += 1
            else:
                tool_counts["unknown"] = tool_counts.get("unknown", 0) + 1
                successful_calls += 1  # Assume success if format is unknown
        
        # Update analysis
        analysis["unique_tools"] = len(tool_counts)
        analysis["tool_diversity_ratio"] = len(tool_counts) / len(tool_calls) if tool_calls else 0
        analysis["has_successful_calls"] = successful_calls > 0
        analysis["has_failed_calls"] = failed_calls > 0
        analysis["tool_usage_distribution"] = tool_counts
        
        if tool_counts:
            analysis["most_used_tool"] = max(tool_counts.items(), key=lambda x: x[1])[0]
        
        return analysis
    
    def _log_to_langsmith(self, example: Dict[str, Any], score: float, reason: Optional[str]):
        """Log evaluation results to LangSmith."""
        try:
            if hasattr(self.langsmith_client, 'create_feedback'):
                self.langsmith_client.create_feedback(
                    run_id=example.get("run_id"),
                    key=f"{self.name()}_score",
                    score=score,
                    comment=reason,
                    source=f"{self.__class__.__name__}",
                    metadata={
                        "metric": self.name(),
                        "threshold": self.threshold,
                        "model": self.model,
                        "version": "3.2.6"
                    }
                )
        except Exception as e:
            # Silently fail if LangSmith logging fails
            if self.verbose_mode:
                print(f"Failed to log to LangSmith: {e}")
            pass