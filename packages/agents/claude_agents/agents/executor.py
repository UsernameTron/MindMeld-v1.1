from typing import Dict, Any, Optional, List, Union, Callable
import json
import logging

from .base import Agent
from ..api.client import ClaudeAPIClient

logger = logging.getLogger(__name__)

class ExecutorAgent(Agent):
    """
    Agent responsible for executing specific tasks and producing concrete outputs.
    Acts as the operational component of the multi-agent system.
    """
    
    def __init__(
        self,
        api_client: ClaudeAPIClient,
        name: str = "Executor",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize the executor agent.
        
        Args:
            api_client: Claude API client instance
            name: Agent name
            temperature: Temperature for responses (higher for more creativity in execution)
            max_tokens: Maximum tokens in the response
            system_prompt: Custom system prompt (if None, a default is used)
            tools: Optional list of tool definitions the executor can use
        """
        role = "executing tasks and producing concrete outputs"
        super().__init__(
            name=name,
            role=role,
            api_client=api_client,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self.tools = tools or []
        self.tool_callbacks = {}  # Map of tool name to callback function
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for the executor."""
        return (
            f"You are {self.name}, an AI specialized in {self.role}. "
            f"You focus on completing specific tasks with precision and efficiency. "
            f"You provide concrete, implementable solutions and outputs. "
            f"You think step-by-step and follow instructions carefully. "
            f"When given a task, you execute it to completion with high-quality results."
        )
    
    def register_tool(self, tool_definition: Dict[str, Any], callback: Callable) -> None:
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
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task and execute it.
        
        Args:
            task: Task definition with description and any required context
            
        Returns:
            Execution results
        """
        # Prepare task description
        task_description = task.get("description", "")
        task_context = task.get("context", {})
        
        # Format context as string if needed
        context_str = ""
        if task_context:
            if isinstance(task_context, str):
                context_str = task_context
            else:
                context_str = json.dumps(task_context, indent=2)
        
        # Add to history
        self.add_to_history({
            "role": "user",
            "content": (
                f"Please execute the following task:\n\n"
                f"TASK: {task_description}\n\n"
                f"{f'CONTEXT:\n{context_str}' if context_str else ''}"
            )
        })
        
        # Make API call with tools
        response = self._call_claude(
            messages=self.history,
            tools=self.tools
        )
        
        # Process tool calls if present
        execution_results = {
            "task_id": task.get("id", "unknown"),
            "outputs": [],
            "tool_calls": [],
            "completion": ""
        }
        
        # Extract completion text
        if response.content:
            execution_results["completion"] = response.content[0].text
        
        # Process tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = tool_call.function.arguments
                
                # Record the tool call
                execution_results["tool_calls"].append({
                    "tool": tool_name,
                    "arguments": tool_args
                })
                
                # Execute callback if registered
                if tool_name in self.tool_callbacks:
                    try:
                        result = self.tool_callbacks[tool_name](tool_args)
                        execution_results["outputs"].append({
                            "tool": tool_name,
                            "result": result
                        })
                    except Exception as e:
                        logger.error(f"Error executing tool '{tool_name}': {str(e)}")
                        execution_results["outputs"].append({
                            "tool": tool_name,
                            "error": str(e)
                        })
        
        return execution_results
    
    def process_step(self, step: Dict[str, Any], plan_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a specific step from a plan.
        
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
                # Add any other relevant context
            }
        }
        
        # Execute the task
        result = self.process(task)
        
        # Add step-specific metadata
        result["step_id"] = step.get("id", "unknown_step")
        result["step_description"] = step.get("description", "")
        
        return result