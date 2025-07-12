# evaluations/evaluators/run_evaluations.py

import asyncio
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from langsmith import Client as LangSmithClient
from .evaluator_registry import get_evaluators_for_profile
from .base import BaseEvaluator
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_evaluations_for_dataset(
    dataset_name: str,
    dataset_profile: str,
    project_name: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> None:
    """
    Run all evaluators associated with a dataset profile over the LangSmith dataset.
    Updates metadata with results.

    Parameters:
    - dataset_name: Nome do dataset registrado no LangSmith
    - dataset_profile: Tipo do perfil (ex: agentic, rag, llm_io, chat)
    - project_name: Nome do projeto LangSmith (opcional, útil para rastreamento)
    - tags: Tags adicionais para rastreamento do run
    """

    logger.info(
        f"🔍 Running evaluation for dataset '{dataset_name}' with profile '{dataset_profile}'"
    )

    # Connect to LangSmith
    client = LangSmithClient()

    # Load dataset entries
    dataset = client.read_dataset(name=dataset_name)
    examples = client.list_examples(dataset_id=dataset.id)
    if not examples:
        logger.warning(f"⚠️ No examples found in dataset '{dataset_name}'")
        return

    evaluators: list[BaseEvaluator] = get_evaluators_for_profile(dataset_profile)
    logger.info(
        f"✅ Loaded {len(evaluators)} evaluators for profile '{dataset_profile}'"
    )

    # Run each evaluator
    for evaluator in evaluators:
        logger.info(f"➡️ Running evaluator: {evaluator.__class__.__name__}")
        evaluation_results = evaluator.evaluate_dataset(examples)

        for result in evaluation_results:
            client.create_feedback(
                example_id=result["example_id"],
                key=result["metric"],
                score=result.get("score"),
                comment=result.get("comment"),
                value=result.get("value"),
                source=result.get("source", evaluator.__class__.__name__),
                tags=tags or [],
            )

    logger.info(
        f"🎉 Evaluation completed and metrics recorded on LangSmith for dataset: {dataset_name}"
    )


class EvaluationRunner:
    """
    Advanced evaluation runner for executing evaluators on LangSmith runs.

    This class provides a comprehensive interface for running evaluations on traces
    collected from LangSmith projects, with support for batching, async execution,
    and detailed reporting.
    """

    def __init__(
        self,
        evaluators: Dict[str, BaseEvaluator],
        langsmith_client: LangSmithClient,
        evaluation_model: str = "openai:gpt-4o",
        batch_size: int = 10,
        max_retries: int = 3,
        verbose: bool = True,
    ):
        """
        Initialize the evaluation runner.

        Args:
            evaluators: Dictionary of evaluator name to evaluator instance
            langsmith_client: LangSmith client for accessing runs and datasets
            evaluation_model: Model to use for evaluation
            batch_size: Number of runs to process in parallel
            max_retries: Maximum retries for failed evaluations
            verbose: Whether to print detailed progress information
        """
        self.evaluators = evaluators
        self.langsmith_client = langsmith_client
        self.evaluation_model = evaluation_model
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.verbose = verbose

        if self.verbose:
            logger.info(
                f"🔧 EvaluationRunner initialized with {len(evaluators)} evaluators"
            )

    async def run_evaluations(
        self,
        project_name: str,
        max_runs: Optional[int] = None,
        batch_size: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run evaluations on all runs from a LangSmith project.

        Args:
            project_name: Name of the LangSmith project
            max_runs: Maximum number of runs to evaluate (None for all)
            batch_size: Batch size for processing (overrides instance default)
            filters: Additional filters for run selection

        Returns:
            Dictionary with evaluation results and summary statistics
        """
        start_time = datetime.now()

        if self.verbose:
            print(f"🚀 Starting evaluation for project: {project_name}")

        # Get runs from project
        runs = self._get_project_runs(project_name, max_runs, filters)

        if not runs:
            return {
                "summary": {
                    "total_runs": 0,
                    "evaluators_executed": 0,
                    "success_rate": 0,
                    "total_evaluation_time": 0,
                    "project_name": project_name,
                },
                "detailed_results": [],
                "failed_evaluations": [],
            }

        if self.verbose:
            print(f"📊 Found {len(runs)} runs to evaluate")

        # Process runs in batches
        batch_size = batch_size or self.batch_size
        all_results = []
        failed_evaluations = []

        for i in range(0, len(runs), batch_size):
            batch = runs[i : i + batch_size]

            if self.verbose:
                print(
                    f"⏳ Processing batch {i//batch_size + 1}/{(len(runs) + batch_size - 1)//batch_size}"
                )

            batch_results = await self._process_batch(batch)
            all_results.extend(batch_results["results"])
            failed_evaluations.extend(batch_results["failures"])

        # Generate summary
        execution_time = (datetime.now() - start_time).total_seconds()
        summary = self._generate_summary(
            all_results, failed_evaluations, execution_time, project_name
        )

        if self.verbose:
            self._print_summary(summary)

        return {
            "summary": summary,
            "detailed_results": all_results,
            "failed_evaluations": failed_evaluations,
            "generated_at": datetime.now().isoformat(),
        }

    def _get_project_runs(
        self,
        project_name: str,
        max_runs: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """Get runs from a LangSmith project."""
        try:
            runs = list(
                self.langsmith_client.list_runs(
                    project_name=project_name, **(filters or {})
                )
            )

            if max_runs:
                runs = runs[:max_runs]

            return runs

        except Exception as e:
            if self.verbose:
                print(f"❌ Error fetching runs from project '{project_name}': {e}")
            return []

    async def _process_batch(self, runs: List[Any]) -> Dict[str, List[Any]]:
        """Process a batch of runs with all evaluators."""
        results = []
        failures = []

        # Create tasks for all run-evaluator combinations
        tasks = []
        for run in runs:
            for evaluator_name, evaluator in self.evaluators.items():
                task = self._evaluate_single_run(run, evaluator_name, evaluator)
                tasks.append(task)

        # Execute all tasks concurrently
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in batch_results:
            if isinstance(result, Exception):
                failures.append(
                    {
                        "error": str(result),
                        "type": type(result).__name__,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            elif result:
                if result.get("success", False):
                    results.append(result)
                else:
                    failures.append(result)

        return {"results": results, "failures": failures}

    async def _evaluate_single_run(
        self, run: Any, evaluator_name: str, evaluator: BaseEvaluator
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a single run with a single evaluator."""
        for attempt in range(self.max_retries):
            try:
                # Convert run to example format expected by evaluators
                example = self._run_to_example(run)

                # Run evaluation
                result = evaluator.evaluate(example)

                # Add metadata
                result.update(
                    {
                        "run_id": str(run.id),
                        "evaluator_name": evaluator_name,
                        "success": True,
                        "attempt": attempt + 1,
                        "evaluation_timestamp": datetime.now().isoformat(),
                    }
                )

                return result

            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        "run_id": str(run.id),
                        "evaluator_name": evaluator_name,
                        "success": False,
                        "error": str(e),
                        "attempts": self.max_retries,
                        "evaluation_timestamp": datetime.now().isoformat(),
                    }

                # Wait before retry
                await asyncio.sleep(0.5 * (attempt + 1))

        return None

    def _run_to_example(self, run: Any) -> Dict[str, Any]:
        """Convert a LangSmith run to the example format expected by evaluators."""
        # Extract relevant information from the run
        example = {
            "id": str(run.id),
            "inputs": getattr(run, "inputs", {}),
            "outputs": getattr(run, "outputs", {}),
            "metadata": getattr(run, "extra", {}),
        }

        # Add run-specific information
        if hasattr(run, "trace_id"):
            example["trace_id"] = str(run.trace_id)

        if hasattr(run, "start_time"):
            example["start_time"] = (
                run.start_time.isoformat() if run.start_time else None
            )

        if hasattr(run, "end_time"):
            example["end_time"] = run.end_time.isoformat() if run.end_time else None

        # Add execution information for trajectory evaluation
        if hasattr(run, "child_runs"):
            example["child_runs"] = [
                {
                    "id": str(child.id),
                    "name": getattr(child, "name", ""),
                    "inputs": getattr(child, "inputs", {}),
                    "outputs": getattr(child, "outputs", {}),
                }
                for child in (run.child_runs or [])
            ]

        return example

    def _generate_summary(
        self,
        results: List[Dict[str, Any]],
        failures: List[Dict[str, Any]],
        execution_time: float,
        project_name: str,
    ) -> Dict[str, Any]:
        """Generate summary statistics from evaluation results."""
        total_evaluations = len(results) + len(failures)
        successful_evaluations = len(results)

        # Calculate success rate
        success_rate = (
            (successful_evaluations / total_evaluations * 100)
            if total_evaluations > 0
            else 0
        )

        # Calculate average scores by evaluator
        evaluator_scores = {}
        evaluator_counts = {}

        for result in results:
            evaluator_name = result.get("evaluator_name", "unknown")
            score = result.get("score")

            if score is not None:
                if evaluator_name not in evaluator_scores:
                    evaluator_scores[evaluator_name] = []
                evaluator_scores[evaluator_name].append(score)
                evaluator_counts[evaluator_name] = (
                    evaluator_counts.get(evaluator_name, 0) + 1
                )

        # Calculate averages
        avg_scores = {}
        for evaluator_name, scores in evaluator_scores.items():
            avg_scores[evaluator_name] = sum(scores) / len(scores) if scores else 0

        # Get unique runs and evaluators
        unique_runs = len(
            set(result.get("run_id") for result in results if result.get("run_id"))
        )
        unique_evaluators = len(
            set(
                result.get("evaluator_name")
                for result in results
                if result.get("evaluator_name")
            )
        )

        return {
            "project_name": project_name,
            "total_runs": unique_runs,
            "total_evaluations": total_evaluations,
            "successful_evaluations": successful_evaluations,
            "failed_evaluations": len(failures),
            "success_rate": success_rate,
            "evaluators_executed": unique_evaluators,
            "avg_evaluation_time": execution_time,
            "avg_scores_by_evaluator": avg_scores,
            "evaluator_counts": evaluator_counts,
            "execution_timestamp": datetime.now().isoformat(),
        }

    def _print_summary(self, summary: Dict[str, Any]):
        """Print a formatted summary of the evaluation results."""
        print("\n" + "=" * 60)
        print("📊 EVALUATION SUMMARY")
        print("=" * 60)
        print(f"🎯 Project: {summary['project_name']}")
        print(f"📈 Runs Evaluated: {summary['total_runs']}")
        print(f"🔧 Evaluators Used: {summary['evaluators_executed']}")
        print(f"✅ Success Rate: {summary['success_rate']:.1f}%")
        print(f"⏱️  Total Time: {summary['avg_evaluation_time']:.2f}s")

        if summary.get("avg_scores_by_evaluator"):
            print(f"\n📊 Average Scores by Evaluator:")
            for evaluator, score in summary["avg_scores_by_evaluator"].items():
                count = summary["evaluator_counts"].get(evaluator, 0)
                print(f"   {evaluator}: {score:.3f} ({count} evaluations)")

        if summary["failed_evaluations"] > 0:
            print(f"\n⚠️  {summary['failed_evaluations']} evaluations failed")

    def save_results(self, results: Dict[str, Any], output_path: str = None) -> str:
        """
        Save evaluation results to a JSON file.

        Args:
            results: Results dictionary from run_evaluations
            output_path: Path to save results (auto-generated if None)

        Returns:
            Path to the saved file
        """
        import json
        from pathlib import Path

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = results.get("summary", {}).get("project_name", "unknown")
            output_path = f"evaluation_results_{project_name}_{timestamp}.json"

        # Ensure directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save results
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        if self.verbose:
            print(f"💾 Results saved to: {output_file}")

        return str(output_file)
