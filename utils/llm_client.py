"""
LLM client utility for MindMeld.

This module provides standardized LLM interaction with retry logic,
fallback models, and consistent error handling.
"""

import logging
import os
import time
from functools import wraps
from typing import Any, Dict, Optional

import requests
import tenacity
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from utils.error_handling import LLMCallError, ModelUnavailableError

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_MODEL = "phi3.5:latest"
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 1.5
DEFAULT_MAX_BACKOFF = 10
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TIMEOUT = 30  # seconds


def get_default_model() -> str:
    """
    Get the default LLM model from environment variables.

    Returns:
        Model name string
    """
    return os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)


def get_model_config() -> Dict[str, Any]:
    """
    Get the model configuration from environment variables.

    Returns:
        Model configuration dictionary
    """
    return {
        "temperature": float(os.getenv("TEMPERATURE", DEFAULT_TEMPERATURE)),
        "max_tokens": int(os.getenv("MAX_TOKENS", DEFAULT_MAX_TOKENS)),
        "timeout": int(os.getenv("TIMEOUT", DEFAULT_TIMEOUT)),
    }


def get_fallback_model() -> str:
    """
    Get the fallback LLM model from environment variables.

    Returns:
        Fallback model name string
    """
    return os.getenv("FALLBACK_MODEL", "llama2")


def call_llm_with_retry(
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    max_backoff: float = DEFAULT_MAX_BACKOFF,
):
    """
    Decorator to retry LLM calls with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor to multiply delay on each retry
        max_backoff: Maximum backoff time in seconds

    Returns:
        Decorated function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            @retry(
                stop=stop_after_attempt(max_retries),
                wait=wait_exponential(multiplier=backoff_factor, max=max_backoff),
                retry=retry_if_exception_type(
                    (LLMCallError, requests.exceptions.RequestException)
                ),
                reraise=True,
            )
            def _retry_call():
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, LLMCallError):
                        logger.warning(f"LLM call failed, retrying: {str(e)}")
                        raise
                    else:
                        logger.warning(f"Error in LLM call, retrying: {str(e)}")
                        raise LLMCallError(f"Error in LLM call: {str(e)}") from e

            try:
                return _retry_call()
            except tenacity.RetryError as e:
                if e.last_attempt.exception():
                    logger.error(
                        f"All retry attempts failed: {str(e.last_attempt.exception())}"
                    )
                    raise LLMCallError(
                        f"All retry attempts failed: {str(e.last_attempt.exception())}"
                    )
                else:
                    logger.error("All retry attempts failed")
                    raise LLMCallError("All retry attempts failed")

        return wrapper

    return decorator


def with_fallback_model(fallback_model: Optional[str] = None):
    """
    Decorator to try a fallback model if the primary model fails.

    Args:
        fallback_model: Name of the fallback model to use

    Returns:
        Decorated function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try with the primary model
            try:
                return func(*args, **kwargs)
            except LLMCallError as e:
                primary_model = kwargs.get("model_name") or get_default_model()
                fallback = fallback_model or get_fallback_model()

                if primary_model == fallback:
                    # Don't fallback to the same model
                    logger.error(
                        f"LLM call failed with model {primary_model}, no different fallback available"
                    )
                    raise

                logger.warning(
                    f"LLM call failed with model {primary_model}, trying fallback model {fallback}"
                )

                # Try with the fallback model
                kwargs["model_name"] = fallback
                try:
                    return func(*args, **kwargs)
                except Exception as fallback_e:
                    # Both primary and fallback failed
                    logger.error(
                        f"Fallback model {fallback} also failed: {str(fallback_e)}"
                    )
                    raise LLMCallError(
                        f"Both primary model ({primary_model}) and fallback model ({fallback}) failed",
                        model_name=primary_model,
                    ) from e

        return wrapper

    return decorator


def check_model_availability(model_name: str = None) -> bool:
    """
    Check if the specified model is available in Ollama.

    Args:
        model_name: Name of the model to check (default: get from environment)

    Returns:
        True if the model is available, False otherwise
    """
    if model_name is None:
        model_name = get_default_model()

    try:
        # Set up the Ollama API URL
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_host}/api/tags")

        if response.status_code == 200:
            models = response.json().get("models", [])
            # Check if the model is in the list of available models
            for model in models:
                if model.get("name") == model_name:
                    logger.debug(f"Model {model_name} is available")
                    return True

            logger.warning(f"Model {model_name} is not available in Ollama")
            return False
        else:
            logger.error(
                f"Failed to get model list from Ollama: {response.status_code}"
            )
            return False
    except Exception as e:
        logger.error(f"Error checking model availability: {str(e)}")
        return False


