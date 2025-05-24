import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from ..agents.critic import CriticAgent
from ..agents.executor import ExecutorAgent
from ..agents.planner import PlannerAgent
from ..api.client import ClaudeAPIClient

logger = logging.getLogger(__name__)


class OrchestrationPipeline:
    """
    Orchestrates the multi-agent workflow by coordinating Planner, Executor, and Critic agents.
    Manages the flow of information between agents and implements the full reasoning pipeline.
    """

    def __init__(
        self,
        api_client: ClaudeAPIClient,
        planner: Optional[PlannerAgent] = None,
        executor: Optional[ExecutorAgent] = None,
        critic: Optional[CriticAgent] = None,
        max_iterations: int = 3,
        feedback_threshold: float = 7.0,
        parallel_execution: bool = True,
    ):
        """
        Initialize the orchestration pipeline.

        Args:
            api_client: Claude API client instance
            planner: Optional custom planner agent (if None, a default one is created)
            executor: Optional custom executor agent (if None, a default one is created)
            critic: Optional custom critic agent (if None, a default one is created)
            max_iterations: Maximum number of planning-execution-critique iterations
            feedback_threshold: Quality threshold (0-10) for critic feedback to trigger refinement
            parallel_execution: Whether to execute independent steps in parallel
        """
        self.api_client = api_client
        self.planner = planner or PlannerAgent(api_client)
        self.executor = executor or ExecutorAgent(api_client)
        self.critic = critic or CriticAgent(api_client)

        self.max_iterations = max_iterations
        self.feedback_threshold = feedback_threshold
        self.parallel_execution = parallel_execution

        self.id = str(uuid.uuid4())
        self.state = {
            "task": {},
            "plan": {},
            "execution_results": {},
            "feedback": {},
            "iterations": 0,
            "status": "initialized",
        }

    def execute(
        self, task_description: str, task_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the full orchestration pipeline on a task.

        Args:
            task_description: Description of the task to execute
            task_context: Optional additional context for the task

        Returns:
            Results of the orchestration process
        """
        self.state["task"] = {
            "description": task_description,
            "context": task_context or {},
            "id": str(uuid.uuid4()),
        }
        self.state["status"] = "in_progress"

        try:
            # Phase 1: Planning
            logger.info(f"Starting planning phase for task: {task_description[:50]}...")
            self.state["plan"] = self.planner.process(task_description)

            # Main orchestration loop
            for iteration in range(self.max_iterations):
                self.state["iterations"] = iteration + 1
                logger.info(f"Starting iteration {iteration + 1}/{self.max_iterations}")

                # Phase 2: Execution
                execution_results = self._execute_plan(self.state["plan"])
                self.state["execution_results"][
                    f"iteration_{iteration + 1}"
                ] = execution_results

                # Phase 3: Critique
                feedback = self._evaluate_results(execution_results, self.state["plan"])
                self.state["feedback"][f"iteration_{iteration + 1}"] = feedback

                # Check if quality is satisfactory
                quality_score = feedback.get("quality_score", 0)
                meets_requirements = feedback.get("meets_requirements", False)

                if quality_score >= self.feedback_threshold and meets_requirements:
                    logger.info(
                        f"Quality threshold met ({quality_score} >= {self.feedback_threshold}). Completing task."
                    )
                    self.state["status"] = "completed"
                    break

                # If this is the last iteration, we're done even if quality isn't met
                if iteration == self.max_iterations - 1:
                    logger.warning(
                        f"Max iterations reached without meeting quality threshold."
                    )
                    self.state["status"] = "max_iterations_reached"
                    break

                # Otherwise, refine the plan and continue
                logger.info(
                    f"Quality threshold not met ({quality_score} < {self.feedback_threshold}). Refining plan."
                )
                feedback_str = feedback.get("overall_feedback", "")
                self.state["plan"] = self.planner.refine_plan(
                    self.state["plan"], feedback_str
                )

            return {
                "task_id": self.state["task"]["id"],
                "status": self.state["status"],
                "iterations": self.state["iterations"],
                "final_plan": self.state["plan"],
                "final_results": self.state["execution_results"].get(
                    f"iteration_{self.state['iterations']}", {}
                ),
                "final_feedback": self.state["feedback"].get(
                    f"iteration_{self.state['iterations']}", {}
                ),
            }

        except Exception as e:
            logger.error(f"Error in orchestration pipeline: {str(e)}")
            self.state["status"] = "error"
            self.state["error"] = str(e)
            return {
                "task_id": self.state["task"]["id"],
                "status": "error",
                "error": str(e),
            }

    def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all steps in a plan.

        Args:
            plan: Plan with steps to execute

        Returns:
            Execution results for all steps
        """
        steps = plan.get("steps", [])
        results = {
            "step_results": {},
            "summary": {},
            "start_time": time.time(),
            "end_time": None,
        }

        # Track context that gets passed between dependent steps
        execution_context = {
            "objective": plan.get("objective", ""),
            "previous_results": {},
        }

        # Build dependency graph
        dependencies = {}
        for step in steps:
            step_id = step.get("id", "")
            if step_id:
                dependencies[step_id] = step.get("dependencies", [])

        # Track completed steps

        # Execute steps respecting dependencies
        if self.parallel_execution:
            results["step_results"] = self._execute_steps_parallel(
                steps, dependencies, execution_context
            )
        else:
            results["step_results"] = self._execute_steps_sequential(
                steps, dependencies, execution_context
            )

        # Summarize results
        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]
        results["total_steps"] = len(steps)
        results["completed_steps"] = len(results["step_results"])

        # Generate summary using executor
        summary_task = {
            "id": "summary",
            "description": f"Summarize the results of executing the following objective: {plan.get('objective', '')}",
            "context": {"plan": plan, "results": results["step_results"]},
        }

        summary_result = self.executor.process(summary_task)
        results["summary"] = summary_result.get("completion", "")

        return results

    def _execute_steps_sequential(
        self,
        steps: List[Dict[str, Any]],
        dependencies: Dict[str, List[str]],
        execution_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute steps sequentially, respecting dependencies.

        Args:
            steps: List of steps to execute
            dependencies: Map of step IDs to their dependency step IDs
            execution_context: Context with previous results

        Returns:
            Map of step IDs to execution results
        """
        results = {}
        completed_steps = set()

        while len(completed_steps) < len(steps):
            for step in steps:
                step_id = step.get("id", "")

                # Skip if already completed
                if step_id in completed_steps:
                    continue

                # Check dependencies
                deps = dependencies.get(step_id, [])
                if not all(dep in completed_steps for dep in deps):
                    logger.debug(
                        f"Skipping step {step_id} as dependencies are not yet completed"
                    )
                    continue

                # Execute step
                logger.info(
                    f"Executing step: {step_id} - {step.get('description', '')[:50]}..."
                )
                result = self.executor.process_step(step, execution_context)
                results[step_id] = result

                # Update context with this step's results
                execution_context["previous_results"][step_id] = result

                # Mark as completed
                completed_steps.add(step_id)

            # If no steps were executed in this iteration, we might have a dependency cycle
            if len(completed_steps) < len(steps) and len(results) == len(
                completed_steps
            ):
                logger.warning(
                    "Possible dependency cycle detected or some steps have invalid dependencies"
                )
                break

        return results

    def _execute_steps_parallel(
        self,
        steps: List[Dict[str, Any]],
        dependencies: Dict[str, List[str]],
        execution_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute steps in parallel where possible, respecting dependencies.

        Args:
            steps: List of steps to execute
            dependencies: Map of step IDs to their dependency step IDs
            execution_context: Context with previous results

        Returns:
            Map of step IDs to execution results
        """
        results = {}
        completed_steps = set()

        while len(completed_steps) < len(steps):
            # Find steps that can be executed in parallel
            executable_steps = []

            for step in steps:
                step_id = step.get("id", "")

                # Skip if already completed
                if step_id in completed_steps:
                    continue

                # Check dependencies
                deps = dependencies.get(step_id, [])
                if all(dep in completed_steps for dep in deps):
                    executable_steps.append(step)

            # If no steps can be executed, we might have a dependency cycle
            if not executable_steps:
                logger.warning(
                    "Possible dependency cycle detected or some steps have invalid dependencies"
                )
                break

            # Execute eligible steps in parallel
            with ThreadPoolExecutor(
                max_workers=min(len(executable_steps), 5)
            ) as executor:
                # Submit all eligible steps
                future_to_step = {
                    executor.submit(
                        self.executor.process_step,
                        step,
                        execution_context.copy(),  # Copy to avoid race conditions
                    ): step
                    for step in executable_steps
                }

                # Process results as they complete
                for future in as_completed(future_to_step):
                    step = future_to_step[future]
                    step_id = step.get("id", "")

                    try:
                        result = future.result()
                        results[step_id] = result

                        # Mark as completed
                        completed_steps.add(step_id)

                        # Update context for subsequent steps
                        execution_context["previous_results"][step_id] = result

                        logger.info(f"Completed step: {step_id}")
                    except Exception as e:
                        logger.error(f"Error executing step {step_id}: {str(e)}")
                        # Add a failed result to prevent infinite loop
                        results[step_id] = {"error": str(e), "status": "failed"}
                        completed_steps.add(step_id)

        return results

    def _evaluate_results(
        self, execution_results: Dict[str, Any], plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate the execution results against the plan.

        Args:
            execution_results: Results from executing the plan
            plan: The original plan

        Returns:
            Evaluation feedback
        """
        # Prepare data for evaluation
        evaluation_data = {
            "plan": plan,
            "results": execution_results,
            "objective": plan.get("objective", ""),
            "summary": execution_results.get("summary", ""),
        }

        # Define requirements for evaluation
        requirements = {
            "objective": plan.get("objective", ""),
            "expected_outcomes": [
                step.get("expected_outcome", "") for step in plan.get("steps", [])
            ],
            "completeness": "All steps in the plan must be executed",
            "quality": "Results must achieve the stated objective effectively",
        }

        # Get evaluation from critic
        feedback = self.critic.process(evaluation_data, requirements)

        return feedback
