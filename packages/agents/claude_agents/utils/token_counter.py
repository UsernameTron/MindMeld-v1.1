from typing import Any, Dict, List

import tiktoken


class TokenCounter:
    """Utility class for more accurate token counting."""

    def __init__(self, model_name: str = "claude-3"):
        """
        Initialize the token counter.

        Args:
            model_name: Model name to use for tokenization.
                For Claude models, we use 'cl100k_base' tokenizer which is close to Claude's tokenization.
        """
        # Claude uses a tokenizer similar to GPT-4's cl100k_base
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.

        Args:
            text: Text to count tokens for

        Returns:
            Token count
        """
        return len(self.tokenizer.encode(text))

    def count_message_tokens(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count tokens in a message list for Claude API.

        Args:
            messages: List of message objects (user/assistant)

        Returns:
            Dictionary with prompt_tokens, likely_completion_tokens, and total
        """
        prompt_tokens = 0
        likely_completion_tokens = 0

        for message in messages:
            content = message.get("content", "")
            if isinstance(content, list):  # Handle content parts for multimodal
                text_content = ""
                for part in content:
                    if part.get("type") == "text":
                        text_content += part.get("text", "")
                content = text_content

            # Count tokens in the message
            token_count = self.count_tokens(content)

            # Add to appropriate counter
            if message.get("role") == "assistant":
                likely_completion_tokens += token_count
            else:
                prompt_tokens += token_count

        return {
            "prompt_tokens": prompt_tokens,
            "likely_completion_tokens": likely_completion_tokens,
            "total": prompt_tokens + likely_completion_tokens,
        }

    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "claude-3-opus-20240229",
    ) -> float:
        """
        Estimate the cost of an API call based on token counts.

        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            model: Model name

        Returns:
            Estimated cost in USD
        """
        # Pricing as of early 2024, may need updates
        prices = {
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

        # Default to opus if model not found
        model_prices = prices.get(model, prices["claude-3-opus-20240229"])

        # Calculate cost in USD
        input_cost = (prompt_tokens / 1_000_000) * model_prices["input"]
        output_cost = (completion_tokens / 1_000_000) * model_prices["output"]

        return input_cost + output_cost
