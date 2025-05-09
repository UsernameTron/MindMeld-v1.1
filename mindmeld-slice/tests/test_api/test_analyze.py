from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.analyze.analyze import AnalysisResult, AnalyzeResponse
from app.services.auth.auth_service import create_access_token
from app.services.errors import InferenceError, ValidationError

client = TestClient(app)

ANALYZE_JWT = create_access_token({"sub": "testuser", "scopes": ["analyze"]})
AUTH_HEADER = {"Authorization": f"Bearer {ANALYZE_JWT}"}


class TestAnalyzeEndpoint:
    def test_analyze_positive_sentiment(self):
        response = client.post(
            "/api/v1/analyze/", json={"text": "I love this product!"}, headers=AUTH_HEADER
        )
        assert response.status_code == 200
        data = response.json()
        # StandardResponse structure checks
        assert data["success"] is True
        assert "data" in data
        assert "meta" in data
        # Actual results
        assert "result" in data["data"]
        assert data["data"]["result"]["label"] == "POSITIVE"

    def test_analyze_negative_sentiment(self):
        response = client.post(
            "/api/v1/analyze/",
            json={"text": "This is terrible, I hate it."},
            headers=AUTH_HEADER,
        )
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}"
        data = response.json()
        # StandardResponse structure checks
        assert data["success"] is True, "Expected success flag to be True"
        assert "data" in data, "Missing data field in response"
        assert "meta" in data, "Missing meta field in response"
        # Actual results now nested in data field
        assert "result" in data["data"], "Missing result in response data"
        assert (
            data["data"]["result"]["label"] == "NEGATIVE"
        ), "Expected NEGATIVE sentiment"

    def test_empty_text(self):
        response = client.post("/api/v1/analyze/", json={"text": ""}, headers=AUTH_HEADER)
        assert response.status_code == 422  # Validation error
        data = response.json()
        # StandardResponse structure for errors
        assert data["success"] is False, "Expected success flag to be False for error"
        assert "error" in data, "Missing error field in error response"
        assert "code" in data, "Missing code field in error response"
        assert "request_id" in data, "Missing request_id in error response"

    @patch("app.services.analyze.analyze_service.AnalyzeService.analyze_sentiment")
    def test_analyze_confidence_threshold(self, mock_analyze):
        from app.models.analyze.analyze import SentimentResponse

        # Mock response with a low confidence score
        mock_analyze.return_value = SentimentResponse(
            text="This is okay I guess.", sentiment="NEGATIVE", scores={"NEGATIVE": 0.4}
        )
        response = client.post(
            "/api/v1/analyze/",
            json={"text": "This is okay I guess.", "confidence_threshold": 0.5},
            headers=AUTH_HEADER,
        )
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}"
        data = response.json()
        # StandardResponse structure checks
        assert data["success"] is True, "Expected success flag to be True"
        assert "data" in data, "Missing data field in response"
        assert "meta" in data, "Missing meta field in response"
        # Verify uncertainty based on threshold
        assert (
            data["data"]["result"]["is_uncertain"] == True
        ), "Expected is_uncertain to be True"


@patch("app.services.analyze.analyze_service.AnalyzeService.analyze_sentiment")
def test_analyze_success(mock_analyze):
    from app.models.analyze.analyze import SentimentResponse

    # Mock the service response
    mock_analyze.return_value = SentimentResponse(
        text="I love this product!",
        sentiment="POSITIVE",
        scores={"POSITIVE": 0.95, "NEGATIVE": 0.05},
    )
    response = client.post(
        "/api/v1/analyze/", json={"text": "I love this product!"}, headers=AUTH_HEADER
    )
    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"
    data = response.json()
    # Test StandardResponse structure
    assert data["success"] == True, "Expected success to be True"
    assert "data" in data, "Expected data field in response"
    assert "meta" in data, "Expected meta field in response"
    # Test actual results
    assert data["data"]["result"]["label"] == "POSITIVE", "Expected POSITIVE sentiment"


@patch("app.services.analyze.analyze_service.AnalyzeService.analyze_sentiment")
def test_analyze_inference_error(mock_analyze):
    mock_analyze.side_effect = InferenceError("Test inference error")
    response = client.post("/api/v1/analyze/", json={"text": "test text"}, headers=AUTH_HEADER)
    assert response.status_code == 500
    data = response.json()
    # StandardResponse structure for errors
    assert data["success"] is False, "Expected success flag to be False for error"
    assert "error" in data, "Missing error field in error response"
    assert "code" in data, "Missing code field in error response"
    assert "request_id" in data, "Missing request_id in error response"


def test_analyze_validation_error():
    response = client.post(
        "/api/v1/analyze/", json={}, headers=AUTH_HEADER
    )  # Missing required field
    assert response.status_code == 422
    response_json = response.json()
    # Check for the specific structured error format
    assert "success" in response_json
    assert (
        response_json["success"] is False
    ), "Expected success flag to be False for error"
    assert "error" in response_json, "Missing error field in error response"
    assert "code" in response_json, "Missing code field in error response"
    assert "request_id" in response_json, "Missing request_id in error response"
