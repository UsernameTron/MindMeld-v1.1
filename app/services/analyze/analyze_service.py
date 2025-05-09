"""
Analyze service module for sentiment analysis and text processing.

This module provides services for analyzing text sentiment, extracting key phrases,
and processing text content using machine learning models.
"""

import re
import uuid
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, ClassVar, Dict, List, Optional

from transformers import pipeline
from opentelemetry import trace

from app.core.config import settings
from app.models.analyze.analyze import (
    BatchSentimentRequest,
    BatchSentimentResponse,
    KeyPhrase,
    SentimentRequest,
    SentimentResponse,
)
from app.services.errors import InferenceError, ValidationError

tracer = trace.get_tracer(__name__)

class AnalyzeService:
    """
    Service for text analysis operations.

    Provides sentiment analysis and text processing functionality
    using transformer models, with singleton instance management.
    """

    _instances: ClassVar[Dict[str, "AnalyzeService"]] = {}

    def __init__(self, model_name: Optional[str] = None) -> None:
        """
        Initialize the analyze service with the specified model.

        Args:
            model_name: Name of the model to use, defaults to settings.DEFAULT_MODEL_NAME
        """
        self.model_name: str = model_name or settings.DEFAULT_MODEL_NAME
        self.device: str = settings.INFERENCE_DEVICE
        self._sentiment_pipeline = None
        self._zero_shot_pipeline = None

    @classmethod
    def get_instance(cls, model_name: Optional[str] = None) -> "AnalyzeService":
        """
        Get or create a singleton instance for the specified model.

        Args:
            model_name: Name of the model to use

        Returns:
            AnalyzeService: A singleton instance for the specified model
        """
        key = model_name or settings.DEFAULT_MODEL_NAME
        if key not in cls._instances:
            cls._instances[key] = cls(model_name)
        return cls._instances[key]

    def _get_pipeline(self, task: str, model_name: Optional[str] = None) -> Any:
        """
        Get or create a pipeline for the specified task.

        Args:
            task: The pipeline task (e.g., 'sentiment-analysis')
            model_name: Optional model name override

        Returns:
            Any: Transformer pipeline for the task
        """
        if task == "sentiment-analysis":
            if not self._sentiment_pipeline:
                self._sentiment_pipeline = pipeline(
                    task, model=model_name or self.model_name, device=self.device
                )
            return self._sentiment_pipeline
        elif task == "zero-shot-classification":
            if not self._zero_shot_pipeline:
                self._zero_shot_pipeline = pipeline(
                    task, model="facebook/bart-large-mnli", device=self.device
                )
            return self._zero_shot_pipeline

    def extract_key_phrases(self, text: str, label: str) -> List[KeyPhrase]:
        """
        Extract key phrases from text using zero-shot classification.

        Args:
            text: Input text to analyze
            label: Sentiment label to guide extraction

        Returns:
            List[KeyPhrase]: List of KeyPhrase objects containing extracted phrases
        """
        with tracer.start_as_current_span("extract_key_phrases"):
            classifier = self._get_pipeline("zero-shot-classification")
            sentences = [s.strip() for s in text.split(".") if s.strip()]
            if len(sentences) <= 1:
                return [KeyPhrase(phrase=text, importance=0.9)]
            sentiment_cats = (
                ["positive opinion", "negative opinion"]
                if label.lower() in ["positive", "negative"]
                else [f"{label.lower()} emotion"]
            )
            results = classifier(sentences, sentiment_cats)
            phrases: List[KeyPhrase] = []
            for i, res in enumerate(results):
                if max(res["scores"]) > 0.5:
                    phrases.append(
                        KeyPhrase(phrase=sentences[i], importance=max(res["scores"]))
                    )
            return sorted(phrases, key=lambda x: x.importance, reverse=True)[:3]

    def analyze_sentiment(self, request: SentimentRequest) -> SentimentResponse:
        """
        Analyze sentiment of a single text.

        Args:
            request: SentimentRequest with text and parameters

        Returns:
            SentimentResponse: Sentiment analysis results containing sentiment label and scores

        Raises:
            InferenceError: If there's an issue with the model inference
        """
        with tracer.start_as_current_span("analyze_sentiment"):
            classifier = self._get_pipeline("sentiment-analysis")
            result = classifier(request.text)[0]
            sentiment = result["label"].lower()
            score = result["score"]
            # Build scores dict as required by SentimentResponse
            scores = {result["label"].upper(): score}
            # key_phrases extraction logic can be added if needed, but not part of SentimentResponse
            return SentimentResponse(
                text=request.text, sentiment=sentiment.upper(), scores=scores
            )

    def analyze_batch_sentiment(
        self, request: BatchSentimentRequest
    ) -> BatchSentimentResponse:
        """
        Analyze sentiment for multiple texts.

        Args:
            request: BatchSentimentRequest with texts and parameters

        Returns:
            BatchSentimentResponse: Collection of sentiment analysis results for all texts

        Raises:
            ValidationError: If the request is invalid
            InferenceError: If there's an issue with the model inference
        """
        with tracer.start_as_current_span("analyze_batch_sentiment"):
            results = []
            for text in request.texts:
                single_request = SentimentRequest(text=text, model_name=request.model_name)
                results.append(self.analyze_sentiment(single_request))
            return BatchSentimentResponse(results=results)
