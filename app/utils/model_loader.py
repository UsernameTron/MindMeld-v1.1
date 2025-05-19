"""Model loader utilities for the MindMeld application.

This module provides functions to load Hugging Face models and run inference
with standardized error handling.
"""

from typing import Any, Callable

from app.core.config import settings
from app.services.errors import InferenceError, ModelLoadError
from transformers import pipeline


def load_model(
    task: str = "sentiment-analysis",
    model_name: str | None = None,
    device: str | None = None,
) -> Callable[[str], Any]:
    """
    Load a Hugging Face model pipeline for a specific task.

    Args:
        task (str): The pipeline task (e.g., 'sentiment-analysis').
        model_name (str | None): The model name or path. Defaults to the app's default model.
        device (str | None): The device to use ('cpu' or 'mps'). Defaults to the app's inference device.

    Returns:
        Callable[[str], Any]: A Hugging Face pipeline function.

    Raises:
        ModelLoadError: If model loading fails.
    """
    model_name = model_name or settings.DEFAULT_MODEL_NAME
    device = device or settings.INFERENCE_DEVICE
    try:
        device_id = 0 if device == "mps" else -1
        return pipeline(task=task, model=model_name, device=device_id)
    except Exception as e:
        raise ModelLoadError(f"Failed to load model: {str(e)}", model_name)


def run_inference(pipeline_fn: Callable[[str], Any], text: str) -> Any:
    """
    Run inference using a Hugging Face pipeline with error handling.

    Args:
        pipeline_fn (Callable[[str], Any]): The Hugging Face pipeline function.
        text (str): The input text for inference.

    Returns:
        Any: The inference result.

    Raises:
        InferenceError: If inference fails.
    """
    try:
        return pipeline_fn(text)
    except Exception as e:
        raise InferenceError(f"Failed to run inference: {str(e)}")
