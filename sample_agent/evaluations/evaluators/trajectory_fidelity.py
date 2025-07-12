# sample_agent/evaluations/evaluators/trajectory_fidelity.py
from typing import Any, Dict, List, Optional, Union
from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from langsmith import Client as LangSmithClient
import json

from .base import BaseEvaluator


class TrajectoryFidelityEvaluator(BaseEvaluator):
    """
    Evaluates trajectory fidelity for agentic systems using modern evaluation approaches.

    Trajectory fidelity measures how well an agent's execution path (trajectory) aligns with
    the expected or optimal behavior patterns. This includes:
    - Step coherence and logical flow
    - Tool usage appropriateness
    - Decision making quality
    - Goal achievement effectiveness

    Production-grade implementation with:
    - Custom G-Eval criteria for trajectory assessment
    - Support for complex multi-step agent workflows
    - LangGraph-specific evaluation patterns
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
        evaluation_criteria: Optional[str] = None,
    ):
        """
        Initialize TrajectoryFidelityEvaluator.

        Args:
            threshold: Minimum score threshold for passing evaluation
            model: Model to use for evaluation (e.g., "gpt-4o", "gpt-4o-mini")
            include_reason: Whether to include reasoning in the evaluation
            strict_mode: If True, enforces binary scoring (0 or 1)
            async_mode: Enable concurrent execution for better performance
            verbose_mode: Print intermediate steps for debugging
            max_retries: Maximum number of retry attempts on failure
            custom_model: Custom model instance for evaluation
            evaluation_criteria: Custom evaluation criteria (if None, uses default)
        """
        self.threshold = threshold
        self.model = model
        self.include_reason = include_reason
        self.strict_mode = strict_mode
        self.async_mode = async_mode
        self.verbose_mode = verbose_mode
        self.max_retries = max_retries
        self.custom_model = custom_model

        # Define evaluation criteria for trajectory fidelity
        self.evaluation_criteria = evaluation_criteria or self._get_default_criteria()

        # Initialize the DeepEval G-Eval metric for trajectory assessment
        self.metric = GEval(
            name="Trajectory Fidelity",
            criteria=self.evaluation_criteria,
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.ADDITIONAL_METADATA,
            ],
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
        return "trajectory_fidelity"

    def applicable_profiles(self) -> List[str]:
        return ["agentic"]

    def evaluate(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single example for trajectory fidelity.

        Args:
            example: Example with 'id', 'inputs', 'outputs', and trajectory information

        Returns:
            Dictionary with evaluation results
        """
        try:
            # Extract and process trajectory information
            trajectory_data = self._extract_trajectory_data(example)
            if not trajectory_data:
                return {
                    "example_id": example.get("id"),
                    "metric": self.name(),
                    "score": None,
                    "comment": "No trajectory data found for evaluation",
                    "value": None,
                    "error": "missing_trajectory",
                }

            # Create formatted input for G-Eval
            formatted_input = self._format_trajectory_input(trajectory_data)
            trajectory_summary = self._generate_trajectory_summary(trajectory_data)

            # Create DeepEval test case with trajectory metadata
            test_case = LLMTestCase(
                input=formatted_input,
                actual_output=trajectory_summary,
                additional_metadata={
                    "trajectory_steps": trajectory_data.get("steps", []),
                    "tool_calls": trajectory_data.get("tool_calls", []),
                    "intermediate_steps": trajectory_data.get("intermediate_steps", []),
                    "final_output": trajectory_data.get("final_output", ""),
                    "goal": trajectory_data.get("goal", ""),
                    "node_sequence": trajectory_data.get("node_sequence", []),
                },
            )

            # Evaluate with retries
            for attempt in range(self.max_retries):
                try:
                    # Measure trajectory fidelity
                    self.metric.measure(test_case)

                    # Extract results
                    score = self.metric.score
                    reason = self.metric.reason if self.include_reason else None

                    # Analyze trajectory patterns
                    trajectory_analysis = self._analyze_trajectory_patterns(
                        trajectory_data
                    )

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
                            "passed": (
                                score >= self.threshold if score is not None else False
                            ),
                            "model": self.model,
                            "trajectory_analysis": trajectory_analysis,
                            "step_count": len(trajectory_data.get("steps", [])),
                            "tool_usage_count": len(
                                trajectory_data.get("tool_calls", [])
                            ),
                        },
                        "metadata": {
                            "evaluation_method": "g_eval_trajectory_fidelity",
                            "version": "1.0.0",
                            "strict_mode": self.strict_mode,
                            "async_mode": self.async_mode,
                            "framework": "deepeval_3.2.6",
                        },
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
                "comment": f"Error during trajectory fidelity evaluation: {str(e)}",
                "value": None,
                "error": str(e),
            }

    def evaluate_dataset(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate multiple examples for trajectory fidelity.

        Args:
            examples: List of examples to evaluate

        Returns:
            List of evaluation results
        """
        results = []

        if self.async_mode:
            # Process examples in batches for better performance
            test_cases = []
            valid_examples = []

            for example in examples:
                try:
                    trajectory_data = self._extract_trajectory_data(example)
                    if trajectory_data:
                        formatted_input = self._format_trajectory_input(trajectory_data)
                        trajectory_summary = self._generate_trajectory_summary(
                            trajectory_data
                        )

                        test_case = LLMTestCase(
                            input=formatted_input,
                            actual_output=trajectory_summary,
                            additional_metadata={
                                "trajectory_steps": trajectory_data.get("steps", []),
                                "tool_calls": trajectory_data.get("tool_calls", []),
                                "intermediate_steps": trajectory_data.get(
                                    "intermediate_steps", []
                                ),
                                "final_output": trajectory_data.get("final_output", ""),
                                "goal": trajectory_data.get("goal", ""),
                            },
                        )
                        test_cases.append(test_case)
                        valid_examples.append(example)
                    else:
                        results.append(
                            {
                                "example_id": example.get("id"),
                                "metric": self.name(),
                                "score": None,
                                "comment": "No trajectory data found",
                                "value": None,
                                "error": "missing_trajectory",
                            }
                        )
                except Exception as e:
                    results.append(
                        {
                            "example_id": example.get("id"),
                            "metric": self.name(),
                            "score": None,
                            "comment": f"Error preparing test case: {str(e)}",
                            "value": None,
                            "error": str(e),
                        }
                    )

            # Bulk evaluate valid test cases
            if test_cases:
                try:
                    evaluate(test_cases=test_cases, metrics=[self.metric])

                    # Extract results
                    for i, (test_case, example) in enumerate(
                        zip(test_cases, valid_examples)
                    ):
                        score = self.metric.score
                        reason = self.metric.reason if self.include_reason else None

                        results.append(
                            {
                                "example_id": example.get("id"),
                                "metric": self.name(),
                                "score": score,
                                "comment": reason,
                                "value": {
                                    "score": score,
                                    "threshold": self.threshold,
                                    "passed": (
                                        score >= self.threshold
                                        if score is not None
                                        else False
                                    ),
                                    "model": self.model,
                                },
                                "metadata": {
                                    "evaluation_method": "g_eval_trajectory_fidelity_bulk",
                                    "version": "1.0.0",
                                    "batch_size": len(test_cases),
                                },
                            }
                        )

                except Exception as e:
                    # Fall back to individual evaluation
                    for example in valid_examples:
                        results.append(self.evaluate(example))
        else:
            # Sequential evaluation
            for example in examples:
                results.append(self.evaluate(example))

        return results

    def _get_default_criteria(self) -> str:
        """Get default evaluation criteria for trajectory fidelity."""
        return """
        Evaluate the trajectory fidelity of this agent execution based on the following criteria:
        
        1. **Step Coherence (25%)**: Do the execution steps follow a logical sequence that makes sense for achieving the goal?
        
        2. **Tool Usage Appropriateness (25%)**: Are the tools used relevant and appropriate for each step? Are they used efficiently?
        
        3. **Decision Making Quality (25%)**: Do the decisions made at each step demonstrate good reasoning and progress toward the goal?
        
        4. **Goal Achievement Effectiveness (25%)**: Does the trajectory lead to successful goal completion or make meaningful progress?
        
        Consider:
        - Logical flow between steps
        - Appropriate tool selection and usage
        - Error handling and recovery
        - Efficiency and directness of the path
        - Final outcome quality
        
        Score from 0 to 1, where 1 represents perfect trajectory fidelity.
        """

    def _extract_trajectory_data(
        self, example: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract trajectory data from the example."""
        # Try multiple possible locations for trajectory data
        trajectory_sources = [
            example.get("outputs", {}),
            example.get("trajectory"),
            example.get("execution_data"),
            example,
        ]

        trajectory_data = {}

        for source in trajectory_sources:
            if isinstance(source, dict):
                # Extract various trajectory components
                if "intermediate_steps" in source:
                    trajectory_data["intermediate_steps"] = source["intermediate_steps"]
                if "tool_calls" in source:
                    trajectory_data["tool_calls"] = source["tool_calls"]
                if "steps" in source:
                    trajectory_data["steps"] = source["steps"]
                if "final_output" in source:
                    trajectory_data["final_output"] = source["final_output"]
                if "messages" in source:
                    trajectory_data["messages"] = source["messages"]
                if "node_sequence" in source:
                    trajectory_data["node_sequence"] = source["node_sequence"]

        # Extract goal from inputs
        inputs = example.get("inputs", {})
        if isinstance(inputs, dict):
            trajectory_data["goal"] = (
                inputs.get("input", "") or inputs.get("query", "") or str(inputs)
            )
        else:
            trajectory_data["goal"] = str(inputs)

        # Return None if no meaningful trajectory data found
        if not any(
            [
                trajectory_data.get("intermediate_steps"),
                trajectory_data.get("tool_calls"),
                trajectory_data.get("steps"),
                trajectory_data.get("messages"),
            ]
        ):
            return None

        return trajectory_data

    def _format_trajectory_input(self, trajectory_data: Dict[str, Any]) -> str:
        """Format trajectory data into a readable input for evaluation."""
        goal = trajectory_data.get("goal", "")

        input_parts = [f"Goal: {goal}"]

        # Add trajectory steps if available
        if trajectory_data.get("steps"):
            input_parts.append("Execution Steps:")
            for i, step in enumerate(trajectory_data["steps"]):
                input_parts.append(f"  {i+1}. {step}")

        # Add tool calls if available
        if trajectory_data.get("tool_calls"):
            input_parts.append("Tool Calls:")
            for i, tool_call in enumerate(trajectory_data["tool_calls"]):
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get("name", "unknown")
                    tool_args = tool_call.get("args", {})
                    input_parts.append(f"  {i+1}. {tool_name}({tool_args})")
                else:
                    input_parts.append(f"  {i+1}. {tool_call}")

        # Add intermediate steps if available
        if trajectory_data.get("intermediate_steps"):
            input_parts.append("Intermediate Steps:")
            for i, step in enumerate(trajectory_data["intermediate_steps"]):
                input_parts.append(f"  {i+1}. {step}")

        return "\n".join(input_parts)

    def _generate_trajectory_summary(self, trajectory_data: Dict[str, Any]) -> str:
        """Generate a summary of the trajectory for evaluation."""
        parts = []

        # Summarize execution
        step_count = len(trajectory_data.get("steps", []))
        tool_count = len(trajectory_data.get("tool_calls", []))

        parts.append(
            f"Trajectory executed {step_count} steps with {tool_count} tool calls."
        )

        # Add final output
        final_output = trajectory_data.get("final_output", "")
        if final_output:
            parts.append(f"Final output: {final_output}")

        # Add node sequence if available (LangGraph specific)
        node_sequence = trajectory_data.get("node_sequence", [])
        if node_sequence:
            parts.append(f"Node sequence: {' -> '.join(node_sequence)}")

        return " ".join(parts)

    def _analyze_trajectory_patterns(
        self, trajectory_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze patterns in the trajectory for additional insights."""
        analysis = {
            "step_count": len(trajectory_data.get("steps", [])),
            "tool_usage_count": len(trajectory_data.get("tool_calls", [])),
            "has_error_handling": False,
            "tool_diversity": 0,
            "execution_efficiency": "unknown",
        }

        # Analyze tool diversity
        tool_calls = trajectory_data.get("tool_calls", [])
        if tool_calls:
            unique_tools = set()
            for tool_call in tool_calls:
                if isinstance(tool_call, dict):
                    unique_tools.add(tool_call.get("name", "unknown"))
                else:
                    unique_tools.add(str(tool_call))
            analysis["tool_diversity"] = len(unique_tools)

        # Check for error handling patterns
        steps = trajectory_data.get("steps", [])
        intermediate_steps = trajectory_data.get("intermediate_steps", [])
        all_steps = steps + intermediate_steps

        error_keywords = ["error", "exception", "retry", "fallback", "recovery"]
        analysis["has_error_handling"] = any(
            any(keyword in str(step).lower() for keyword in error_keywords)
            for step in all_steps
        )

        # Simple efficiency heuristic
        if analysis["step_count"] > 0:
            if analysis["step_count"] <= 3:
                analysis["execution_efficiency"] = "high"
            elif analysis["step_count"] <= 6:
                analysis["execution_efficiency"] = "medium"
            else:
                analysis["execution_efficiency"] = "low"

        return analysis

    def _log_to_langsmith(
        self, example: Dict[str, Any], score: float, reason: Optional[str]
    ):
        """Log evaluation results to LangSmith."""
        try:
            if hasattr(self.langsmith_client, "create_feedback"):
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
                        "version": "1.0.0",
                        "framework": "deepeval_3.2.6",
                    },
                )
        except Exception as e:
            # Silently fail if LangSmith logging fails
            if self.verbose_mode:
                print(f"Failed to log to LangSmith: {e}")
            pass
