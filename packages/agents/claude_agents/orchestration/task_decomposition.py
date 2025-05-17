from typing import Dict, Any, Optional, List, Union
import logging

from ..agents.planner import PlannerAgent
from ..api.client import ClaudeAPIClient

logger = logging.getLogger(__name__)

class TaskDecomposer:
    """
    Specialized component for decomposing complex tasks into simpler subtasks.
    Uses a planner agent to break down tasks with appropriate granularity.
    """
    
    def __init__(
        self,
        api_client: ClaudeAPIClient,
        planner: Optional[PlannerAgent] = None,
        max_subtasks: int = 10,
        min_subtasks: int = 2,
    ):
        """
        Initialize the task decomposer.
        
        Args:
            api_client: Claude API client instance
            planner: Optional custom planner agent (if None, a default one is created)
            max_subtasks: Maximum number of subtasks to create
            min_subtasks: Minimum number of subtasks for complex tasks
        """
        self.api_client = api_client
        self.planner = planner or PlannerAgent(
            api_client,
            name="TaskDecomposer",
            system_prompt=(
                "You are TaskDecomposer, an AI specialized in analyzing complex tasks and "
                "breaking them down into appropriate subtasks. Your goal is to decompose tasks "
                "with the right level of granularity - not too fine-grained and not too coarse. "
                "Each subtask should be self-contained, clear, and achievable."
            )
        )
        
        self.max_subtasks = max_subtasks
        self.min_subtasks = min_subtasks
    
    def decompose(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Decompose a complex task into subtasks.
        
        Args:
            task: Task description to decompose
            context: Optional additional context
            
        Returns:
            List of subtask definitions
        """
        # Create a prompt that encourages good decomposition
        task_prompt = (
            f"Please decompose the following task into {self.min_subtasks}-{self.max_subtasks} "
            f"clear, manageable subtasks with the right level of granularity.\n\n"
            f"TASK: {task}\n\n"
        )
        
        if context:
            # Add context if provided
            context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
            task_prompt += f"CONTEXT:\n{context_str}\n\n"
        
        task_prompt += (
            "For each subtask, provide:\n"
            "1. A clear description of what needs to be done\n"
            "2. The expected outcome\n"
            "3. Any dependencies on other subtasks\n"
            "4. Estimated complexity (low, medium, high)\n\n"
            "Ensure your decomposition is complete and covers all aspects of the task."
        )
        
        # Get decomposition plan from planner
        plan = self.planner.process(task_prompt)
        
        # Extract subtasks from plan
        subtasks = []
        for step in plan.get("steps", []):
            # Convert plan step to subtask format
            subtask = {
                "id": step.get("id", ""),
                "description": step.get("description", ""),
                "expected_outcome": step.get("expected_outcome", ""),
                "dependencies": step.get("dependencies", []),
                "complexity": self._estimate_complexity(step),
                "status": "pending"
            }
            subtasks.append(subtask)
        
        logger.info(f"Decomposed task into {len(subtasks)} subtasks")
        return subtasks
    
    def _estimate_complexity(self, step: Dict[str, Any]) -> str:
        """
        Estimate the complexity of a step based on its description.
        
        Args:
            step: Step definition from plan
            
        Returns:
            Complexity level (low, medium, high)
        """
        # Use hints from the planner if available
        description = step.get("description", "").lower()
        
        # Look for complexity hints in the description
        if any(word in description for word in ["simple", "straightforward", "basic", "easy"]):
            return "low"
        elif any(word in description for word in ["complex", "difficult", "challenging", "advanced"]):
            return "high"
        else:
            return "medium"
    
    def rebalance_subtasks(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rebalance subtasks if they are too fine-grained or too coarse.
        
        Args:
            subtasks: List of subtask definitions
            
        Returns:
            Rebalanced list of subtasks
        """
        # If we have too many subtasks, try to combine some
        if len(subtasks) > self.max_subtasks:
            logger.info(f"Too many subtasks ({len(subtasks)}). Attempting to combine some.")
            
            # Combine subtasks prompt
            combine_prompt = (
                f"The following list of {len(subtasks)} subtasks is too fine-grained. "
                f"Please combine them into at most {self.max_subtasks} subtasks while preserving "
                f"all functionality and maintaining clear separations of concerns.\n\n"
                f"CURRENT SUBTASKS:\n"
            )
            
            for subtask in subtasks:
                combine_prompt += (
                    f"ID: {subtask['id']}\n"
                    f"Description: {subtask['description']}\n"
                    f"Expected outcome: {subtask['expected_outcome']}\n"
                    f"Dependencies: {', '.join(subtask['dependencies'])}\n\n"
                )
            
            # Get new decomposition from planner
            plan = self.planner.process(combine_prompt)
            
            # Extract rebalanced subtasks
            rebalanced = []
            for step in plan.get("steps", []):
                subtask = {
                    "id": step.get("id", ""),
                    "description": step.get("description", ""),
                    "expected_outcome": step.get("expected_outcome", ""),
                    "dependencies": step.get("dependencies", []),
                    "complexity": self._estimate_complexity(step),
                    "status": "pending"
                }
                rebalanced.append(subtask)
            
            return rebalanced
        
        # If we have too few subtasks, try to split some
        elif len(subtasks) < self.min_subtasks and len(subtasks) > 0:
            logger.info(f"Too few subtasks ({len(subtasks)}). Attempting to split some.")
            
            # Find the most complex subtask to split
            complex_subtasks = sorted(
                subtasks,
                key=lambda x: {"low": 0, "medium": 1, "high": 2}.get(x.get("complexity", "medium"), 1),
                reverse=True
            )
            
            if complex_subtasks:
                subtask_to_split = complex_subtasks[0]
                
                # Create prompt to split this subtask
                split_prompt = (
                    f"Please split the following complex subtask into 2-3 simpler subtasks "
                    f"while preserving the original functionality:\n\n"
                    f"SUBTASK TO SPLIT:\n"
                    f"Description: {subtask_to_split['description']}\n"
                    f"Expected outcome: {subtask_to_split['expected_outcome']}\n\n"
                    f"Provide a clear description, expected outcome, and any dependencies for each new subtask."
                )
                
                # Get decomposition from planner
                split_plan = self.planner.process(split_prompt)
                
                # Extract new subtasks
                new_subtasks = []
                for step in split_plan.get("steps", []):
                    subtask = {
                        "id": f"{subtask_to_split['id']}_{step.get('id', '')}",
                        "description": step.get("description", ""),
                        "expected_outcome": step.get("expected_outcome", ""),
                        "dependencies": step.get("dependencies", []),
                        "complexity": self._estimate_complexity(step),
                        "status": "pending"
                    }
                    new_subtasks.append(subtask)
                
                # Update dependencies in other subtasks
                for subtask in subtasks:
                    if subtask_to_split["id"] in subtask.get("dependencies", []):
                        # Replace the dependency on the split subtask with dependencies on all new subtasks
                        subtask["dependencies"].remove(subtask_to_split["id"])
                        subtask["dependencies"].extend([s["id"] for s in new_subtasks])
                
                # Remove the original subtask and add the new ones
                rebalanced = [s for s in subtasks if s["id"] != subtask_to_split["id"]]
                rebalanced.extend(new_subtasks)
                
                return rebalanced
        
        # If the number of subtasks is within range, return as is
        return subtasks