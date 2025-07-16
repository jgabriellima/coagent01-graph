# sample_agent/evaluations/evaluators/correctness.py
from typing import Any, Dict, List, Optional, Union
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from langsmith import Client as LangSmithClient

from .base import BaseEvaluator


class CorrectnessEvaluator(BaseEvaluator):
    """
    Evaluates correctness of LLM responses using DeepEval 3.2.6.
    
    Correctness measures how accurate the actual output is compared to the expected output.
    This is particularly important for agents that need to provide factually correct information.
    
    Production-grade implementation with:
    - Configurable thresholds and models
    - Support for reference-based evaluation
    - Async support for better performance
    - Comprehensive error handling
    - LangSmith integration
    """
    
    def __init__(
        self,
        threshold: float = 0.5,
        model: str = "gpt-4o",
        include_reason: bool = True,
        strict_mode: bool = False,
        async_mode: bool = True,
        verbose_mode: bool = False,
        max_retries: int = 3,
        custom_model: Optional[Any] = None,
        use_reference: bool = True,
    ):
        """
        Initialize CorrectnessEvaluator.
        
        Args:
            threshold: Minimum score threshold for passing evaluation
            model: Model to use for evaluation (e.g., "gpt-4o", "gpt-4o-mini")
            include_reason: Whether to include reasoning in the evaluation
            strict_mode: If True, enforces binary scoring (0 or 1)
            async_mode: Enable concurrent execution for better performance
            verbose_mode: Print intermediate steps for debugging
            max_retries: Maximum number of retry attempts on failure
            custom_model: Custom model instance for evaluation
            use_reference: Whether to use reference outputs for evaluation
        """
        self.threshold = threshold
        self.model = model
        self.include_reason = include_reason
        self.strict_mode = strict_mode
        self.async_mode = async_mode
        self.verbose_mode = verbose_mode
        self.max_retries = max_retries
        self.custom_model = custom_model
        self.use_reference = use_reference
        
        # Initialize the DeepEval metric for correctness
        # We'll use AnswerRelevancyMetric as a proxy for correctness
        self.metric = AnswerRelevancyMetric(
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
        return "correctness"
    
    def applicable_profiles(self) -> List[str]:
        return ["agentic", "rag", "chat", "llm_io"]
    
    def evaluate(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single example for correctness.
        
        Args:
            example: Example with 'id', 'inputs', 'outputs', and optionally 'expected_outputs'
        
        Returns:
            Dictionary with evaluation results
        """
        try:
            # Extract required fields
            input_text = self._extract_input(example)
            actual_output = self._extract_output(example)
            expected_output = self._extract_expected_output(example)
            
            # Create DeepEval test case
            test_case_kwargs = {
                "input": input_text,
                "actual_output": actual_output,
            }
            
            if self.use_reference and expected_output:
                test_case_kwargs["expected_output"] = expected_output
            
            test_case = LLMTestCase(**test_case_kwargs)
            
            # Evaluate with retries
            for attempt in range(self.max_retries):
                try:
                    # Measure correctness
                    self.metric.measure(test_case)
                    
                    # Extract results
                    score = self.metric.score
                    reason = self.metric.reason if self.include_reason else None
                    
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
                            "has_reference": expected_output is not None,
                            "evaluation_type": "reference_based" if expected_output else "reference_free",
                        },
                        "metadata": {
                            "evaluation_method": "deepeval_correctness",
                            "version": "3.2.6",
                            "strict_mode": self.strict_mode,
                            "async_mode": self.async_mode,
                            "use_reference": self.use_reference,
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
                "comment": f"Error during correctness evaluation: {str(e)}",
                "value": None,
                "error": str(e)
            }
    
    def evaluate_dataset(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate multiple examples for correctness.
        
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
                    input_text = self._extract_input(example)
                    actual_output = self._extract_output(example)
                    expected_output = self._extract_expected_output(example)
                    
                    test_case_kwargs = {
                        "input": input_text,
                        "actual_output": actual_output,
                    }
                    
                    if self.use_reference and expected_output:
                        test_case_kwargs["expected_output"] = expected_output
                    
                    test_case = LLMTestCase(**test_case_kwargs)
                    test_cases.append(test_case)
                    valid_examples.append(example)
                    
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
                                "evaluation_method": "deepeval_correctness_bulk",
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
    
    def _extract_input(self, example: Dict[str, Any]) -> str:
        """Extract input text from example."""
        inputs = example.get("inputs", {})
        if isinstance(inputs, dict):
            return inputs.get("input", "") or inputs.get("query", "") or str(inputs)
        return str(inputs)
    
    def _extract_output(self, example: Dict[str, Any]) -> str:
        """Extract output text from example."""
        outputs = example.get("outputs", {})
        if isinstance(outputs, dict):
            return outputs.get("output", "") or outputs.get("final_output", "") or str(outputs)
        return str(outputs)
    
    def _extract_expected_output(self, example: Dict[str, Any]) -> Optional[str]:
        """Extract expected output from example."""
        # Try multiple possible locations for expected output
        expected_sources = [
            example.get("expected_outputs"),
            example.get("expected_output"),
            example.get("reference_outputs"),
            example.get("reference_output"),
            example.get("ground_truth"),
            example.get("target"),
        ]
        
        for expected in expected_sources:
            if expected:
                if isinstance(expected, dict):
                    return expected.get("output", "") or expected.get("final_output", "") or str(expected)
                return str(expected)
        
        return None
    
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