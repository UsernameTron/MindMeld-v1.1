# filepath: /packages/agents/implementations/critic.py
"""
CriticAgent - Standardized quality evaluation agent
Migrated from claude_agents.agents.critic to use the unified agent protocol
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from ..base.protocols import AgentProtocol
from ..base.registry import AgentRegistry

logger = logging.getLogger(__name__)


class CriticAgent(AgentProtocol):
    """
    Agent responsible for evaluating outputs, finding errors, and suggesting improvements.
    Acts as the quality control component of the multi-agent system.

    Capabilities:
    - Output quality evaluation with scoring
    - Error detection and categorization
    - Improvement suggestions generation
    - Multi-output comparison and ranking
    - Requirements compliance checking
    - Structured feedback provision
    """

    def __init__(
        self,
        api_client: Optional[Any] = None,
        name: str = "CriticAgent",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        """
        Initialize the critic agent.

        Args:
            api_client: Claude API client instance (optional for standardized interface)
            name: Agent name
            temperature: Temperature for responses (lower for more consistent evaluation)
            max_tokens: Maximum tokens in the response
        """
        self.name = name
        self.api_client = api_client
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Evaluation history for tracking patterns
        self.evaluation_history: List[Dict[str, Any]] = []

        # Auto-register with the agent registry
        registry = AgentRegistry.get_instance()
        registry.register_agent(
            self.name, lambda **kwargs: CriticAgent(**kwargs), self.get_capabilities()
        )
        logger.info(f"Registered {self.name} with AgentRegistry")

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and metadata."""
        return {
            "name": self.name,
            "type": "critic",
            "description": "Evaluates outputs, finds errors, and suggests improvements",
            "capabilities": [
                "quality_evaluation",
                "error_detection",
                "improvement_suggestions",
                "multi_output_comparison",
                "requirements_checking",
                "structured_feedback",
                "scoring_and_ranking",
            ],
            "input_types": ["output", "comparison_request", "evaluation_request"],
            "output_types": ["evaluation", "comparison", "feedback"],
            "evaluation_criteria": [
                "correctness",
                "completeness",
                "quality",
                "clarity",
                "efficiency",
                "maintainability",
            ],
        }

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data for evaluation.

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check for evaluation request
            if "evaluate" in data:
                eval_data = data["evaluate"]
                if "output" not in eval_data:
                    logger.error("Evaluation request must include 'output'")
                    return False

            # Check for comparison request
            elif "compare" in data:
                comp_data = data["compare"]
                if "outputs" not in comp_data:
                    logger.error("Comparison request must include 'outputs'")
                    return False
                if not isinstance(comp_data["outputs"], list):
                    logger.error("Outputs for comparison must be a list")
                    return False
                if len(comp_data["outputs"]) < 2:
                    logger.error("Need at least 2 outputs for comparison")
                    return False

            # Check for direct outputs comparison (legacy support)
            elif "outputs" in data:
                if not isinstance(data["outputs"], list):
                    logger.error("Outputs for comparison must be a list")
                    return False
                if len(data["outputs"]) < 2:
                    logger.error("Need at least 2 outputs for comparison")
                    return False

            # Check for direct output evaluation (legacy support)
            elif "output" in data:
                # Direct output evaluation - validate output is not empty
                output_value = data["output"]
                if output_value is None:
                    logger.error("Output value cannot be None")
                    return False
                if isinstance(output_value, str) and output_value.strip() == "":
                    logger.error("Output value cannot be empty string")
                    return False

            else:
                logger.error(
                    "Input must contain 'evaluate', 'compare', 'outputs', or 'output'"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"Input validation error: {str(e)}")
            return False

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process evaluation request and return analysis.

        Args:
            data: Input data containing output(s) to evaluate or compare

        Returns:
            Evaluation results with scores, issues, and suggestions
        """
        if not self.validate_input(data):
            return {
                "status": "error",
                "error": "Invalid input data",
                "agent": self.name,
            }

        try:
            # Determine evaluation type and process accordingly
            if "evaluate" in data:
                eval_data = data["evaluate"]
                output = eval_data["output"]
                requirements = eval_data.get("requirements")
                return self._evaluate_output(output, requirements)

            elif "compare" in data:
                comp_data = data["compare"]
                outputs = comp_data["outputs"]
                requirements = comp_data.get("requirements")
                return self._compare_outputs(outputs, requirements)

            elif "outputs" in data:
                # Legacy direct comparison
                outputs = data["outputs"]
                requirements = data.get("requirements")
                return self._compare_outputs(outputs, requirements)

            elif "output" in data:
                # Legacy direct evaluation
                output = data["output"]
                requirements = data.get("requirements")
                return self._evaluate_output(output, requirements)

            else:
                return {
                    "status": "error",
                    "error": "No valid evaluation target found",
                    "agent": self.name,
                }

        except Exception as e:
            logger.error(f"Evaluation error in {self.name}: {str(e)}")
            return {"status": "error", "error": str(e), "agent": self.name}

    def _evaluate_output(
        self, output: Any, requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a single output against requirements and provide feedback.

        Args:
            output: The output to evaluate (text, code, or structured data)
            requirements: Optional requirements to evaluate against

        Returns:
            Evaluation results with scores and feedback
        """
        evaluation_id = f"eval_{len(self.evaluation_history)}"

        # Format output for analysis
        output_str = self._format_output_for_analysis(output)

        # Prepare evaluation structure
        evaluation = {
            "evaluation_id": evaluation_id,
            "status": "completed",
            "agent": self.name,
            "quality_score": None,
            "correctness_score": None,
            "completeness_score": None,
            "clarity_score": None,
            "issues": [],
            "errors": [],  # Add errors field for test compatibility
            "strengths": [],
            "improvement_suggestions": [],
            "meets_requirements": None,
            "overall_feedback": "",
        }

        # If API client is available, use it for sophisticated evaluation
        if self.api_client:
            try:
                evaluation = self._api_evaluate_output(
                    output_str, requirements, evaluation
                )
            except Exception as e:
                logger.error(f"API evaluation error: {str(e)}")
                evaluation.update({"status": "error", "error": str(e)})
        else:
            # Fallback evaluation without API
            evaluation = self._fallback_evaluate_output(
                output_str, requirements, evaluation
            )

        # Record evaluation in history
        self.evaluation_history.append(
            {
                "type": "evaluation",
                "input": {"output": output, "requirements": requirements},
                "result": evaluation,
                "timestamp": self._get_timestamp(),
            }
        )

        return evaluation

    def _compare_outputs(
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
        comparison_id = f"comp_{len(self.evaluation_history)}"

        # Format outputs for analysis
        formatted_outputs = [
            self._format_output_for_analysis(output) for output in outputs
        ]

        # Prepare comparison structure
        comparison = {
            "comparison_id": comparison_id,
            "status": "completed",
            "agent": self.name,
            "num_outputs": len(outputs),
            "rankings": [],
            "comparison_criteria": [],
            "recommended_output": None,
            "analysis": "",
        }

        # If API client is available, use it for sophisticated comparison
        if self.api_client:
            try:
                comparison = self._api_compare_outputs(
                    formatted_outputs, requirements, comparison
                )
            except Exception as e:
                logger.error(f"API comparison error: {str(e)}")
                comparison.update({"status": "error", "error": str(e)})
        else:
            # Fallback comparison without API
            comparison = self._fallback_compare_outputs(
                formatted_outputs, requirements, comparison
            )

        # Ensure compatibility with test expectations - add 'ranking' alias for 'rankings'
        if "rankings" in comparison and "ranking" not in comparison:
            comparison["ranking"] = comparison["rankings"]

        # Record comparison in history
        self.evaluation_history.append(
            {
                "type": "comparison",
                "input": {"outputs": outputs, "requirements": requirements},
                "result": comparison,
                "timestamp": self._get_timestamp(),
            }
        )

        return comparison

    def _api_evaluate_output(
        self,
        output_str: str,
        requirements: Optional[Dict[str, Any]],
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Use API client for sophisticated output evaluation.

        Args:
            output_str: Formatted output string
            requirements: Optional requirements
            evaluation: Base evaluation structure

        Returns:
            Enhanced evaluation with API analysis
        """
        # Define evaluation tool for structured feedback
        evaluation_tool = {
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
                        "clarity_score": {
                            "type": "number",
                            "description": "Clarity score (0-10, where 10 is perfectly clear)",
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

        # Format requirements if present
        req_str = ""
        if requirements:
            req_str = self._format_requirements(requirements)

        req_block = f"REQUIREMENTS:\n```\n{req_str}\n```\n\n" if req_str else ""

        # Prepare prompt
        prompt = (
            f"Please evaluate the following output:\n\n"
            f"OUTPUT:\n```\n{output_str}\n```\n\n"
            f"{req_block}"
            f"Provide a detailed evaluation identifying issues, strengths, and suggestions for improvement."
        )

        # Make API call (placeholder - would use actual API client)
        response = self._call_api(prompt, [evaluation_tool])

        # Extract evaluation from response
        api_evaluation = self._extract_structured_response(response, "evaluate_output")

        if api_evaluation:
            evaluation.update(api_evaluation)
        else:
            # Fallback to text-based extraction
            evaluation = self._extract_evaluation_from_text(response, evaluation)

        return evaluation

    def _api_compare_outputs(
        self,
        formatted_outputs: List[str],
        requirements: Optional[Dict[str, Any]],
        comparison: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Use API client for sophisticated output comparison.

        Args:
            formatted_outputs: List of formatted output strings
            requirements: Optional requirements
            comparison: Base comparison structure

        Returns:
            Enhanced comparison with API analysis
        """
        # Format outputs for prompt
        outputs_str = ""
        for i, output in enumerate(formatted_outputs, 1):
            outputs_str += f"OUTPUT {i}:\n```\n{output}\n```\n\n"

        # Format requirements if present
        req_str = ""
        if requirements:
            req_str = self._format_requirements(requirements)

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
                                    "weight": {
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

        # Prepare prompt
        req_block = f"REQUIREMENTS:\n```\n{req_str}\n```\n\n" if req_str else ""
        prompt = (
            f"Please compare the following outputs and rank them from best to worst:\n\n"
            f"{outputs_str}\n"
            f"{req_block}"
            f"Provide a detailed comparison with rankings, scores, and analysis of each output."
        )

        # Make API call (placeholder - would use actual API client)
        response = self._call_api(prompt, [comparison_tool])

        # Extract comparison from response
        api_comparison = self._extract_structured_response(response, "compare_outputs")

        if api_comparison:
            comparison.update(api_comparison)
        else:
            # Fallback to text-based extraction
            comparison = self._extract_comparison_from_text(response, comparison)

        return comparison

    def _fallback_evaluate_output(
        self,
        output_str: str,
        requirements: Optional[Dict[str, Any]],
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Fallback evaluation without API client.

        Args:
            output_str: Formatted output string
            requirements: Optional requirements
            evaluation: Base evaluation structure

        Returns:
            Basic evaluation with heuristic analysis
        """
        # Basic heuristic evaluation
        issues = []
        errors = []  # Specific error detection for tests
        strengths = []
        suggestions = []

        # Length analysis
        if len(output_str.strip()) == 0:
            error_item = {"severity": "critical", "description": "Output is empty"}
            issues.append(error_item)
            errors.append(error_item)
        elif len(output_str) < 10:
            issue_item = {"severity": "minor", "description": "Output seems very short"}
            issues.append(issue_item)
        else:
            strengths.append("Output has substantial content")

        # Error detection - look for common syntax/logical errors
        if "=" in output_str and "if" in output_str:
            # Check for assignment in if statements (should be ==)
            lines = output_str.split("\n")
            for i, line in enumerate(lines, 1):
                if "if" in line and " = " in line and " == " not in line:
                    error_item = {
                        "severity": "critical",
                        "description": f"Syntax error: assignment (=) used instead of equality (==) in conditional at line {i}",
                        "location": f"line {i}",
                    }
                    issues.append(error_item)
                    errors.append(error_item)

        # Basic structure analysis
        if output_str.count("\n") > 5:
            strengths.append("Output is well-structured with multiple lines")

        # Code detection
        if "```" in output_str or any(
            keyword in output_str.lower()
            for keyword in ["def ", "class ", "function", "import"]
        ):
            strengths.append("Contains code or structured content")

        # Requirements checking
        meets_requirements = True
        if requirements:
            req_str = self._format_requirements(requirements)
            # Simple keyword matching
            for word in req_str.lower().split():
                if len(word) > 3 and word not in output_str.lower():
                    meets_requirements = False
                    suggestions.append(
                        {
                            "area": "requirements",
                            "suggestion": f"Consider addressing '{word}' mentioned in requirements",
                        }
                    )

        # Calculate basic scores
        quality_score = 8.0 if not issues else max(3.0, 8.0 - len(issues) * 2)
        correctness_score = 7.0 if meets_requirements else 5.0
        completeness_score = 6.0 if len(output_str) > 100 else 4.0
        clarity_score = 7.0 if output_str.count("\n") > 2 else 5.0

        evaluation.update(
            {
                "quality_score": quality_score,
                "correctness_score": correctness_score,
                "completeness_score": completeness_score,
                "clarity_score": clarity_score,
                "issues": issues,
                "errors": errors,  # Include errors field for test compatibility
                "strengths": strengths,
                "improvement_suggestions": suggestions,
                "meets_requirements": meets_requirements,
                "overall_feedback": f"Basic evaluation completed. Quality score: {quality_score}/10. {'Meets requirements.' if meets_requirements else 'May not fully meet requirements.'}",
            }
        )

        return evaluation

    def _fallback_compare_outputs(
        self,
        formatted_outputs: List[str],
        requirements: Optional[Dict[str, Any]],
        comparison: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Fallback comparison without API client.

        Args:
            formatted_outputs: List of formatted output strings
            requirements: Optional requirements
            comparison: Base comparison structure

        Returns:
            Basic comparison with heuristic ranking
        """
        # Basic heuristic comparison
        rankings = []

        for i, output in enumerate(formatted_outputs, 1):
            # Simple scoring based on length and structure
            score = 5.0  # Base score

            # Length bonus
            if len(output) > 100:
                score += 1.0
            if len(output) > 500:
                score += 1.0

            # Structure bonus
            if output.count("\n") > 5:
                score += 0.5
            if "```" in output:
                score += 0.5

            rankings.append(
                {
                    "rank": i,  # Will be sorted later
                    "output_index": i,
                    "score": min(10.0, score),
                    "rationale": f"Basic heuristic scoring based on length ({len(output)} chars) and structure",
                }
            )

        # Sort by score (descending)
        rankings.sort(key=lambda x: x["score"], reverse=True)

        # Update ranks
        for i, ranking in enumerate(rankings, 1):
            ranking["rank"] = i

        comparison.update(
            {
                "rankings": rankings,
                "comparison_criteria": [
                    {
                        "criterion": "length",
                        "weight": 0.4,
                        "description": "Longer outputs generally scored higher",
                    },
                    {
                        "criterion": "structure",
                        "weight": 0.3,
                        "description": "Well-structured outputs with line breaks scored higher",
                    },
                    {
                        "criterion": "code_presence",
                        "weight": 0.3,
                        "description": "Outputs containing code blocks scored higher",
                    },
                ],
                "recommended_output": rankings[0]["output_index"] if rankings else 1,
                "analysis": f"Basic heuristic comparison of {len(formatted_outputs)} outputs. Ranking based on length, structure, and code presence.",
            }
        )

        # Ensure compatibility with test expectations - add 'ranking' alias for 'rankings'
        if "rankings" in comparison and "ranking" not in comparison:
            comparison["ranking"] = comparison["rankings"]

        return comparison

    def _format_output_for_analysis(self, output: Any) -> str:
        """
        Format output for analysis.

        Args:
            output: Output to format

        Returns:
            Formatted output string
        """
        if isinstance(output, str):
            return output
        elif isinstance(output, (int, float, bool)):
            return str(output)
        else:
            try:
                return json.dumps(output, indent=2)
            except:
                return str(output)

    def _format_requirements(self, requirements: Dict[str, Any]) -> str:
        """
        Format requirements for analysis.

        Args:
            requirements: Requirements to format

        Returns:
            Formatted requirements string
        """
        if isinstance(requirements, str):
            return requirements
        else:
            try:
                return json.dumps(requirements, indent=2)
            except:
                return str(requirements)

    def _call_api(
        self, prompt: str, tools: Optional[List[Dict[str, Any]]] = None
    ) -> Any:
        """
        Make API call if client is available.

        Args:
            prompt: Prompt to send to API
            tools: Optional tools for API call

        Returns:
            API response
        """
        if not self.api_client:
            raise ValueError("API client not available")

        # This would be implemented based on the specific API client interface
        # For now, we'll use a placeholder
        return {"content": [{"text": f"Evaluated: {prompt[:100]}..."}]}

    def _extract_structured_response(
        self, response: Any, tool_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract structured response from API tool calls.

        Args:
            response: API response
            tool_name: Name of the tool to extract

        Returns:
            Extracted structured data or None
        """
        try:
            if hasattr(response, "tool_calls") and response.tool_calls:
                for tool_call in response.tool_calls:
                    if tool_call.function.name == tool_name:
                        return json.loads(tool_call.function.arguments)
        except Exception as e:
            logger.error(f"Error extracting structured response: {str(e)}")

        return None

    def _extract_evaluation_from_text(
        self, response: Any, evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract evaluation from text response.

        Args:
            response: API response
            evaluation: Base evaluation structure

        Returns:
            Updated evaluation
        """
        if hasattr(response, "content") and response.content:
            content = response.content[0].text

            # Try to find JSON block
            json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
            if json_match:
                try:
                    extracted = json.loads(json_match.group(1))
                    evaluation.update(extracted)
                    return evaluation
                except json.JSONDecodeError:
                    pass

            # Fallback to text analysis
            evaluation["overall_feedback"] = content

            # Try to extract scores from text
            score_patterns = [
                (r"quality[:\s]*(\d+(?:\.\d+)?)", "quality_score"),
                (r"correctness[:\s]*(\d+(?:\.\d+)?)", "correctness_score"),
                (r"completeness[:\s]*(\d+(?:\.\d+)?)", "completeness_score"),
            ]

            for pattern, key in score_patterns:
                match = re.search(pattern, content.lower())
                if match:
                    try:
                        evaluation[key] = float(match.group(1))
                    except ValueError:
                        pass

        return evaluation

    def _extract_comparison_from_text(
        self, response: Any, comparison: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract comparison from text response.

        Args:
            response: API response
            comparison: Base comparison structure

        Returns:
            Updated comparison
        """
        if hasattr(response, "content") and response.content:
            content = response.content[0].text
            comparison["analysis"] = content

            # Try to infer rankings from text
            rankings = []
            for i in range(1, comparison["num_outputs"] + 1):
                if f"output {i}" in content.lower():
                    rankings.append(
                        {
                            "rank": i,
                            "output_index": i,
                            "score": 5.0,
                            "rationale": f"Mentioned in analysis",
                        }
                    )

            if rankings:
                comparison["rankings"] = rankings
                comparison["recommended_output"] = rankings[0]["output_index"]

        return comparison

    def _get_timestamp(self) -> str:
        """Get current timestamp for history tracking."""
        import datetime

        return datetime.datetime.now().isoformat()

    def get_evaluation_history(self) -> List[Dict[str, Any]]:
        """
        Get evaluation history for analysis.

        Returns:
            List of evaluation records
        """
        return self.evaluation_history.copy()

    def clear_evaluation_history(self) -> None:
        """Clear evaluation history."""
        self.evaluation_history.clear()
        logger.info(f"Cleared evaluation history for {self.name}")

    def get_evaluation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about evaluations performed.

        Returns:
            Statistics about evaluations
        """
        total_evaluations = len(
            [h for h in self.evaluation_history if h["type"] == "evaluation"]
        )
        total_comparisons = len(
            [h for h in self.evaluation_history if h["type"] == "comparison"]
        )

        # Calculate average scores from evaluations
        quality_scores = []
        for history in self.evaluation_history:
            if history["type"] == "evaluation" and history["result"].get(
                "quality_score"
            ):
                quality_scores.append(history["result"]["quality_score"])

        avg_quality = (
            sum(quality_scores) / len(quality_scores) if quality_scores else None
        )

        return {
            "total_evaluations": total_evaluations,
            "total_comparisons": total_comparisons,
            "average_quality_score": avg_quality,
            "evaluations_with_api": sum(
                1
                for h in self.evaluation_history
                if h["result"].get("status") == "completed"
            ),
            "evaluation_errors": sum(
                1
                for h in self.evaluation_history
                if h["result"].get("status") == "error"
            ),
        }
