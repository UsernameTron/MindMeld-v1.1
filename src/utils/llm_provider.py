import logging
import os
from enum import Enum
from typing import Any, Dict, Optional  # Removed unused List


class LLMProvider(Enum):
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    PERPLEXITY = "perplexity"
    GOOGLE = "google"


class LLMClient:
    def __init__(
        self,
        provider: LLMProvider,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs,
    ):
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.value.upper()}_API_KEY")
        self.model_name = model_name or os.getenv(f"{provider.value.upper()}_MODEL")
        self.kwargs = kwargs
        self.client = self._initialize_client()

    def _initialize_client(self):
        if self.provider == LLMProvider.OLLAMA:
            import ollama

            return ollama.Client(
                host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
            )
        elif self.provider == LLMProvider.ANTHROPIC:
            import anthropic

            return anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == LLMProvider.OPENAI:
            import openai

            return openai.OpenAI(api_key=self.api_key)
        elif self.provider == LLMProvider.PERPLEXITY:
            # Placeholder for Perplexity client
            if not self.api_key:
                raise RuntimeError(
                    "PERPLEXITY_API_KEY is required for Perplexity provider."
                )
            return None  # NotImplemented
        elif self.provider == LLMProvider.GOOGLE:
            import google.generativeai as genai

            if not self.api_key:
                raise RuntimeError("GOOGLE_API_KEY is required for Google provider.")
            genai.configure(api_key=self.api_key)
            # Use a supported Gemini model name for v1beta
            self.model_name = self.model_name or "gemini-2.0-flash"
            return genai.GenerativeModel(self.model_name)
        else:
            raise RuntimeError(f"Unsupported provider: {self.provider}")

    def chat(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        try:
            if self.provider == LLMProvider.OLLAMA:
                # OLLAMA expects a single prompt string
                prompt = "\n".join([m["content"] for m in messages])
                response = self.client.chat(
                    model=self.model_name or "phi3.5:latest",
                    messages=messages,
                    **kwargs,
                )
                return response["message"]["content"]
            elif self.provider == LLMProvider.ANTHROPIC:
                # Anthropic expects system, user, assistant roles
                pass

                system_prompt = next(
                    (m["content"] for m in messages if m["role"] == "system"), ""
                )
                user_content = "\n".join(
                    [m["content"] for m in messages if m["role"] == "user"]
                )
                response = self.client.messages.create(
                    model=self.model_name or "claude-3-opus-20240229",
                    system=system_prompt,
                    max_tokens=kwargs.get("max_tokens", 2048),
                    messages=[
                        {"role": m["role"], "content": m["content"]} for m in messages
                    ],
                )
                return response.content[0].text
            elif self.provider == LLMProvider.OPENAI:
                # OpenAI expects a list of dicts with role/content
                response = self.client.chat.completions.create(
                    model=self.model_name or "gpt-4-turbo",
                    messages=messages,
                    max_tokens=kwargs.get("max_tokens", 2048),
                )
                # Fix: Use attribute access for message content
                return response.choices[0].message.content
            elif self.provider == LLMProvider.PERPLEXITY:
                raise NotImplementedError("Perplexity provider is not yet implemented.")
            elif self.provider == LLMProvider.GOOGLE:
                # Convert messages to Gemini format
                # Google expects a specific format for chat messages
                gemini_messages = []

                for message in messages:
                    role = message.get("role", "user")
                    content = message.get("content", "")

                    if role == "system":
                        # For system messages, prepend to the first user message
                        # or add as a user message if none exists
                        continue

                    gemini_messages.append(
                        {
                            "role": "user" if role == "user" else "model",
                            "parts": [{"text": content}],
                        }
                    )

                # If no messages, return empty result
                if not gemini_messages:
                    return ""

                # Generate response
                response = self.client.generate_content(gemini_messages)
                return response.text
            else:
                raise RuntimeError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logging.error(f"LLMClient failed for {self.provider.value}: {e}")
            raise RuntimeError(f"LLMClient failed for {self.provider.value}: {e}")
