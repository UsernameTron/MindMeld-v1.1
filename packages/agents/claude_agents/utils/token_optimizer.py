import logging
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TokenOptimizer:
    """
    Utilities for optimizing token usage in Claude API calls.
    Implements prompt compression and response filtering strategies.
    """

    @staticmethod
    def compress_prompt(prompt: str, compression_level: str = "medium") -> str:
        """
        Compress a prompt to reduce token usage.

        Args:
            prompt: The prompt text to compress
            compression_level: Compression aggressiveness (low, medium, high)

        Returns:
            Compressed prompt
        """
        if not prompt:
            return prompt

        # Apply compression based on level
        if compression_level == "low":
            # Just remove unnecessary whitespace
            compressed = TokenOptimizer._remove_extra_whitespace(prompt)
        elif compression_level == "medium":
            # Remove whitespace and abbreviate common phrases
            compressed = TokenOptimizer._remove_extra_whitespace(prompt)
            compressed = TokenOptimizer._abbreviate_common_phrases(compressed)
        elif compression_level == "high":
            # Aggressive compression including structural changes
            compressed = TokenOptimizer._remove_extra_whitespace(prompt)
            compressed = TokenOptimizer._abbreviate_common_phrases(compressed)
            compressed = TokenOptimizer._condense_instructions(compressed)
        else:
            compressed = prompt

        # Log compression stats
        if prompt != compressed:
            orig_len = len(prompt)
            new_len = len(compressed)
            reduction = (orig_len - new_len) / orig_len * 100
            logger.debug(
                f"Compressed prompt from {orig_len} to {new_len} chars ({reduction:.1f}% reduction)"
            )

        return compressed

    @staticmethod
    def compress_messages(
        messages: List[Dict[str, Any]], compression_level: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Compress a list of message objects for the Claude API.

        Args:
            messages: List of message objects with role/content
            compression_level: Compression aggressiveness (low, medium, high)

        Returns:
            Compressed message list
        """
        compressed_messages = []

        for message in messages:
            # Only compress user messages (preserve assistant messages for context quality)
            if message.get("role") == "user":
                compressed_content = TokenOptimizer.compress_prompt(
                    message.get("content", ""), compression_level
                )
                compressed_message = {**message, "content": compressed_content}
                compressed_messages.append(compressed_message)
            else:
                compressed_messages.append(message)

        return compressed_messages

    @staticmethod
    def filter_response(response: str, filters: List[str] = None) -> str:
        """
        Filter unnecessary content from Claude's response.

        Args:
            response: Response text from Claude
            filters: Optional list of sections to filter (e.g., ["explanation", "thinking"])

        Returns:
            Filtered response
        """
        if not response:
            return response

        # Default filters if none provided
        if not filters:
            filters = ["thinking", "explanation", "reasoning"]

        # Find and remove thinking/explanation sections
        for filter_term in filters:
            # Match common "thinking" or "reasoning" sections with various formats
            pattern = rf"<{filter_term}>.*?</{filter_term}>"
            response = re.sub(pattern, "", response, flags=re.DOTALL | re.IGNORECASE)

            # Try other common formats
            pattern = rf"\*{filter_term}:?\*.*?(\n\n|\Z)"  # Markdown style
            response = re.sub(
                pattern, "\n\n", response, flags=re.DOTALL | re.IGNORECASE
            )

            pattern = rf"{filter_term}:.*?(\n\n|\Z)"  # Simple "thinking:" format
            response = re.sub(
                pattern, "\n\n", response, flags=re.DOTALL | re.IGNORECASE
            )

        # Remove multiple newlines
        response = re.sub(r"\n{3,}", "\n\n", response)

        return response.strip()

    @staticmethod
    def optimize_api_parameters(
        params: Dict[str, Any], budget_tier: str = "standard"
    ) -> Dict[str, Any]:
        """
        Optimize Claude API parameters for cost efficiency.

        Args:
            params: Claude API parameters
            budget_tier: Cost optimization tier (economy, standard, premium)

        Returns:
            Optimized parameters
        """
        # Make a copy to avoid modifying the original
        optimized = params.copy()

        # Apply optimizations based on budget tier
        if budget_tier == "economy":
            # Maximum cost savings for budget-constrained scenarios
            optimized["max_tokens"] = min(optimized.get("max_tokens", 4096), 1024)
            optimized["temperature"] = (
                0.3  # Lower temp for more deterministic (and often shorter) responses
            )

            # Compress prompts if present
            if "messages" in optimized:
                optimized["messages"] = TokenOptimizer.compress_messages(
                    optimized["messages"], compression_level="high"
                )

            if "system" in optimized:
                optimized["system"] = TokenOptimizer.compress_prompt(
                    optimized["system"], compression_level="high"
                )

        elif budget_tier == "standard":
            # Balanced cost optimization
            optimized["max_tokens"] = min(optimized.get("max_tokens", 4096), 2048)

            # Only compress prompts if messages are present
            if "messages" in optimized:
                optimized["messages"] = TokenOptimizer.compress_messages(
                    optimized["messages"], compression_level="medium"
                )

            if "system" in optimized:
                optimized["system"] = TokenOptimizer.compress_prompt(
                    optimized["system"], compression_level="medium"
                )

        elif budget_tier == "premium":
            # Minimal optimization for high-quality scenarios
            # Just ensure token limits are reasonable
            optimized["max_tokens"] = min(optimized.get("max_tokens", 4096), 4096)

            if "messages" in optimized:
                optimized["messages"] = TokenOptimizer.compress_messages(
                    optimized["messages"], compression_level="low"
                )

        return optimized

    @staticmethod
    def estimate_monthly_cost(
        avg_prompt_tokens: int,
        avg_completion_tokens: int,
        requests_per_day: int,
        model: str = "claude-3-opus-20240229",
    ) -> Dict[str, Any]:
        """
        Estimate monthly API costs based on usage patterns.

        Args:
            avg_prompt_tokens: Average tokens per prompt
            avg_completion_tokens: Average tokens per completion
            requests_per_day: Average number of API requests per day
            model: Claude model name

        Returns:
            Dictionary with cost estimates
        """
        # Model pricing (per million tokens as of March 2024)
        model_pricing = {
            "claude-3-opus-20240229": {
                "input": 15.0,
                "output": 75.0,
            },  # $15/$75 per million tokens
            "claude-3-sonnet-20240229": {
                "input": 3.0,
                "output": 15.0,
            },  # $3/$15 per million tokens
            "claude-3-haiku-20240307": {
                "input": 0.25,
                "output": 1.25,
            },  # $0.25/$1.25 per million tokens
            "claude-2.1": {"input": 8.0, "output": 24.0},  # $8/$24 per million tokens
            "claude-2.0": {"input": 8.0, "output": 24.0},  # $8/$24 per million tokens
        }

        # Get pricing for selected model (default to Opus if not found)
        pricing = model_pricing.get(model, model_pricing["claude-3-opus-20240229"])

        # Calculate monthly usage
        days_per_month = 30.44  # Average days per month
        monthly_requests = requests_per_day * days_per_month
        monthly_prompt_tokens = avg_prompt_tokens * monthly_requests
        monthly_completion_tokens = avg_completion_tokens * monthly_requests

        # Calculate costs
        prompt_cost = (monthly_prompt_tokens / 1_000_000) * pricing["input"]
        completion_cost = (monthly_completion_tokens / 1_000_000) * pricing["output"]
        total_cost = prompt_cost + completion_cost

        # Create result
        return {
            "model": model,
            "monthly_requests": monthly_requests,
            "monthly_prompt_tokens": monthly_prompt_tokens,
            "monthly_completion_tokens": monthly_completion_tokens,
            "prompt_cost": prompt_cost,
            "completion_cost": completion_cost,
            "total_cost": total_cost,
            "within_budget": total_cost <= 500,  # Check against $500 budget
        }

    @staticmethod
    def optimize_for_budget(
        avg_prompt_tokens: int,
        avg_completion_tokens: int,
        requests_per_day: int,
        target_budget: float = 500.0,
        models: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Find optimal configuration to stay within budget.

        Args:
            avg_prompt_tokens: Average tokens per prompt
            avg_completion_tokens: Average tokens per completion
            requests_per_day: Average number of API requests per day
            target_budget: Monthly budget in USD
            models: List of models to consider

        Returns:
            Optimization recommendations
        """
        if not models:
            models = [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ]

        # Try different models and compression levels
        scenarios = []
        compression_levels = ["low", "medium", "high"]

        for model in models:
            for compression in compression_levels:
                # Calculate token reduction based on compression level
                token_reduction = {
                    "low": 0.10,  # 10% reduction
                    "medium": 0.25,  # 25% reduction
                    "high": 0.40,  # 40% reduction
                }

                # Apply compression to tokens
                compressed_prompt_tokens = int(
                    avg_prompt_tokens * (1 - token_reduction[compression])
                )

                # Calculate cost
                cost_estimate = TokenOptimizer.estimate_monthly_cost(
                    compressed_prompt_tokens,
                    avg_completion_tokens,
                    requests_per_day,
                    model,
                )

                # Add scenario
                scenarios.append(
                    {
                        "model": model,
                        "compression_level": compression,
                        "monthly_cost": cost_estimate["total_cost"],
                        "within_budget": cost_estimate["total_cost"] <= target_budget,
                        "prompt_tokens": compressed_prompt_tokens,
                        "completion_tokens": avg_completion_tokens,
                        "token_reduction": f"{token_reduction[compression]*100:.0f}%",
                        "details": cost_estimate,
                    }
                )

        # Sort by cost
        scenarios.sort(key=lambda x: x["monthly_cost"])

        # Find cheapest that's within budget
        viable_options = [s for s in scenarios if s["within_budget"]]

        if viable_options:
            recommended = viable_options[0]
            for option in viable_options:
                if "opus" in option["model"]:
                    # Prefer opus with highest possible compression that fits budget
                    recommended = option
                    break
        else:
            # If nothing fits budget, recommend cheapest option
            recommended = scenarios[0]

        # Generate recommendations
        return {
            "original_monthly_cost": TokenOptimizer.estimate_monthly_cost(
                avg_prompt_tokens,
                avg_completion_tokens,
                requests_per_day,
                "claude-3-opus-20240229",
            )["total_cost"],
            "target_budget": target_budget,
            "scenarios": scenarios,
            "recommended": recommended,
            "optimization_needed": recommended["monthly_cost"] > target_budget,
            "suggestions": TokenOptimizer._generate_optimization_suggestions(
                recommended, target_budget
            ),
        }

    # Helper methods

    @staticmethod
    def _remove_extra_whitespace(text: str) -> str:
        """Remove unnecessary whitespace from text."""
        # Replace multiple spaces with a single space
        text = re.sub(r" {2,}", " ", text)

        # Replace multiple newlines with at most two
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Trim leading/trailing whitespace from lines
        lines = text.split("\n")
        lines = [line.strip() for line in lines]
        text = "\n".join(lines)

        return text.strip()

    @staticmethod
    def _abbreviate_common_phrases(text: str) -> str:
        """Replace common phrases with shorter equivalents."""
        replacements = {
            "for example": "e.g.",
            "that is to say": "i.e.",
            "in other words": "i.e.",
            "please note that": "note:",
            "it is important to": "importantly,",
            "it is recommended to": "recommend:",
            "in order to": "to",
            "as well as": "&",
            "with respect to": "re:",
            "with regard to": "re:",
        }

        for phrase, replacement in replacements.items():
            text = re.sub(
                r"\b" + re.escape(phrase) + r"\b",
                replacement,
                text,
                flags=re.IGNORECASE,
            )

        return text

    @staticmethod
    def _condense_instructions(text: str) -> str:
        """Condense verbose instructions into more compact form."""
        # Convert bullet lists with redundant prefixes
        redundant_prefixes = [
            r"Please ensure that you",
            r"Make sure to",
            r"You should",
            r"It is necessary to",
        ]

        for prefix in redundant_prefixes:
            pattern = rf"- {prefix} (.*?)(?=\n|$)"
            text = re.sub(pattern, r"- \1", text, flags=re.IGNORECASE)

        # Convert redundant instruction patterns
        patterns = [
            (r"I would like you to", ""),
            (r"Your task is to", ""),
            (r"I need you to", ""),
            (r"Please provide", "Provide"),
            (r"Please generate", "Generate"),
            (r"Please create", "Create"),
            (r"Please implement", "Implement"),
            (r"Please write", "Write"),
        ]

        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def _generate_optimization_suggestions(
        recommendation: Dict[str, Any], target_budget: float
    ) -> List[str]:
        """Generate textual suggestions for optimization."""
        suggestions = []

        if recommendation["monthly_cost"] > target_budget:
            # Budget exceeded, provide aggressive optimization suggestions
            suggestions.append(
                f"Switch to {recommendation['model']} with {recommendation['compression_level']} compression"
            )
            suggestions.append("Implement response caching for common queries")
            suggestions.append(
                "Reduce max_tokens limit further and implement chunking for long outputs"
            )
            suggestions.append(
                "Consider reducing daily request volume or batching similar requests"
            )
        else:
            # Within budget, provide balancing suggestions
            headroom = target_budget - recommendation["monthly_cost"]
            headroom_percentage = (headroom / target_budget) * 100

            if headroom_percentage < 10:
                # Very tight margin
                suggestions.append(
                    "Current configuration fits within budget but with minimal margin"
                )
                suggestions.append(
                    "Implement usage monitoring to avoid unexpected overages"
                )
            elif "haiku" in recommendation["model"] and headroom_percentage > 30:
                # Could potentially upgrade model
                suggestions.append(
                    "Consider upgrading to claude-3-sonnet for improved quality while staying within budget"
                )
            elif "sonnet" in recommendation["model"] and headroom_percentage > 50:
                # Could potentially upgrade model
                suggestions.append(
                    "Consider upgrading to claude-3-opus for critical reasoning tasks while staying within budget"
                )

            if (
                recommendation["compression_level"] == "high"
                and headroom_percentage > 20
            ):
                suggestions.append(
                    "Could reduce compression level to improve prompt quality while staying within budget"
                )

        # Add general efficiency suggestions
        suggestions.append("Implement dynamic model selection based on task complexity")
        suggestions.append("Use token-counting to avoid unnecessary context in prompts")

        return suggestions
