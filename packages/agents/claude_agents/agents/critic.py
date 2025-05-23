import json
import logging
from typing import Any, Dict, List, Optional

from ..api.client import ClaudeAPIClient
from .base import Agent

logger = logging.getLogger(__name__)


class CriticAgent(Agent):
    """
    Agent responsible for evaluating outputs, finding errors, and suggesting improvements.
    Acts as the quality control component of the multi-agent system.
    """

    def __init__(
        self,
        api_client: ClaudeAPIClient,
        name: str = "Critic",
        temperature: float = 0.3,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the critic agent.

        Args:
            api_client: Claude API client instance
            name: Agent name
            temperature: Temperature for responses (lower for more consistent evaluation)
            max_tokens: Maximum tokens in the response
            system_prompt: Custom system prompt (if None, a default is used)
        """
        role = "evaluation, error detection, and quality improvement"
        super().__init__(
            name=name,
            role=role,
            api_client=api_client,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _default_system_prompt(self) -> str:
        """Default system prompt for the critic."""
        return (
            f"You are {self.name}, an AI specialized in {self.role}. "
            f"You carefully analyze outputs, identify errors, inconsistencies, or areas for improvement. "
            f"You provide specific, constructive feedback on how to enhance quality. "
            f"You consider multiple perspectives and evaluate against objective standards. "
            f"Your analysis is thorough, clear, and actionable. "
            f"You focus on critical evaluation rather than making the improvements yourself."
        )

    def process(
        self, output: Any, requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate an output against requirements and provide feedback.

        Args:
            output: The output to evaluate (text, code, or structured data)
            requirements: Optional requirements to evaluate against

        Returns:
            Evaluation results with scores and feedback
        """
        tools = [
            {
                "type": "custom",
                "function": {
                    "name": "evaluate_output",
                    "description": "Evaluate output quality and provide feedback",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "quality_score": {
                                "type": "number",
                                "description": "Overall quality score (0-10, where 10 is perfect)",
                            },
                            "correctness_score": {
                                "type": "number",
                                "description": "Correctness score (0-10, where 10 is completely correct)",
                            },
                            "completeness_score": {
                                "type": "number",
                                "description": "Completeness score (0-10, where 10 is fully complete)",
                            },
                            "issues": {
                                "type": "array",
                                "description": "List of identified issues or problems",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "severity": {
                                            "type": "string",
                                            "enum": [
                                                "critical",
                                                "major",
                                                "minor",
                                                "suggestion",
                                            ],
                                            "description": "Severity of the issue",
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "Description of the issue",
                                        },
                                        "location": {
                                            "type": "string",
                                            "description": "Where the issue occurs (section, line number, etc.)",
                                        },
                                    },
                                    "required": ["severity", "description"],
                                },
                            },
                            "strengths": {
                                "type": "array",
                                "description": "List of strengths or positive aspects",
                                "items": {"type": "string"},
                            },
                            "improvement_suggestions": {
                                "type": "array",
                                "description": "Specific suggestions for improvement",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "area": {
                                            "type": "string",
                                            "description": "Area for improvement",
                                        },
                                        "suggestion": {
                                            "type": "string",
                                            "description": "Specific suggestion",
                                        },
                                    },
                                    "required": ["area", "suggestion"],
                                },
                            },
                            "meets_requirements": {
                                "type": "boolean",
                                "description": "Whether the output meets the stated requirements",
                            },
                            "overall_feedback": {
                                "type": "string",
                                "description": "Summary of evaluation and recommendations",
                            },
                        },
                        "required": [
                            "quality_score",
                            "issues",
                            "improvement_suggestions",
                            "meets_requirements",
                            "overall_feedback",
                        ],
                    },
                },
            }
        ]

        # Format output and requirements for prompt
        output_str = (
            str(output)
            if isinstance(output, (str, int, float, bool))
            else json.dumps(output, indent=2)
        )

        # Format requirements if present
        req_str = ""
        if requirements:
            if isinstance(requirements, str):
                req_str = requirements
            else:
                req_str = json.dumps(requirements, indent=2)

        req_block = f"REQUIREMENTS:\n```\n{req_str}\n```\n\n" if req_str else ""
        self.add_to_history(
            {
                "role": "user",
                "content": (
                    f"Please evaluate the following output:\n\n"
                    f"OUTPUT:\n```\n{output_str}\n```\n\n"
                    f"{req_block}"
                    f"Provide a detailed evaluation identifying issues, strengths, and suggestions for improvement."
                ),
            }
        )

        # Make API call with tool
        response = self._call_claude(messages=self.history, tools=tools)

        # Extract evaluation from tool calls if present
        evaluation = {}
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call.function.name == "evaluate_output":
                    try:
                        evaluation = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse evaluation JSON: {e}")
                        evaluation = {}

        # If no tool call, extract from response text
        if not evaluation and response.content:
            content = response.content[0].text

            # Try to find structured content in the response
            try:
                # Look for JSON block
                import re

                json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
                if json_match:
                    evaluation = json.loads(json_match.group(1))
                else:
                    # Create basic evaluation from text
                    evaluation = {
                        "quality_score": None,
                        "issues": [],
                        "improvement_suggestions": [],
                        "meets_requirements": None,
                        "overall_feedback": content,
                    }
            except Exception as e:
                logger.error(f"Error extracting evaluation from text response: {e}")
                evaluation = {
                    "error": "Failed to extract structured evaluation",
                    "raw_response": content,
                }

        return evaluation

    def compare_outputs(
        self, outputs: List[Any], requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple outputs and rank them.

        Args:
            outputs: List of outputs to compare
            requirements: Optional requirements to evaluate against

        Returns:
            Comparison results with rankings and analysis
        """
        # Format outputs for prompt
        outputs_str = ""
        for i, output in enumerate(outputs, 1):
            output_text = (
                str(output)
                if isinstance(output, (str, int, float, bool))
                else json.dumps(output, indent=2)
            )
            outputs_str += f"OUTPUT {i}:\n```\n{output_text}\n```\n\n"

        # Format requirements if present
        req_str = ""
        if requirements:
            if isinstance(requirements, str):
                req_str = requirements
            else:
                req_str = json.dumps(requirements, indent=2)

        # Define comparison tool
        comparison_tool = {
            "type": "custom",
            "function": {
                "name": "compare_outputs",
                "description": "Compare multiple outputs and rank them",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rankings": {
                            "type": "array",
                            "description": "Ranked outputs from best to worst",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "rank": {
                                        "type": "integer",
                                        "description": "Rank position (1 is best)",
                                    },
                                    "output_index": {
                                        "type": "integer",
                                        "description": "Index of the output (1-based)",
                                    },
                                    "score": {
                                        "type": "number",
                                        "description": "Quality score (0-10)",
                                    },
                                    "rationale": {
                                        "type": "string",
                                        "description": "Rationale for this ranking",
                                    },
                                },
                                "required": ["rank", "output_index", "rationale"],
                            },
                        },
                        "comparison_criteria": {
                            "type": "array",
                            "description": "Criteria used for comparison",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "criterion": {
                                        "type": "string",
                                        "description": "Name of comparison criterion",
                                    },
                                    "weights": {
                                        "type": "number",
                                        "description": "Weight of this criterion (0-1)",
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Description of how this criterion was applied",
                                    },
                                },
                                "required": ["criterion", "description"],
                            },
                        },
                        "recommended_output": {
                            "type": "integer",
                            "description": "Index of the recommended output (1-based)",
                        },
                        "analysis": {
                            "type": "string",
                            "description": "Detailed analysis of the comparison",
                        },
                    },
                    "required": ["rankings", "recommended_output", "analysis"],
                },
            },
        }

        # Add to history
        req_block = f"REQUIREMENTS:\n```\n{req_str}\n```\n\n" if req_str else ""
        self.add_to_history(
            {
                "role": "user",
                "content": (
                    f"Please compare the following outputs and rank them from best to worst:\n\n"
                    f"{outputs_str}\n"
                    f"{req_block}"
                    f"Provide a detailed comparison with rankings, scores, and analysis of each output."
                ),
            }
        )

        # Make API call with tool
        response = self._call_claude(messages=self.history, tools=[comparison_tool])

        # Extract comparison from tool calls if present
        comparison = {}
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call.function.name == "compare_outputs":
                    try:
                        comparison = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse comparison JSON: {e}")
                        comparison = {}

        # If no tool call, extract from response text
        if not comparison and response.content:
            # Create basic comparison from text
            comparison = {
                "analysis": response.content[0].text,
                "rankings": [],
                "recommended_output": None,
            }

            # Try to infer rankings from text
            try:
                text = response.content[0].text.lower()
                for i, output in enumerate(outputs, 1):
                    if f"output {i} is" in text and "best" in text:
                        comparison["recommended_output"] = i
                        break
            except Exception:
                pass

        return comparison
