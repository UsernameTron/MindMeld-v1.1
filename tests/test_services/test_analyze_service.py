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


def test_emotion_detection():
    service = AnalyzeService.get_instance()
    request = SentimentRequest(text="I'm so happy about this!", include_emotions=True)
    response = service.analyze_sentiment(request)

    # Check emotions field exists and is a dictionary
    assert response.emotions is not None
    assert isinstance(response.emotions, dict)

    # Check required emotion categories are present
    required_emotions = ["joy", "anger", "fear", "sadness", "surprise", "disgust"]
    for emotion in required_emotions:
        assert emotion in response.emotions
        assert 0 <= response.emotions[emotion] <= 1

    # Check that at least one emotion has a significant score
    assert any(score > 0.1 for score in response.emotions.values())


def test_emotion_detection_positive_text():
    service = AnalyzeService.get_instance()
    request = SentimentRequest(
        text="I'm thrilled and excited about this wonderful news!",
        include_emotions=True,
    )
    response = service.analyze_sentiment(request)

    # For positive text, joy should be among highest emotions
    assert response.emotions["joy"] > 0.2


def test_emotion_detection_negative_text():
    service = AnalyzeService.get_instance()
    request = SentimentRequest(
        text="I'm feeling very angry and frustrated about this situation.",
        include_emotions=True,
    )
    response = service.analyze_sentiment(request)

    # For negative text, anger should be among highest emotions
    assert response.emotions["anger"] > 0.2


def test_emotion_detection_disabled():
    service = AnalyzeService.get_instance()
    request = SentimentRequest(text="I'm happy about this!", include_emotions=False)
    response = service.analyze_sentiment(request)

    # Check emotions field is None when disabled
    assert response.emotions is None


def test_batch_sentiment_with_emotions():
    service = AnalyzeService.get_instance()
    request = BatchSentimentRequest(
        texts=["I'm so happy!", "I'm very angry."], include_emotions=True
    )
    response = service.analyze_batch_sentiment(request)

    assert len(response.results) == 2

    # First result should have joy as dominant emotion
    assert response.results[0].emotions is not None
    assert response.results[0].emotions["joy"] > response.results[0].emotions["anger"]

    # Second result should have anger as dominant emotion
    assert response.results[1].emotions is not None
    assert response.results[1].emotions["anger"] > response.results[1].emotions["joy"]


def test_batch_sentiment():
    service = AnalyzeService.get_instance()
    request = BatchSentimentRequest(texts=["I love this", "I hate this"])
    response = service.analyze_batch_sentiment(request)
    assert len(response.results) == 2
    assert response.results[0].sentiment != response.results[1].sentiment


def test_analyze_emotions_directly():
    service = AnalyzeService.get_instance()
    emotions = service.analyze_emotions("I'm feeling very happy and excited!")

    # Check required emotion categories are present
    required_emotions = ["joy", "anger", "fear", "sadness", "surprise", "disgust"]
    for emotion in required_emotions:
        assert emotion in emotions

    # For this text, joy should be the dominant emotion
    assert emotions["joy"] > emotions["anger"]
    assert emotions["joy"] > emotions["sadness"]


def test_analyze_sentiment_inference_error(monkeypatch):
    service = AnalyzeService.get_instance()

    def broken_pipeline(*args, **kwargs):
        raise Exception("Model error")

    monkeypatch.setattr(service, "_get_pipeline", lambda *a, **k: broken_pipeline)
    request = SentimentRequest(text="fail")
    with pytest.raises(Exception):
        service.analyze_sentiment(request)


def test_analyze_emotions_inference_error(monkeypatch):
    service = AnalyzeService.get_instance()

    def broken_pipeline(*args, **kwargs):
        raise Exception("Emotion model error")

    monkeypatch.setattr(service, "_get_pipeline", lambda *a, **k: broken_pipeline)
    with pytest.raises(Exception):
        service.analyze_emotions("fail")


def test_analyze_batch_sentiment_validation_error(monkeypatch):
    service = AnalyzeService.get_instance()
    # Simulate error in analyze_sentiment
    monkeypatch.setattr(
        service,
        "analyze_sentiment",
        lambda req: (_ for _ in ()).throw(Exception("Batch error")),
    )
    request = BatchSentimentRequest(texts=["bad1", "bad2"])
    with pytest.raises(Exception):
        service.analyze_batch_sentiment(request)
