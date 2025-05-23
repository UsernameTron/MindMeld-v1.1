import logging
from typing import Any, Dict

from ..core.registry import REGISTRY as AGENT_REGISTRY
from ..core.registry import register_agent
from .base import Agent

logger = logging.getLogger(__name__)


@register_agent("orchestrator")
class OrchestratorAgent(Agent):
    """
    Agent for orchestrating multiple agents to work together on complex tasks.

    The OrchestratorAgent coordinates workflows involving multiple specialized
    agents, manages data flow between them, and aggregates results.
    """

    def __init__(self, **kwargs):
        """Initialize the orchestrator agent."""
        super().__init__(**kwargs)
        self.workflows = {}
        self.registered_agents = {}

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request by orchestrating multiple agents.

        Args:
            input_data: Dictionary containing:
                - 'workflow': Name of the workflow to execute
                - 'input': Input data for the workflow
                - 'options': Optional configuration for the workflow

        Returns:
            Dictionary containing results from the workflow execution
        """
        # Store input in history
        self.add_to_history({"type": "input", "content": input_data})

        workflow_name = input_data.get("workflow")
        workflow_input = input_data.get("input", {})
        options = input_data.get("options", {})

        if not workflow_name:
            result = {"error": "No workflow specified"}
            self.add_to_history({"type": "output", "content": result})
            return result

        if workflow_name not in self.workflows:
            result = {"error": f"Workflow '{workflow_name}' not found"}
            self.add_to_history({"type": "output", "content": result})
            return result

        # Execute the workflow
        try:
            workflow = self.workflows[workflow_name]
            result = self._execute_workflow(workflow, workflow_input, options)
        except Exception as e:
            logger.exception(f"Error executing workflow '{workflow_name}'")
            result = {
                "error": f"Workflow execution failed: {str(e)}",
                "workflow": workflow_name,
            }

        # Store result in history
        self.add_to_history({"type": "output", "content": result})

        return result

    def register_agent_instance(self, name: str, agent: Agent) -> None:
        """
        Register an agent instance for use in workflows.

        Args:
            name: Name to register the agent under
            agent: Agent instance to register
        """
        self.registered_agents[name] = agent
        logger.info(f"Registered agent instance '{name}'")

    def register_workflow(self, name: str, workflow_def: Dict[str, Any]) -> None:
        """
        Register a workflow definition.

        Args:
            name: Name of the workflow
            workflow_def: Workflow definition dictionary
        """
        self.workflows[name] = workflow_def
        logger.info(f"Registered workflow '{name}'")

    def _execute_workflow(
        self,
        workflow: Dict[str, Any],
        input_data: Dict[str, Any],
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a workflow with the given input data.

        Args:
            workflow: Workflow definition
            input_data: Input data for the workflow
            options: Configuration options

        Returns:
            Results from the workflow execution
        """
        # Initialize workflow state
        state = {
            "input": input_data,
            "results": {},
            "options": options,
            "current_step": 0,
            "completed_steps": [],
            "errors": [],
        }

        # Execute each step in the workflow
        steps = workflow.get("steps", [])

        for i, step in enumerate(steps):
            state["current_step"] = i

            try:
                step_result = self._execute_step(step, state)
                state["results"][step["id"]] = step_result
                state["completed_steps"].append(step["id"])
            except Exception as e:
                logger.exception(
                    f"Error executing step {i} ({step.get('id', 'unknown')})"
                )
                state["errors"].append(
                    {"step": i, "step_id": step.get("id"), "error": str(e)}
                )

                # Check if we should continue on error
                if not options.get("continue_on_error", False):
                    break

        # Prepare the final result
        result = {
            "workflow_completed": len(state["errors"]) == 0,
            "completed_steps": state["completed_steps"],
            "results": state["results"],
        }

        if state["errors"]:
            result["errors"] = state["errors"]

        return result

    def _execute_step(
        self, step: Dict[str, Any], state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single step in a workflow.

        Args:
            step: Step definition
            state: Current workflow state

        Returns:
            Result from executing the step
        """
        step_type = step.get("type")
        step_id = step.get("id")

        if not step_type:
            raise ValueError(f"Step {step_id} has no type specified")

        # Agent step
        if step_type == "agent":
            return self._execute_agent_step(step, state)

        # Conditional step
        elif step_type == "condition":
            return self._execute_condition_step(step, state)

        # Transformation step
        elif step_type == "transform":
            return self._execute_transform_step(step, state)

        # Unsupported step type
        else:
            raise ValueError(f"Unsupported step type: {step_type}")

    def _execute_agent_step(
        self, step: Dict[str, Any], state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an agent step in a workflow.

        Args:
            step: Step definition
            state: Current workflow state

        Returns:
            Result from the agent
        """
        agent_name = step.get("agent")
        if not agent_name:
            raise ValueError(f"Agent step {step.get('id')} has no agent specified")

        # Get the agent instance
        agent = self._get_agent_instance(agent_name)

        # Prepare input for the agent
        agent_input = self._prepare_agent_input(step, state)

        # Process with the agent
        return agent.process(agent_input)

    def _execute_condition_step(
        self, step: Dict[str, Any], state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a conditional step in a workflow.

        Args:
            step: Step definition
            state: Current workflow state

        Returns:
            Result of the condition evaluation
        """
        condition = step.get("condition")
        if not condition:
            raise ValueError(
                f"Condition step {step.get('id')} has no condition specified"
            )

        # Evaluate the condition
        condition_result = self._evaluate_condition(condition, state)

        # Execute the appropriate branch
        if condition_result:
            if "then" in step:
                return self._execute_step(step["then"], state)
        else:
            if "else" in step:
                return self._execute_step(step["else"], state)

        return {"condition_result": condition_result}

    def _execute_transform_step(
        self, step: Dict[str, Any], state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a transformation step in a workflow.

        Args:
            step: Step definition
            state: Current workflow state

        Returns:
            Transformed data
        """
        transform_type = step.get("transform_type")
        if not transform_type:
            raise ValueError(
                f"Transform step {step.get('id')} has no transform_type specified"
            )

        # Get input data for the transformation
        input_path = step.get("input", "")

        # Handle both string and list inputs
        if isinstance(input_path, str):
            transform_input = self._get_data_from_path(state, input_path)
        elif isinstance(input_path, list):
            # If input is a list of paths, collect all the data
            transform_input = []
            for path in input_path:
                data = self._get_data_from_path(state, path)
                if data is not None:
                    transform_input.append(data)
        else:
            transform_input = None

        # Execute the transformation
        if transform_type == "merge":
            return self._transform_merge(transform_input, step.get("options", {}))
        elif transform_type == "filter":
            return self._transform_filter(transform_input, step.get("options", {}))
        elif transform_type == "map":
            return self._transform_map(transform_input, step.get("options", {}))
        else:
            raise ValueError(f"Unsupported transform type: {transform_type}")

    def _get_agent_instance(self, agent_name: str) -> Agent:
        """
        Get an agent instance by name.

        Args:
            agent_name: Name of the agent

        Returns:
            Agent instance
        """
        # Check if we have a registered instance
        if agent_name in self.registered_agents:
            return self.registered_agents[agent_name]

        # Try to create from registry
        if agent_name in AGENT_REGISTRY:
            agent_class = AGENT_REGISTRY[agent_name]
            agent = agent_class()
            self.registered_agents[agent_name] = agent
            return agent

        raise ValueError(
            f"Agent '{agent_name}' not found in registry or registered instances"
        )

    def _prepare_agent_input(
        self, step: Dict[str, Any], state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare input data for an agent.

        Args:
            step: Step definition
            state: Current workflow state

        Returns:
            Input data for the agent
        """
        # Start with any static input defined in the step
        agent_input = step.get("input", {}).copy()

        # Process dynamic inputs
        if "dynamic_input" in step:
            for key, path in step["dynamic_input"].items():
                value = self._get_data_from_path(state, path)
                agent_input[key] = value

        return agent_input

    def _evaluate_condition(
        self, condition: Dict[str, Any], state: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition against the workflow state.

        Args:
            condition: Condition definition
            state: Current workflow state

        Returns:
            Boolean result of the condition evaluation
        """
        condition_type = condition.get("type")

        if condition_type == "exists":
            path = condition.get("path", "")
            try:
                value = self._get_data_from_path(state, path)
                return value is not None
            except Exception:
                return False

        elif condition_type == "equals":
            path = condition.get("path", "")
            expected = condition.get("value")
            try:
                value = self._get_data_from_path(state, path)
                return value == expected
            except Exception:
                return False

        elif condition_type == "not_empty":
            path = condition.get("path", "")
            try:
                value = self._get_data_from_path(state, path)
                if isinstance(value, (list, dict)):
                    return len(value) > 0
                return bool(value)
            except Exception:
                return False

        else:
            raise ValueError(f"Unsupported condition type: {condition_type}")

    def _get_data_from_path(self, state: Dict[str, Any], path: str) -> Any:
        """
        Get data from the workflow state using a path.

        Args:
            state: Current workflow state
            path: Path to the data (e.g., "results.step1.output")

        Returns:
            Data at the specified path
        """
        if not path:
            return None

        parts = path.split(".")
        current = state

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def _transform_merge(
        self, input_data: Any, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge multiple data sources.

        Args:
            input_data: Input data (list of dictionaries to merge)
            options: Transformation options

        Returns:
            Merged data
        """
        if not isinstance(input_data, list):
            return {"error": "Merge transform requires list input"}

        result = {}
        for item in input_data:
            if isinstance(item, dict):
                result.update(item)

        return result

    def _transform_filter(
        self, input_data: Any, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filter data based on criteria.

        Args:
            input_data: Input data (list to filter)
            options: Transformation options including filter criteria

        Returns:
            Filtered data
        """
        if not isinstance(input_data, list):
            return {"error": "Filter transform requires list input"}

        criteria = options.get("criteria", {})
        if not criteria:
            return {"filtered": input_data}

        filtered = []
        for item in input_data:
            if not isinstance(item, dict):
                continue

            match = True
            for key, value in criteria.items():
                if key not in item or item[key] != value:
                    match = False
                    break

            if match:
                filtered.append(item)

        return {"filtered": filtered}

    def _transform_map(
        self, input_data: Any, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map data using a mapping function.

        Args:
            input_data: Input data (list to map)
            options: Transformation options including mapping function

        Returns:
            Mapped data
        """
        if not isinstance(input_data, list):
            return {"error": "Map transform requires list input"}

        # Extract fields if specified
        if "fields" in options:
            fields = options["fields"]
            mapped = []

            for item in input_data:
                if not isinstance(item, dict):
                    continue

                mapped_item = {}
                for field in fields:
                    if field in item:
                        mapped_item[field] = item[field]

                mapped.append(mapped_item)

            return {"mapped": mapped}

        # Default is identity mapping
        return {"mapped": input_data}
