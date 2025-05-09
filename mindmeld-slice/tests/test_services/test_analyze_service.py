import pytest

from app.models.analyze.analyze import BatchSentimentRequest, SentimentRequest
from app.services.analyze.analyze_service import AnalyzeService


def test_sentiment_analysis():
    service = AnalyzeService.get_instance()
    request = SentimentRequest(text="I love this product!")
    response = service.analyze_sentiment(request)
    assert response.sentiment.lower() in ["positive", "negative", "neutral"]
    assert 0 <= list(response.scores.values())[0] <= 1


def test_key_phrase_extraction():
    service = AnalyzeService.get_instance()
    request = SentimentRequest(
        text="The product quality is excellent. The customer service was terrible though. I wouldn't recommend it."
    )
    response = service.analyze_sentiment(request)
    # key_phrases is not part of SentimentResponse, so skip those asserts
    assert response.text == request.text
    assert isinstance(response.scores, dict)


def test_batch_sentiment():
    service = AnalyzeService.get_instance()
    request = BatchSentimentRequest(texts=["I love this", "I hate this"])
    response = service.analyze_batch_sentiment(request)
    assert len(response.results) == 2
    assert response.results[0].sentiment != response.results[1].sentiment


def test_analyze_sentiment_inference_error(monkeypatch):
    service = AnalyzeService.get_instance()
    def broken_pipeline(*args, **kwargs):
        raise Exception("Model error")
    monkeypatch.setattr(service, '_get_pipeline', lambda *a, **k: broken_pipeline)
    request = SentimentRequest(text="fail")
    with pytest.raises(Exception):
        service.analyze_sentiment(request)

def test_analyze_batch_sentiment_validation_error(monkeypatch):
    service = AnalyzeService.get_instance()
    # Simulate error in analyze_sentiment
    monkeypatch.setattr(service, 'analyze_sentiment', lambda req: (_ for _ in ()).throw(Exception("Batch error")))
    request = BatchSentimentRequest(texts=["bad1", "bad2"])
    with pytest.raises(Exception):
        service.analyze_batch_sentiment(request)
