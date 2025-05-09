"""
API routes for sentiment analysis endpoints in the MindMeld backend.

This module defines the FastAPI routes for analyzing text sentiment,
including single and batch sentiment analysis endpoints.
"""

from fastapi import APIRouter, Depends

from app.core.middleware import RateLimiter
from app.models.analyze.analyze import (
    AnalysisResult,
    AnalyzeRequest,
    AnalyzeResponse,
    BatchSentimentRequest,
    BatchSentimentResponse,
    SentimentRequest,
    SentimentResponse,
)
from app.models.common import StandardResponse
from app.services.analyze.analyze_service import AnalyzeService

router = APIRouter(tags=["Sentiment Analysis"])

# Create a singleton instance of the service
analyze_service = AnalyzeService()


@router.post(
    "",
    response_model=StandardResponse[AnalyzeResponse],
    summary="Analyze text sentiment",
    description="Analyzes the sentiment of provided text using Hugging Face transformers",
    dependencies=[Depends(RateLimiter(requests=20, window=60 * 5))],
    responses={
        429: {
            "description": "Rate limit exceeded",
            "headers": {
                "Retry-After": {
                    "description": "Seconds to wait before retrying",
                    "schema": {"type": "string"},
                }
            },
        },
    },
)
async def analyze_text(
    request: AnalyzeRequest, service: AnalyzeService = Depends()
) -> StandardResponse[AnalyzeResponse]:
    """
    Analyze the sentiment of the provided text.

    Args:
        request (AnalyzeRequest): The request containing the text to analyze.
        service (AnalyzeService): The service instance to perform the analysis.

    Returns:
        StandardResponse[AnalyzeResponse]: The analysis result wrapped in a standard response.
    """
    sentiment_request = SentimentRequest(text=request.text)
    result = service.analyze_sentiment(sentiment_request)
    results = [
        AnalysisResult(
            text=request.text,
            label=result.sentiment.upper(),
            score=list(result.scores.values())[0] if result.scores else 0.0,
            confidence_level=(
                "high"
                if (list(result.scores.values())[0] if result.scores else 0.0) > 0.8
                else "medium"
            ),
            is_uncertain=(list(result.scores.values())[0] if result.scores else 0.0)
            < 0.5,
            key_phrases=[],
            intensity_level=(
                "strong"
                if (list(result.scores.values())[0] if result.scores else 0.0) > 0.8
                else "moderate"
            ),
        )
    ]
    analyze_response = AnalyzeResponse(result=results[0])
    return StandardResponse(
        success=True,
        data=analyze_response,
        meta={"model": "default", "task": "sentiment-analysis"},
    )


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest) -> SentimentResponse:
    """
    Perform sentiment analysis on the provided text.

    Args:
        request (SentimentRequest): The request containing the text to analyze.

    Returns:
        SentimentResponse: The sentiment analysis result.
    """
    service = AnalyzeService.get_instance(request.model_name)
    return service.analyze_sentiment(request)


@router.post("/batch-sentiment", response_model=BatchSentimentResponse)
async def analyze_batch_sentiment(
    request: BatchSentimentRequest,
) -> BatchSentimentResponse:
    """
    Perform batch sentiment analysis on the provided texts.

    Args:
        request (BatchSentimentRequest): The request containing the texts to analyze.

    Returns:
        BatchSentimentResponse: The batch sentiment analysis results.
    """
    service = AnalyzeService.get_instance(request.model_name)
    return service.analyze_batch_sentiment(request)
