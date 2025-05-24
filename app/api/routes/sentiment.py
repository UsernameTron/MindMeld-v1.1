from fastapi import APIRouter, HTTPException

from app.models.analyze.sentiment import SentimentRequest, SentimentResponse
from app.services.analyze.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()


@router.post("/sentiment", response_model=SentimentResponse)
def analyze_sentiment(request: SentimentRequest):
    try:
        text = SentimentAnalyzer.extract_text_from_url(str(request.url))
        result = SentimentAnalyzer.analyze_sentiment(text)
        return SentimentResponse(**result)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Sentiment analysis failed: {e}")