retry_on_llm_error = retry(
    retry=retry_if_exception_type((requests.RequestException, LLMCallError)),
    stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
    wait=wait_exponential(multiplier=DEFAULT_BACKOFF_FACTOR, max=DEFAULT_MAX_BACKOFF),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying LLM call after error (attempt {retry_state.attempt_number}/{DEFAULT_MAX_RETRIES})"
    ),
)


def with_fallback_model(func):
    """
    Decorator to retry with fallback model if primary model fails.

    Args:
        func: The function to decorate

    Returns:
        Wrapped function with fallback capability
    """

    @wraps(func)
    def wrapper(prompt, model_name=None, *args, **kwargs):
        try:
            return func(prompt, model_name, *args, **kwargs)
        except LLMCallError:
            # Try with fallback model if available
            fallback_model = get_fallback_model()
            if fallback_model and fallback_model != model_name:
                logger.warning(
                    f"Primary model failed, trying with fallback model {fallback_model}"
                )
                kwargs["fallback_used"] = True
                return func(prompt, fallback_model, *args, **kwargs)
            else:
                # Re-raise if no fallback or fallback is the same as primary
                raise

    return wrapper


@retry_on_llm_error
@with_fallback_model
def call_llm(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout: int = DEFAULT_TIMEOUT,
    system_prompt: Optional[str] = None,
    fallback_used: bool = False,
) -> Dict[str, Any]:
    """
    Call the LLM model with retry and fallback logic.

    Args:
        prompt: Input prompt for the model
        model_name: Name of the model to use (default: get from environment)
        temperature: Sampling temperature (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 2048)
        timeout: Request timeout in seconds (default: 30)
        system_prompt: Optional system prompt to use
        fallback_used: Whether this is a fallback call

    Returns:
        Dictionary containing the model response

    Raises:
        LLMCallError: If the model call fails
        ModelUnavailableError: If the model is not available
    """
    # Use default model if none specified
    if model_name is None:
        model_name = get_default_model()

    # Check if model is available
    if not check_model_availability(model_name):
        raise ModelUnavailableError(
            f"Model {model_name} is not available", model_name=model_name
        )

    try:
        # Set up the Ollama API URL and payload
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        url = f"{ollama_host}/api/generate"

        payload = {
            "model": model_name,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
        }

        if system_prompt:
            payload["system"] = system_prompt

        # Log request details (excluding the prompt for brevity)
        logger.debug(
            f"Calling model {model_name} with temperature={temperature}, max_tokens={max_tokens}"
        )

        # Record start time for runtime calculation
        start_time = time.time()

        # Make the API call
        response = requests.post(url, json=payload, timeout=timeout)

        # Calculate runtime
        runtime_seconds = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            # Add metadata to the response
            metadata = {
                "model_info": {
                    "name": model_name,
                },
                "runtime_seconds": runtime_seconds,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if fallback_used:
                metadata["fallback_used"] = True
                metadata["model_info"]["initial_model"] = get_default_model()

            result["metadata"] = metadata

            logger.debug(f"LLM call completed in {runtime_seconds:.2f} seconds")
            return result
        else:
            error_msg = f"LLM API call failed with status {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise LLMCallError(error_msg, model_name=model_name)

    except requests.RequestException as e:
        error_msg = f"LLM API request failed: {str(e)}"
        logger.error(error_msg)
        raise LLMCallError(error_msg, model_name=model_name) from e

    except Exception as e:
        error_msg = f"Unexpected error in LLM call: {str(e)}"
        logger.error(error_msg)
        raise LLMCallError(error_msg, model_name=model_name) from e


def extract_llm_response(response: Dict[str, Any]) -> str:
    """
    Extract the text from an LLM response.

    Args:
        response: Response dictionary from call_llm

    Returns:
        Response text
    """
    if "response" in response:
        return response["response"]
    elif "choices" in response and len(response["choices"]) > 0:
        return response["choices"][0]["text"]
    else:
        logger.warning("Could not extract response text from LLM response")
        return ""


def check_syntax(code_string: str, filename: str = "<string>") -> tuple:
    """
    Check Python code syntax without executing it.

    Args:
        code_string: Python code to check
        filename: Filename to use in error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        compile(code_string, filename, "exec")
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
