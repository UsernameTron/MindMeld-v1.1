# filepath: /packages/agents/implementations/executor.py
"""
ExecutorAgent - Standardized task execution agent
Migrated from claude_agents.agents.executor to use the unified agent protocol
"""

import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional

from ..base.protocols import AgentProtocol
from ..base.registry import AgentRegistry

logger = logging.getLogger(__name__)


class ExecutorAgent(AgentProtocol):
    """
    Agent responsible for executing specific tasks and producing concrete outputs.
    Acts as the operational component of the multi-agent system.

    Capabilities:
    - Task execution with step-by-step processing
    - Tool registration and callback management
    - Multi-step plan execution
    - Error handling and result tracking
    - Structured output generation
    """

    def __init__(
        self,
        api_client: Optional[Any] = None,
        name: str = "ExecutorAgent",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize the executor agent.

        Args:
            api_client: Claude API client instance (optional for standardized interface)
            name: Agent name
            temperature: Temperature for responses (higher for more creativity in execution)
            max_tokens: Maximum tokens in the response
            tools: Optional list of tool definitions the executor can use
        """
        self.name = name
        self.api_client = api_client
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Tool management
        self.tools = tools or []
        self.tool_callbacks: Dict[str, Callable] = {}

        # Execution state
        self.execution_history: List[Dict[str, Any]] = []

        # Auto-register with the agent registry
        registry = AgentRegistry.get_instance()
        registry.register_agent(
            self.name, lambda **kwargs: ExecutorAgent(**kwargs), self.get_capabilities()
        )
        logger.info(f"Registered {self.name} with AgentRegistry")

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and metadata."""
        return {
            "name": self.name,
            "type": "executor",
            "description": "Executes specific tasks and produces concrete outputs",
            "capabilities": [
                "task_execution",
                "step_by_step_processing",
                "tool_integration",
                "plan_execution",
                "error_handling",
                "result_tracking",
            ],
            "input_types": ["task", "step", "plan"],
            "output_types": ["execution_result", "tool_output", "step_result"],
            "tools_supported": len(self.tools),
            "registered_callbacks": len(self.tool_callbacks),
        }

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data for task execution.

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check for required fields based on input type
            if "task" in data:
                task = data["task"]
                if not isinstance(task, dict):
                    logger.error("Task must be a dictionary")
                    return False
                if "description" not in task:
                    logger.error("Task must have a description")
                    return False

            elif "step" in data:
                step = data["step"]
                if not isinstance(step, dict):
                    logger.error("Step must be a dictionary")
                    return False
                if "description" not in step:
                    logger.error("Step must have a description")
                    return False

            elif "plan" in data:
                plan = data["plan"]
                if not isinstance(plan, dict):
                    logger.error("Plan must be a dictionary")
                    return False
                if "steps" not in plan or not isinstance(plan["steps"], list):
                    logger.error("Plan must have steps as a list")
                    return False

            else:
                logger.error("Input must contain 'task', 'step', or 'plan'")
                return False

            return True

        except Exception as e:
            logger.error(f"Input validation error: {str(e)}")
            return False

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process execution request and return results.

        Args:
            data: Input data containing task, step, or plan information

        Returns:
            Execution results with outputs, tool calls, and completion status
        """
        if not self.validate_input(data):
            return {
                "status": "error",
                "error": "Invalid input data",
                "agent": self.name,
            }

        try:
            # Determine execution type and process accordingly
            if "task" in data:
                return self._execute_task(data["task"])
            elif "step" in data:
                plan_context = data.get("plan_context", {})
                return self._execute_step(data["step"], plan_context)
            elif "plan" in data:
                return self._execute_plan(data["plan"])
            else:
                return {
                    "status": "error",
                    "error": "No valid execution target found",
                    "agent": self.name,
                }

        except Exception as e:
            logger.error(f"Execution error in {self.name}: {str(e)}")
            return {"status": "error", "error": str(e), "agent": self.name}

    def register_tool(
        self, tool_definition: Dict[str, Any], callback: Callable
    ) -> None:
        """
        Register a tool that the executor can use, along with its callback.

        Args:
            tool_definition: Tool definition in Claude tool format
            callback: Function to call when tool is invoked
        """
        # Check if tool already exists
        tool_name = tool_definition.get("function", {}).get("name")
        if not tool_name:
            raise ValueError("Tool definition must include function.name")

        # Add to tools list if not already present
        if not any(t.get("function", {}).get("name") == tool_name for t in self.tools):
            self.tools.append(tool_definition)

        # Register callback
        self.tool_callbacks[tool_name] = callback

        logger.info(f"Registered tool '{tool_name}' with executor agent")

    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task.

        Args:
            task: Task definition with description and context

        Returns:
            Task execution results
        """
        task_id = task.get("id", f"task_{len(self.execution_history)}")
        task_description = task.get("description", "")
        task_context = task.get("context", {})

        # Format context as string if needed
        context_str = ""
        if task_context:
            if isinstance(task_context, str):
                context_str = task_context
            else:
                context_str = json.dumps(task_context, indent=2)

        # Prepare execution results structure
        execution_results = {
            "task_id": task_id,
            "status": "completed",
            "outputs": [],
            "tool_calls": [],
            "completion": "",
            "agent": self.name,
        }

        # If API client is available, use it for execution
        if self.api_client:
            try:
                # Prepare prompt
                prompt = f"Please execute the following task:\n\nTASK: {task_description}\n\n"
                if context_str:
                    prompt += f"CONTEXT:\n{context_str}\n\n"

                # Make API call with tools
                response = self._call_api(prompt)

                # Process response and tool calls
                execution_results = self._process_api_response(
                    response, execution_results
                )

            except Exception as e:
                logger.error(f"API execution error: {str(e)}")
                execution_results.update({"status": "error", "error": str(e)})
        else:
            # Fallback execution without API
            execution_results.update(
                {
                    "completion": f"Task '{task_description}' would be executed here",
                    "note": "API client not available - using fallback execution",
                }
            )

        # Record execution in history
        self.execution_history.append(
            {
                "type": "task",
                "input": task,
                "result": execution_results,
                "timestamp": self._get_timestamp(),
            }
        )

        return execution_results

    def _execute_step(
        self, step: Dict[str, Any], plan_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a specific step from a plan.

        Args:
            step: Step definition from a plan
            plan_context: Overall plan context and previous results

        Returns:
            Step execution results
        """
        # Format task for this specific step
        task = {
            "id": step.get("id", "unknown_step"),
            "description": step.get("description", ""),
            "context": {
                "plan_objective": plan_context.get("objective", ""),
                "expected_outcome": step.get("expected_outcome", ""),
                "previous_results": plan_context.get("previous_results", {}),
                "step_dependencies": step.get("dependencies", []),
                "plan_context": plan_context,
            },
        }

        # Execute the task
        result = self._execute_task(task)

        # Add step-specific metadata
        result.update(
            {
                "step_id": step.get("id", "unknown_step"),
                "step_description": step.get("description", ""),
                "step_type": step.get("type", "general"),
            }
        )

        return result

    def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete plan with multiple steps.

        Args:
            plan: Plan definition with steps and context

        Returns:
            Plan execution results
        """
        plan_id = plan.get("id", f"plan_{len(self.execution_history)}")
        steps = plan.get("steps", [])
        objective = plan.get("objective", "")

        plan_results = {
            "plan_id": plan_id,
            "objective": objective,
            "status": "in_progress",
            "step_results": [],
            "overall_completion": "",
            "agent": self.name,
        }

        plan_context = {
            "objective": objective,
            "previous_results": {},
            "total_steps": len(steps),
        }

        try:
            # Execute each step
            for i, step in enumerate(steps):
                step_result = self._execute_step(step, plan_context)
                plan_results["step_results"].append(step_result)

                # Update context with results for next steps
                plan_context["previous_results"][
                    step.get("id", f"step_{i}")
                ] = step_result

                # Check for step failure
                if step_result.get("status") == "error":
                    plan_results["status"] = "failed"
                    plan_results["failed_step"] = step.get("id", f"step_{i}")
                    break

            # Mark as completed if all steps succeeded
            if plan_results["status"] == "in_progress":
                plan_results["status"] = "completed"
                plan_results["overall_completion"] = (
                    f"Successfully executed {len(steps)} steps for objective: {objective}"
                )

        except Exception as e:
            logger.error(f"Plan execution error: {str(e)}")
            plan_results.update({"status": "error", "error": str(e)})

        # Record plan execution in history
        self.execution_history.append(
            {
                "type": "plan",
                "input": plan,
                "result": plan_results,
                "timestamp": self._get_timestamp(),
            }
        )

        return plan_results

    def _call_api(self, prompt: str) -> Any:
        """
        Make API call if client is available.

        Args:
            prompt: Prompt to send to API

        Returns:
            API response
        """
        if not self.api_client:
            raise ValueError("API client not available")

        # This would be implemented based on the specific API client interface
        # For now, we'll use a placeholder
        return {"content": [{"text": f"Executed: {prompt}"}]}

    def _process_api_response(
        self, response: Any, execution_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process API response and extract tool calls and completion.

        Args:
            response: API response
            execution_results: Current execution results to update

        Returns:
            Updated execution results
        """
        # Extract completion text
        if hasattr(response, "content") and response.content:
            completion_parts = []
            for block in response.content:
                if hasattr(block, "type") and block.type == "text":
                    completion_parts.append(block.text)
                elif isinstance(block, dict) and block.get("type") == "text":
                    completion_parts.append(block.get("text", ""))

            execution_results["completion"] = "".join(completion_parts)

        # Process tool calls if present
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                # Handle different possible structures
                tool_name, tool_args = self._extract_tool_call_data(tool_call)

                if tool_name:
                    # Record the tool call
                    execution_results["tool_calls"].append(
                        {"tool": tool_name, "arguments": tool_args}
                    )

                    # Execute callback if registered
                    if tool_name in self.tool_callbacks:
                        try:
                            result = self.tool_callbacks[tool_name](tool_args)
                            execution_results["outputs"].append(
                                {"tool": tool_name, "result": result}
                            )
                        except Exception as e:
                            logger.error(
                                f"Error executing tool '{tool_name}': {str(e)}"
                            )
                            execution_results["outputs"].append(
                                {"tool": tool_name, "error": str(e)}
                            )

        return execution_results

    def _extract_tool_call_data(self, tool_call: Any) -> tuple[Optional[str], Any]:
        """
        Extract tool name and arguments from tool call.

        Args:
            tool_call: Tool call object or dict

        Returns:
            Tuple of (tool_name, tool_args)
        """
        tool_name = None
        tool_args = None

        try:
            if hasattr(tool_call, "function"):
                tool_name = (
                    tool_call.function.name
                    if hasattr(tool_call.function, "name")
                    else tool_call.function.get("name")
                )
                tool_args_raw = (
                    tool_call.function.arguments
                    if hasattr(tool_call.function, "arguments")
                    else tool_call.function.get("arguments")
                )
            elif isinstance(tool_call, dict) and "function" in tool_call:
                tool_name = tool_call["function"].get("name")
                tool_args_raw = tool_call["function"].get("arguments")
            else:
                logger.warning(f"Unexpected tool_call structure: {tool_call}")
                return None, None

            # Parse arguments
            try:
                tool_args = (
                    json.loads(tool_args_raw)
                    if isinstance(tool_args_raw, str)
                    else tool_args_raw
                )
            except json.JSONDecodeError:
                tool_args = tool_args_raw

        except Exception as e:
            logger.error(f"Error extracting tool call data: {str(e)}")

        return tool_name, tool_args

    def _get_timestamp(self) -> str:
        """Get current timestamp for history tracking."""
        import datetime

        return datetime.datetime.now().isoformat()

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get execution history for debugging and analysis.

        Returns:
            List of execution records
        """
        return self.execution_history.copy()

    def clear_execution_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
        logger.info(f"Cleared execution history for {self.name}")

    def some_method_that_might_fail(self, path: str):
        """Legacy method from original implementation."""
        if not os.path.exists(path):
            formatted_path = path.replace("\n", "\\n")
            raise RuntimeError(f"Invalid path: {formatted_path}")
