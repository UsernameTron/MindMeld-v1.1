#!/usr/bin/env python3
"""
Model Manager for MindMeld Framework

This module provides utilities for managing LLM model dependencies,
checking availability, and handling model version compatibility.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_TIMEOUT = 10  # seconds
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODELS = ["phi3.5:latest"]
DEFAULT_RETRIES = 3
DEFAULT_RETRY_DELAY = 2  # seconds


class ModelManager:
    """Manager for LLM models used in MindMeld agents"""

    def __init__(
        self,
        ollama_host: Optional[str] = None,
        default_models: Optional[List[str]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRIES,
        retry_delay: int = DEFAULT_RETRY_DELAY,
    ):
        """
        Initialize the model manager

        Args:
            ollama_host: URL for Ollama API
            default_models: List of default models to ensure availability
            timeout: Timeout for API calls in seconds
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
        """
        self.ollama_host = ollama_host or os.environ.get(
            "OLLAMA_HOST", DEFAULT_OLLAMA_HOST
        )
        self.default_models = default_models or DEFAULT_MODELS
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.model_registry = {}  # Maps agent names to their required models

    def register_agent_model(self, agent_name: str, model_name: str) -> None:
        """
        Register which model an agent requires

        Args:
            agent_name: Name of the agent
            model_name: Name of the model required by the agent
        """
        self.model_registry[agent_name] = model_name
        logger.info(f"Registered model '{model_name}' for agent '{agent_name}'")

    def get_agent_model(self, agent_name: str) -> Optional[str]:
        """
        Get the model required by an agent

        Args:
            agent_name: Name of the agent

        Returns:
            The model name or None if not registered
        """
        return self.model_registry.get(agent_name)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from Ollama

        Returns:
            List of model information dictionaries
        """
        try:
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        f"{self.ollama_host}/api/tags", timeout=self.timeout
                    )
                    if response.status_code == 200:
                        return response.json().get("models", [])
                    logger.warning(
                        f"Failed to get models, status: {response.status_code}"
                    )
                except RequestException as e:
                    logger.warning(f"Request exception getting models: {e}")

                # Retry after delay if not last attempt
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

            return []
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            return []

    def check_model_availability(self, model_name: str) -> bool:
        """
        Check if a specific model is available

        Args:
            model_name: Name of the model to check

        Returns:
            True if the model is available, False otherwise
        """
        models = self.get_available_models()
        model_names = [m.get("name") for m in models]
        return model_name in model_names

    def ensure_model_available(self, model_name: str) -> Tuple[bool, Optional[str]]:
        """
        Ensure a model is available, pulling it if necessary

        Args:
            model_name: Name of the model to ensure

        Returns:
            Tuple of (success, error_message)
        """
        # First check if model is already available
        if self.check_model_availability(model_name):
            return True, None

        # If not, try to pull the model
        logger.info(f"Model '{model_name}' not found, attempting to pull")
        try:
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        f"{self.ollama_host}/api/pull",
                        json={"name": model_name},
                        timeout=600,  # Longer timeout for model pulling
                    )

                    if response.status_code == 200:
                        logger.info(f"Successfully pulled model '{model_name}'")
                        return True, None

                    error_msg = f"Failed to pull model '{model_name}': {response.text}"
                    logger.warning(error_msg)

                except RequestException as e:
                    error_msg = f"Request exception pulling model '{model_name}': {e}"
                    logger.warning(error_msg)

                # Retry after delay if not last attempt
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

            return False, error_msg

        except Exception as e:
            error_msg = f"Error pulling model '{model_name}': {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def ensure_default_models(self) -> Dict[str, bool]:
        """
        Ensure all default models are available

        Returns:
            Dictionary mapping model names to availability status
        """
        results = {}
        for model in self.default_models:
            success, _ = self.ensure_model_available(model)
            results[model] = success
        return results

    def get_models_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all default and registered models

        Returns:
            Dictionary mapping model names to their status information
        """
        models_to_check = set(self.default_models)
        for model in self.model_registry.values():
            models_to_check.add(model)

        status = {}
        available_models = self.get_available_models()
        model_details = {m.get("name"): m for m in available_models}

        for model_name in models_to_check:
            if model_name in model_details:
                status[model_name] = {
                    "available": True,
                    "details": model_details[model_name],
                }
            else:
                status[model_name] = {"available": False, "details": {}}

        return status


# Create a singleton instance for global use
model_manager = ModelManager()


def check_model_availability(model_name: str = "phi3.5:latest") -> bool:
    """
    Check if required model is available.

    Args:
        model_name: Name of the model to check

    Returns:
        True if the model is available, False otherwise
    """
    return model_manager.check_model_availability(model_name)


def ensure_model_available(
    model_name: str = "phi3.5:latest",
) -> Tuple[bool, Optional[str]]:
    """
    Ensure a model is available, pulling it if necessary.

    Args:
        model_name: Name of the model to ensure

    Returns:
        Tuple of (success, error_message)
    """
    return model_manager.ensure_model_available(model_name)
