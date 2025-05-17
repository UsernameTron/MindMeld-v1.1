from typing import Dict, Any, Optional, List, Union
import json
import logging

from .base import Agent
from ..api.client import ClaudeAPIClient

logger = logging.getLogger(__name__)

class PlannerAgent(Agent):
    """
    Agent responsible for developing plans and decomposing tasks into subtasks.
    Acts as the strategic component of the multi-agent system.
    """
    
    def __init__(
        self,
        api_client: ClaudeAPIClient,
        name: str = "Planner",
        temperature: float = 0.5,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the planner agent.
        
        Args:
            api_client: Claude API client instance
            name: Agent name
            temperature: Temperature for responses (lower for more deterministic planning)
            max_tokens: Maximum tokens in the response
            system_prompt: Custom system prompt (if None, a default is used)
        """
        role = "planning, task decomposition, and strategic reasoning"
        super().__init__(
            name=name,
            role=role,
            api_client=api_client,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for the planner."""
        return (
            f"You are {self.name}, an AI specialized in {self.role}. "
            f"You excel at breaking down complex tasks into manageable steps and creating clear, "
            f"effective plans. Your output should be structured, logical, and actionable. "
            f"You think step-by-step and consider potential challenges and edge cases. "
            f"You focus exclusively on planning and avoid executing tasks yourself."
        )
    
    def process(self, task_description: str) -> Dict[str, Any]:
        """
        Process a task description and create a plan.
        
        Args:
            task_description: Description of the task to plan for
            
        Returns:
            Structured plan with steps, dependencies, and metadata
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_plan",
                    "description": "Create a structured plan with steps and metadata",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "objective": {
                                "type": "string",
                                "description": "Refined main objective of the task"
                            },
                            "steps": {
                                "type": "array",
                                "description": "Ordered list of steps to complete the objective",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "Unique step identifier (e.g., 'step_1')"
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "Clear description of the step"
                                        },
                                        "expected_outcome": {
                                            "type": "string",
                                            "description": "What should be achieved after this step"
                                        },
                                        "dependencies": {
                                            "type": "array",
                                            "description": "IDs of steps that must be completed before this one",
                                            "items": {
                                                "type": "string"
                                            }
                                        }
                                    },
                                    "required": ["id", "description", "expected_outcome"]
                                }
                            },
                            "estimated_completion_time": {
                                "type": "string",
                                "description": "Estimated time to complete the full plan"
                            },
                            "potential_challenges": {
                                "type": "array",
                                "description": "Potential issues that might arise",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": ["objective", "steps"]
                    }
                }
            }
        ]
        
        # Add to history
        self.add_to_history({
            "role": "user",
            "content": (
                f"I need a detailed plan for the following task:\n\n"
                f"{task_description}\n\n"
                f"Please break it down into clear, logical steps with dependencies where appropriate."
            )
        })
        
        # Make API call with tool
        response = self._call_claude(
            messages=self.history,
            tools=tools
        )
        
        # Extract plan from tool calls if present
        plan = {}
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call.function.name == "create_plan":
                    try:
                        plan = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse plan JSON: {e}")
                        plan = {}
        
        # If no tool call, extract from response text
        if not plan and response.content:
            try:
                # Try to find JSON-like content in the response
                content = response.content[0].text
                
                # Look for JSON block (common Claude formatting)
                import re
                json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group(1))
                else:
                    logger.warning("No structured plan found in response")
                    # Create minimal plan structure from text
                    plan = {
                        "objective": task_description,
                        "steps": [{"id": "step_1", "description": content, "expected_outcome": "Task completed"}]
                    }
            except Exception as e:
                logger.error(f"Error extracting plan from text response: {e}")
                plan = {
                    "objective": task_description,
                    "error": "Failed to create structured plan"
                }
        
        return plan
    
    def refine_plan(self, original_plan: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """
        Refine an existing plan based on feedback.
        
        Args:
            original_plan: The original plan to refine
            feedback: Feedback about the plan
            
        Returns:
            Refined plan
        """
        # Convert plan to string for prompt
        plan_str = json.dumps(original_plan, indent=2)
        
        # Add to history
        self.add_to_history({
            "role": "user",
            "content": (
                f"Please refine the following plan based on this feedback:\n\n"
                f"ORIGINAL PLAN:\n```json\n{plan_str}\n```\n\n"
                f"FEEDBACK:\n{feedback}\n\n"
                f"Please provide an improved version of the plan addressing the feedback."
            )
        })
        
        # Use the same tools as in process
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_plan",
                    "description": "Create a structured plan with steps and metadata",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "objective": {
                                "type": "string",
                                "description": "Refined main objective of the task"
                            },
                            "steps": {
                                "type": "array",
                                "description": "Ordered list of steps to complete the objective",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "Unique step identifier (e.g., 'step_1')"
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "Clear description of the step"
                                        },
                                        "expected_outcome": {
                                            "type": "string",
                                            "description": "What should be achieved after this step"
                                        },
                                        "dependencies": {
                                            "type": "array",
                                            "description": "IDs of steps that must be completed before this one",
                                            "items": {
                                                "type": "string"
                                            }
                                        }
                                    },
                                    "required": ["id", "description", "expected_outcome"]
                                }
                            },
                            "estimated_completion_time": {
                                "type": "string",
                                "description": "Estimated time to complete the full plan"
                            },
                            "potential_challenges": {
                                "type": "array",
                                "description": "Potential issues that might arise",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": ["objective", "steps"]
                    }
                }
            }
        ]
        
        # Make API call with tool
        response = self._call_claude(
            messages=self.history,
            tools=tools
        )
        
        # Extract plan from tool calls if present
        refined_plan = {}
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call.function.name == "create_plan":
                    try:
                        refined_plan = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse refined plan JSON: {e}")
                        refined_plan = original_plan  # Fallback to original
        
        # If no tool call, try to extract from response text
        if not refined_plan and response.content:
            try:
                # Try to find JSON-like content in the response
                content = response.content[0].text
                
                # Look for JSON block
                import re
                json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
                if json_match:
                    refined_plan = json.loads(json_match.group(1))
                else:
                    logger.warning("No structured refined plan found in response")
                    refined_plan = original_plan  # Fallback to original
            except Exception as e:
                logger.error(f"Error extracting refined plan from text response: {e}")
                refined_plan = original_plan  # Fallback to original
        
        return refined_plan