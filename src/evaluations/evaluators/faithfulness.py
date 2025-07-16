# sample_agent/evaluations/evaluators/faithfulness.py
from typing import Any, Dict, List, Optional, Union
from deepeval import evaluate
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from langsmith import Client as LangSmithClient

from .base import BaseEvaluator


class FaithfulnessEvaluator(BaseEvaluator):
    """
    Evaluates faithfulness of LLM responses using DeepEval 3.2.6.
    
    Faithfulness measures whether the actual output factually aligns with the contents 
    of the retrieval context. This is crucial for RAG and agentic systems that rely on 
    external knowledge.
    
    Production-grade implementation with:
    - Configurable thresholds and models
    - Async support
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
        truths_extraction_limit: Optional[int] = None,
        custom_model: Optional[Any] = None,
    ):
        """
        Initialize FaithfulnessEvaluator.
        
        Args:
            threshold: Minimum score threshold for passing evaluation
            model: Model to use for evaluation (e.g., "gpt-4o", "gpt-4o-mini")
            include_reason: Whether to include reasoning in the evaluation
            strict_mode: If True, enforces binary scoring (0 or 1)
            async_mode: Enable concurrent execution for better performance
            verbose_mode: Print intermediate steps for debugging
            max_retries: Maximum number of retry attempts on failure
            truths_extraction_limit: Maximum number of truths to extract from context
            custom_model: Custom model instance for evaluation
        """
        self.threshold = threshold
        self.model = model
        self.include_reason = include_reason
        self.strict_mode = strict_mode
        self.async_mode = async_mode
        self.verbose_mode = verbose_mode
        self.max_retries = max_retries
        self.truths_extraction_limit = truths_extraction_limit
        self.custom_model = custom_model
        
        # Initialize the DeepEval metric
        self.metric = FaithfulnessMetric(
            threshold=threshold,
            model=custom_model or model,
            include_reason=include_reason,
            strict_mode=strict_mode,
            async_mode=async_mode,
            verbose_mode=verbose_mode,
            truths_extraction_limit=truths_extraction_limit,
        )
        
        # Initialize LangSmith client for logging
        self.langsmith_client = LangSmithClient()
    
    def name(self) -> str:
        return "faithfulness"
    
    def applicable_profiles(self) -> List[str]:
        return ["agentic", "rag", "chat", "llm_io"]
    
    def evaluate(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single example for faithfulness.
        
        Args:
            example: Example with 'id', 'inputs', 'outputs', and 'retrieval_context'
        
        Returns:
            Dictionary with evaluation results
        """
        try:
            # Extract required fields
            input_text = self._extract_input(example)
            actual_output = self._extract_output(example)
            retrieval_context = self._extract_context(example)
            
            if not retrieval_context:
                return {
                    "example_id": example.get("id"),
                    "metric": self.name(),
                    "score": None,
                    "comment": "No retrieval context provided for faithfulness evaluation",
                    "value": None,
                    "error": "missing_context"
                }
            
            # Create DeepEval test case
            test_case = LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                retrieval_context=retrieval_context
            )
            
            # Evaluate with retries
            for attempt in range(self.max_retries):
                try:
                    # Measure faithfulness
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
                            "context_length": len(retrieval_context) if isinstance(retrieval_context, list) else 1,
                        },
                        "metadata": {
                            "evaluation_method": "deepeval_faithfulness",
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
                "comment": f"Error during faithfulness evaluation: {str(e)}",
                "value": None,
                "error": str(e)
            }
    
    def evaluate_dataset(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate multiple examples for faithfulness.
        
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
                    retrieval_context = self._extract_context(example)
                    
                    if retrieval_context:
                        test_case = LLMTestCase(
                            input=input_text,
                            actual_output=actual_output,
                            retrieval_context=retrieval_context
                        )
                        test_cases.append(test_case)
                        valid_examples.append(example)
                    else:
                        # Handle missing context
                        results.append({
                            "example_id": example.get("id"),
                            "metric": self.name(),
                            "score": None,
                            "comment": "No retrieval context provided",
                            "value": None,
                            "error": "missing_context"
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
                                "evaluation_method": "deepeval_faithfulness_bulk",
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
    
    def _extract_context(self, example: Dict[str, Any]) -> Optional[List[str]]:
        """Extract retrieval context from example."""
        # Try multiple possible locations for context
        context_sources = [
            example.get("retrieval_context"),
            example.get("context"),
            example.get("inputs", {}).get("context"),
            example.get("inputs", {}).get("retrieval_context"),
            example.get("outputs", {}).get("context"),
        ]
        
        for context in context_sources:
            if context:
                if isinstance(context, list):
                    return [str(item) for item in context]
                elif isinstance(context, str):
                    return [context]
                elif isinstance(context, dict):
                    # Try to extract from documents field
                    if "documents" in context:
                        docs = context["documents"]
                        if isinstance(docs, list):
                            return [str(doc) for doc in docs]
                        return [str(docs)]
                    return [str(context)]
        
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