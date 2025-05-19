"""
Analyze models module for the MindMeld sentiment analysis functionality.

This module defines the Pydantic models for text analysis operations,
including request schemas, response formats, and validation logic for
sentiment analysis and other text analysis features.
"""

from typing import Dict, List, Optional

from app.models.common import BaseModel
from pydantic import ConfigDict, Field, field_validator


class AnalyzeRequest(BaseModel):
    """
    Request model for general text analysis operations.

    Defines the structure for requests to analyze text content,
    with validation to ensure non-empty text.
    """

    text: str = Field(
        ...,
        description="Text content to analyze",
        json_schema_extra={"example": "I love this product!"},
    )
    confidence_threshold: Optional[float] = Field(
        None,
        description="Optional confidence threshold for analysis",
        json_schema_extra={"example": 0.7},
    )
    model_config = ConfigDict(extra="forbid")

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validate that text field is not empty."""
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v


class KeyPhrase(BaseModel):
    """
    Model representing an extracted key phrase from text.

    Contains the extracted phrase and its importance score.
    """

    phrase: str = Field(
        ...,
        description="The extracted key phrase",
        json_schema_extra={"example": "great product"},
    )
    score: float = Field(
        ...,
        description="Importance score of the phrase",
        json_schema_extra={"example": 0.92},
    )


class AnalysisResult(BaseModel):
    """
    Result of a text analysis operation.

    Contains sentiment scores and other analytical data
    extracted from the input text.
    """

    text: str = Field(
        ...,
        description="Original text that was analyzed",
        json_schema_extra={"example": "I love this product!"},
    )
    label: str = Field(
        ...,
        description="Sentiment label (e.g., POSITIVE, NEGATIVE)",
        json_schema_extra={"example": "POSITIVE"},
    )
    score: float = Field(
        ..., description="Primary sentiment score", json_schema_extra={"example": 0.95}
    )
    confidence_level: str = Field(
        ...,
        description="Confidence level (e.g., high, medium, low)",
        json_schema_extra={"example": "high"},
    )
    is_uncertain: bool = Field(
        ...,
        description="Whether the sentiment is uncertain",
        json_schema_extra={"example": False},
    )
    key_phrases: List[KeyPhrase] = Field(
        ...,
        description="Key phrases extracted from the text",
        json_schema_extra={"example": [{"phrase": "great product", "score": 0.92}]},
    )
    intensity_level: str = Field(
        ...,
        description="Intensity of sentiment (e.g., strong, moderate)",
        json_schema_extra={"example": "strong"},
    )


class BatchResult(BaseModel):
    """
    Container for multiple analysis results.

    Used for batch processing operations to hold multiple
    individual analysis results.
    """

    results: List[AnalysisResult] = Field(
        ...,
        description="List of analysis results",
        json_schema_extra={
            "example": [
                {
                    "text": "I love this product!",
                    "label": "POSITIVE",
                    "score": 0.95,
                    "confidence_level": "high",
                    "is_uncertain": False,
                    "key_phrases": [{"phrase": "great product", "score": 0.92}],
                    "intensity_level": "strong",
                }
            ]
        },
    )


class AnalyzeResponse(BaseModel):
    """
    Response model for text analysis operations.

    Provides a standardized structure for returning
    analysis results to the client.
    """

    result: AnalysisResult = Field(
        ...,
        description="Analysis result",
        json_schema_extra={
            "example": {
                "text": "I love this product!",
                "label": "POSITIVE",
                "score": 0.95,
                "confidence_level": "high",
                "is_uncertain": False,
                "key_phrases": [{"phrase": "great product", "score": 0.92}],
                "intensity_level": "strong",
            }
        },
    )


class SentimentRequest(BaseModel):
    """
    Request model for sentiment analysis operations.

    Defines the structure for requests to analyze sentiment in text,
    with validation to ensure non-empty text and parameters to
    control analysis behavior.
    """

    text: str = Field(
        ...,
        description="Text to analyze for sentiment",
        json_schema_extra={"example": "I really enjoyed this movie!"},
    )
    include_scores: bool = Field(
        True,
        description="Include detailed sentiment scores in response",
        json_schema_extra={"example": True},
    )
    include_emotions: bool = Field(
        True,
        description="Include emotion category scores in response (joy, anger, fear, etc.)",
        json_schema_extra={"example": True},
    )
    model_name: Optional[str] = Field(
        None,
        description="Specific model to use for sentiment analysis",
        json_schema_extra={"example": "distilbert-base-uncased"},
    )
    normalize_scores: bool = Field(
        True,
        description="Normalize sentiment scores to range 0-1",
        json_schema_extra={"example": True},
    )
    model_config = ConfigDict(extra="forbid")

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validate that text field is not empty."""
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v


class SentimentResponse(BaseModel):
    """
    Response model for sentiment analysis operations.

    Provides sentiment classification, emotion categories, and scores for the analyzed text.
    """

    text: str = Field(
        ...,
        description="Original text that was analyzed",
        json_schema_extra={"example": "I really enjoyed this movie!"},
    )
    sentiment: str = Field(
        ...,
        description="Overall sentiment classification",
        json_schema_extra={"example": "POSITIVE"},
    )
    scores: Dict[str, float] = Field(
        ...,
        description="Detailed sentiment scores",
        json_schema_extra={"example": {"POSITIVE": 0.95, "NEGATIVE": 0.05}},
    )
    emotions: Optional[Dict[str, float]] = Field(
        None,
        description="Emotion category scores (joy, anger, fear, sadness, surprise, disgust)",
        json_schema_extra={"example": {"joy": 0.8, "surprise": 0.15, "anger": 0.02, "sadness": 0.01, "fear": 0.01, "disgust": 0.01}},
    )


class BatchSentimentRequest(BaseModel):
    """
    Request model for batch sentiment analysis operations.

    Allows submitting multiple texts for sentiment analysis in a single request,
    with shared parameters for all analyses.
    """

    texts: List[str] = Field(
        ...,
        description="List of texts to analyze",
        min_length=1,
        json_schema_extra={"example": ["I love this!", "Not good."]},
    )
    include_scores: bool = Field(
        True,
        description="Include detailed sentiment scores in response",
        json_schema_extra={"example": True},
    )
    include_emotions: bool = Field(
        True,
        description="Include emotion category scores in response (joy, anger, fear, etc.)",
        json_schema_extra={"example": True},
    )
    model_name: Optional[str] = Field(
        None,
        description="Specific model to use for sentiment analysis",
        json_schema_extra={"example": "distilbert-base-uncased"},
    )
    normalize_scores: bool = Field(
        True,
        description="Normalize sentiment scores to range 0-1",
        json_schema_extra={"example": True},
    )
    model_config = ConfigDict(extra="forbid")


class BatchSentimentResponse(BaseModel):
    """
    Response model for batch sentiment analysis operations.

    Contains sentiment analysis results for multiple input texts.
    """

    results: List[SentimentResponse] = Field(
        ...,
        description="List of sentiment analysis results",
        json_schema_extra={
            "example": [
                {
                    "text": "I really enjoyed this movie!",
                    "sentiment": "POSITIVE",
                    "scores": {"POSITIVE": 0.95, "NEGATIVE": 0.05},
                }
            ]
        },
    )
