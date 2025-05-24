from typing import Dict

from pydantic import BaseModel, HttpUrl


class SentimentRequest(BaseModel):
    url: HttpUrl


class SentimentResponse(BaseModel):
    overall_sentiment: str
    sentiment_score: float
    subjectivity: float
    emotions: Dict[str, float]
    confidence: float
