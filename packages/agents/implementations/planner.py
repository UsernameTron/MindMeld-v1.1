"""
Standardized PlannerAgent implementation.

This module provides a planning agent that follows the standardized
AgentProtocol interface, offering task decomposition and strategic
planning capabilities.
"""

from typing import Any, Dict, List

from ..base.registry import AgentRegistry


class PlannerAgent:
    """Standardized agent for developing plans and decomposing tasks.

    This agent acts as the strategic component of the multi-agent system,
    responsible for breaking down complex tasks into manageable subtasks
    and creating clear, effective plans.

    The agent implements the AgentProtocol interface for consistent interaction
    with the agent registry system.
    """

    def __init__(self, name: str = "planner", **kwargs):
        """Initialize the planner agent.

        Args:
            name: Unique identifier for this agent instance
            **kwargs: Additional configuration options
        """
        self.name = name
        self.config = kwargs

        # Register with the global registry
        registry = AgentRegistry.get_instance()
        registry.register_agent(self.name, self)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task to create a decomposed plan.

        Args:
            input_data: Dictionary containing:
                - 'task': Task description to plan (required)
                - 'context': Optional context information
                - 'constraints': Optional constraints to consider
                - 'goals': Optional specific goals or objectives
                - 'timeline': Optional timeline requirements

        Returns:
            Dictionary containing:
                - 'status': 'success' or 'error'
                - 'plan': Structured plan with steps and details
                - 'metadata': Processing metadata
        """
        try:
            # Validate input
            validation_result = self.validate_input(input_data)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "error": f"Invalid input: {validation_result['message']}",
                    "metadata": self._get_metadata(),
                }

            task = input_data["task"]
            context = input_data.get("context", "")
            constraints = input_data.get("constraints", [])
            goals = input_data.get("goals", [])
            timeline = input_data.get("timeline", "")

            # Create the plan
            plan = self._create_plan(task, context, constraints, goals, timeline)

            return {"status": "success", "plan": plan, "metadata": self._get_metadata()}

        except Exception as e:
            return {
                "status": "error",
                "error": f"Planning failed: {str(e)}",
                "metadata": self._get_metadata(),
            }

    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data format and requirements.

        Args:
            input_data: Input data to validate

        Returns:
            Validation result with 'valid' boolean and 'message'
        """
        if not isinstance(input_data, dict):
            return {"valid": False, "message": "Input must be a dictionary"}

        if "task" not in input_data:
            return {"valid": False, "message": "'task' is required"}

        if not isinstance(input_data["task"], str):
            return {"valid": False, "message": "'task' must be a string"}

        if not input_data["task"].strip():
            return {"valid": False, "message": "'task' cannot be empty"}

        # Validate optional fields
        optional_fields = ["context", "timeline"]
        for field in optional_fields:
            if field in input_data and not isinstance(input_data[field], str):
                return {"valid": False, "message": f"'{field}' must be a string"}

        list_fields = ["constraints", "goals"]
        for field in list_fields:
            if field in input_data and not isinstance(input_data[field], list):
                return {"valid": False, "message": f"'{field}' must be a list"}

        return {"valid": True, "message": "Input is valid"}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and supported operations.

        Returns:
            Dictionary describing agent capabilities
        """
        return {
            "name": self.name,
            "type": "planner",
            "description": "Strategic planning and task decomposition agent",
            "capabilities": [
                "task_decomposition",
                "strategic_planning",
                "step_sequencing",
                "constraint_analysis",
                "goal_alignment",
                "timeline_planning",
                "risk_assessment",
                "resource_planning",
            ],
            "input_schema": {
                "required": ["task"],
                "optional": ["context", "constraints", "goals", "timeline"],
                "task": "Task description to plan",
                "context": "Optional context information",
                "constraints": "List of constraints to consider",
                "goals": "List of specific goals or objectives",
                "timeline": "Timeline requirements",
            },
            "output_schema": {
                "status": "success or error",
                "plan": {
                    "summary": "High-level plan summary",
                    "steps": "List of detailed steps",
                    "timeline": "Estimated timeline",
                    "resources": "Required resources",
                    "risks": "Identified risks and mitigations",
                },
                "metadata": "processing metadata",
            },
        }

    def _create_plan(
        self,
        task: str,
        context: str,
        constraints: List[str],
        goals: List[str],
        timeline: str,
    ) -> Dict[str, Any]:
        """Create a structured plan for the given task.

        Args:
            task: Task description
            context: Context information
            constraints: List of constraints
            goals: List of goals
            timeline: Timeline requirements

        Returns:
            Structured plan dictionary
        """
        # Analyze the task to identify key components
        task_analysis = self._analyze_task(task, context)

        # Break down into steps
        steps = self._decompose_task(task, task_analysis, constraints, goals)

        # Estimate timeline and resources
        timeline_estimate = self._estimate_timeline(steps, timeline)
        resources = self._identify_resources(steps)

        # Identify risks and mitigations
        risks = self._identify_risks(steps, constraints)

        return {
            "summary": self._create_summary(task, len(steps)),
            "task_analysis": task_analysis,
            "steps": steps,
            "timeline": timeline_estimate,
            "resources": resources,
            "risks": risks,
            "constraints": constraints,
            "goals": goals,
        }

    def _analyze_task(self, task: str, context: str) -> Dict[str, Any]:
        """Analyze the task to understand its complexity and requirements."""
        # Simple task analysis based on keywords and structure
        task_lower = task.lower()

        complexity = "medium"
        if any(word in task_lower for word in ["simple", "basic", "quick", "easy"]):
            complexity = "low"
        elif any(
            word in task_lower
            for word in ["complex", "advanced", "comprehensive", "detailed"]
        ):
            complexity = "high"

        # Identify task type
        task_type = "general"
        if any(
            word in task_lower for word in ["code", "program", "develop", "implement"]
        ):
            task_type = "development"
        elif any(word in task_lower for word in ["analyze", "research", "investigate"]):
            task_type = "analysis"
        elif any(word in task_lower for word in ["test", "validate", "verify"]):
            task_type = "testing"
        elif any(word in task_lower for word in ["design", "plan", "architect"]):
            task_type = "design"

        # Estimate effort
        estimated_steps = 3  # Default
        if complexity == "low":
            estimated_steps = 2
        elif complexity == "high":
            estimated_steps = 5

        return {
            "complexity": complexity,
            "type": task_type,
            "estimated_steps": estimated_steps,
            "key_concepts": self._extract_key_concepts(task),
            "dependencies": self._identify_dependencies(task, context),
        }

    def _extract_key_concepts(self, task: str) -> List[str]:
        """Extract key concepts from the task description."""
        # Simple keyword extraction
        important_words = []
        words = task.split()

        # Look for nouns and technical terms
        for word in words:
            word_clean = word.strip(".,!?()[]{}").lower()
            if len(word_clean) > 3 and not word_clean in [
                "that",
                "this",
                "with",
                "from",
                "will",
                "have",
                "been",
            ]:
                important_words.append(word_clean)

        return list(set(important_words))[:10]  # Return up to 10 unique concepts

    def _identify_dependencies(self, task: str, context: str) -> List[str]:
        """Identify potential dependencies for the task."""
        dependencies = []
        combined_text = f"{task} {context}".lower()

        # Look for common dependency indicators
        if "database" in combined_text or "db" in combined_text:
            dependencies.append("Database access")
        if "api" in combined_text or "service" in combined_text:
            dependencies.append("External API/service")
        if "file" in combined_text or "data" in combined_text:
            dependencies.append("Data files")
        if "test" in combined_text:
            dependencies.append("Test data/environment")
        if "deploy" in combined_text or "production" in combined_text:
            dependencies.append("Deployment environment")

        return dependencies

    def _decompose_task(
        self,
        task: str,
        analysis: Dict[str, Any],
        constraints: List[str],
        goals: List[str],
    ) -> List[Dict[str, Any]]:
        """Decompose the task into detailed steps."""
        steps = []
        task_type = analysis["type"]
        complexity = analysis["complexity"]

        # Base step templates by task type
        if task_type == "development":
            steps = self._create_development_steps(task, complexity)
        elif task_type == "analysis":
            steps = self._create_analysis_steps(task, complexity)
        elif task_type == "testing":
            steps = self._create_testing_steps(task, complexity)
        elif task_type == "design":
            steps = self._create_design_steps(task, complexity)
        else:
            steps = self._create_general_steps(task, complexity)

        # Add constraint and goal considerations
        steps = self._apply_constraints_to_steps(steps, constraints)
        steps = self._align_steps_with_goals(steps, goals)

        return steps

    def _create_development_steps(
        self, task: str, complexity: str
    ) -> List[Dict[str, Any]]:
        """Create steps for development tasks."""
        base_steps = [
            {
                "id": 1,
                "title": "Requirements Analysis",
                "description": "Analyze and document the requirements",
                "estimated_time": "30 minutes",
                "dependencies": [],
                "deliverables": ["Requirements document"],
            },
            {
                "id": 2,
                "title": "Design and Planning",
                "description": "Create design specifications and implementation plan",
                "estimated_time": "45 minutes",
                "dependencies": [1],
                "deliverables": ["Design document", "Implementation plan"],
            },
            {
                "id": 3,
                "title": "Implementation",
                "description": "Write and implement the code",
                "estimated_time": "2 hours",
                "dependencies": [2],
                "deliverables": ["Working code"],
            },
            {
                "id": 4,
                "title": "Testing",
                "description": "Test the implementation thoroughly",
                "estimated_time": "45 minutes",
                "dependencies": [3],
                "deliverables": ["Test results", "Bug fixes"],
            },
        ]

        if complexity == "high":
            base_steps.insert(
                2,
                {
                    "id": 2.5,
                    "title": "Prototype Development",
                    "description": "Create a working prototype to validate approach",
                    "estimated_time": "1 hour",
                    "dependencies": [2],
                    "deliverables": ["Prototype"],
                },
            )
            # Update subsequent step IDs
            for i, step in enumerate(base_steps[3:], 3):
                step["id"] = i + 1
                step["dependencies"] = [
                    dep + 0.5 if dep == 2 else dep for dep in step["dependencies"]
                ]

        return base_steps

    def _create_analysis_steps(
        self, task: str, complexity: str
    ) -> List[Dict[str, Any]]:
        """Create steps for analysis tasks."""
        return [
            {
                "id": 1,
                "title": "Data Collection",
                "description": "Gather relevant data and information",
                "estimated_time": "45 minutes",
                "dependencies": [],
                "deliverables": ["Data sources", "Raw data"],
            },
            {
                "id": 2,
                "title": "Data Processing",
                "description": "Clean and prepare data for analysis",
                "estimated_time": "30 minutes",
                "dependencies": [1],
                "deliverables": ["Processed data"],
            },
            {
                "id": 3,
                "title": "Analysis",
                "description": "Perform the required analysis",
                "estimated_time": "1 hour",
                "dependencies": [2],
                "deliverables": ["Analysis results"],
            },
            {
                "id": 4,
                "title": "Report Generation",
                "description": "Create comprehensive report with findings",
                "estimated_time": "45 minutes",
                "dependencies": [3],
                "deliverables": ["Analysis report"],
            },
        ]

    def _create_testing_steps(self, task: str, complexity: str) -> List[Dict[str, Any]]:
        """Create steps for testing tasks."""
        return [
            {
                "id": 1,
                "title": "Test Planning",
                "description": "Define test strategy and create test plan",
                "estimated_time": "30 minutes",
                "dependencies": [],
                "deliverables": ["Test plan", "Test strategy"],
            },
            {
                "id": 2,
                "title": "Test Case Development",
                "description": "Create detailed test cases",
                "estimated_time": "45 minutes",
                "dependencies": [1],
                "deliverables": ["Test cases"],
            },
            {
                "id": 3,
                "title": "Test Execution",
                "description": "Execute test cases and record results",
                "estimated_time": "1 hour",
                "dependencies": [2],
                "deliverables": ["Test results"],
            },
            {
                "id": 4,
                "title": "Results Analysis",
                "description": "Analyze test results and create summary",
                "estimated_time": "30 minutes",
                "dependencies": [3],
                "deliverables": ["Test summary", "Defect report"],
            },
        ]

    def _create_design_steps(self, task: str, complexity: str) -> List[Dict[str, Any]]:
        """Create steps for design tasks."""
        return [
            {
                "id": 1,
                "title": "Requirements Gathering",
                "description": "Collect and document design requirements",
                "estimated_time": "30 minutes",
                "dependencies": [],
                "deliverables": ["Requirements document"],
            },
            {
                "id": 2,
                "title": "Concept Development",
                "description": "Develop initial design concepts",
                "estimated_time": "1 hour",
                "dependencies": [1],
                "deliverables": ["Concept sketches"],
            },
            {
                "id": 3,
                "title": "Detailed Design",
                "description": "Create detailed design specifications",
                "estimated_time": "1.5 hours",
                "dependencies": [2],
                "deliverables": ["Detailed design documents"],
            },
            {
                "id": 4,
                "title": "Design Review",
                "description": "Review and refine the design",
                "estimated_time": "30 minutes",
                "dependencies": [3],
                "deliverables": ["Final design"],
            },
        ]

    def _create_general_steps(self, task: str, complexity: str) -> List[Dict[str, Any]]:
        """Create steps for general tasks."""
        return [
            {
                "id": 1,
                "title": "Planning",
                "description": "Plan the approach and methodology",
                "estimated_time": "30 minutes",
                "dependencies": [],
                "deliverables": ["Project plan"],
            },
            {
                "id": 2,
                "title": "Execution",
                "description": "Execute the main task",
                "estimated_time": "1 hour",
                "dependencies": [1],
                "deliverables": ["Task output"],
            },
            {
                "id": 3,
                "title": "Review and Finalization",
                "description": "Review results and finalize deliverables",
                "estimated_time": "30 minutes",
                "dependencies": [2],
                "deliverables": ["Final deliverables"],
            },
        ]

    def _apply_constraints_to_steps(
        self, steps: List[Dict[str, Any]], constraints: List[str]
    ) -> List[Dict[str, Any]]:
        """Apply constraints to modify the steps as needed."""
        # Simple constraint handling - could be expanded
        for constraint in constraints:
            constraint_lower = constraint.lower()
            if "time" in constraint_lower or "quick" in constraint_lower:
                # Reduce time estimates
                for step in steps:
                    time_str = step["estimated_time"]
                    if "hour" in time_str:
                        hours = float(time_str.split()[0])
                        step["estimated_time"] = f"{max(0.5, hours * 0.7)} hours"
                    elif "minute" in time_str:
                        minutes = int(time_str.split()[0])
                        step["estimated_time"] = (
                            f"{max(15, int(minutes * 0.8))} minutes"
                        )

        return steps

    def _align_steps_with_goals(
        self, steps: List[Dict[str, Any]], goals: List[str]
    ) -> List[Dict[str, Any]]:
        """Align steps with specified goals."""
        # Add goal alignment notes to relevant steps
        for goal in goals:
            goal_lower = goal.lower()
            for step in steps:
                if any(
                    word in step["description"].lower() for word in goal_lower.split()
                ):
                    if "goal_alignment" not in step:
                        step["goal_alignment"] = []
                    step["goal_alignment"].append(goal)

        return steps

    def _estimate_timeline(
        self, steps: List[Dict[str, Any]], timeline_req: str
    ) -> Dict[str, Any]:
        """Estimate timeline for the plan."""
        total_minutes = 0

        for step in steps:
            time_str = step["estimated_time"]
            if "hour" in time_str:
                hours = float(time_str.split()[0])
                total_minutes += hours * 60
            elif "minute" in time_str:
                minutes = int(time_str.split()[0])
                total_minutes += minutes

        total_hours = total_minutes / 60

        return {
            "total_estimated_time": f"{total_hours:.1f} hours",
            "number_of_steps": len(steps),
            "critical_path": [step["id"] for step in steps],  # Simplified
            "timeline_requirement": timeline_req,
            "feasibility": (
                "feasible"
                if not timeline_req or "urgent" not in timeline_req.lower()
                else "tight"
            ),
        }

    def _identify_resources(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify required resources for the plan."""
        resources = {
            "human_resources": ["Primary executor"],
            "tools": ["Standard development tools"],
            "data": [],
            "external_dependencies": [],
        }

        # Extract resource requirements from step descriptions
        for step in steps:
            desc_lower = step["description"].lower()
            if "database" in desc_lower:
                resources["external_dependencies"].append("Database access")
            if "test" in desc_lower:
                resources["tools"].append("Testing framework")
            if "design" in desc_lower:
                resources["tools"].append("Design tools")

        return resources

    def _identify_risks(
        self, steps: List[Dict[str, Any]], constraints: List[str]
    ) -> List[Dict[str, Any]]:
        """Identify potential risks and mitigations."""
        risks = []

        # Common risk patterns
        if len(steps) > 4:
            risks.append(
                {
                    "risk": "Project complexity",
                    "impact": "medium",
                    "probability": "medium",
                    "mitigation": "Break down complex steps further, regular progress reviews",
                }
            )

        # Timeline risks
        for constraint in constraints:
            if "time" in constraint.lower() or "urgent" in constraint.lower():
                risks.append(
                    {
                        "risk": "Timeline pressure",
                        "impact": "high",
                        "probability": "medium",
                        "mitigation": "Prioritize core features, consider parallel execution",
                    }
                )

        # Dependency risks
        for step in steps:
            if len(step["dependencies"]) > 1:
                risks.append(
                    {
                        "risk": f"Multiple dependencies for {step['title']}",
                        "impact": "medium",
                        "probability": "low",
                        "mitigation": "Ensure clear completion criteria for dependent steps",
                    }
                )

        return risks

    def _create_summary(self, task: str, num_steps: int) -> str:
        """Create a high-level summary of the plan."""
        return (
            f"Plan for '{task}' decomposed into {num_steps} structured steps. "
            f"The plan includes detailed timelines, resource requirements, and risk mitigation strategies."
        )

    def _get_metadata(self) -> Dict[str, Any]:
        """Get processing metadata."""
        return {"agent_name": self.name, "agent_type": "planner", "version": "1.0.0"}


# Register the agent class for easy instantiation
def create_planner_agent(**kwargs) -> PlannerAgent:
    """Factory function to create a PlannerAgent instance."""
    return PlannerAgent(**kwargs)


# Auto-register when module is imported
if __name__ != "__main__":
    registry = AgentRegistry.get_instance()
    registry.register_agent_class("planner", create_planner_agent)
