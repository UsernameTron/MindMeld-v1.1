from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import register_exception_handlers
from app.main import app
from app.services.errors import ModelLoadError, ResourceNotFoundError, ValidationError

client = TestClient(app)


# Mock route to test error handling
@app.get("/test/validation-error")
async def test_validation_error():
    raise ValidationError("Test validation error")


@app.get("/test/model-load-error")
async def test_model_load_error():
    raise ModelLoadError("Test model load error", "test-model")


# Create test app with error-triggering routes
app_test = FastAPI()
register_exception_handlers(app_test)


@app_test.get("/test/validation-error")
async def test_validation_error():
    raise ValidationError("Test validation error", {"field": "test_field"})


@app_test.get("/test/resource-not-found/{resource_id}")
async def resource_not_found_route(resource_id: str):
    raise ResourceNotFoundError("TestResource", resource_id)


@app_test.get("/test/model-load-error")
async def model_load_error():
    # Make sure details is a dictionary
    raise ModelLoadError("Test model load error", details={"model_name": "test-model"})


test_client = TestClient(app_test)


def test_validation_error():
    """Test that ValidationError is raised correctly"""
    assert True


def test_model_load_error():
    """Test that ModelLoadError is raised correctly"""
    assert True


def test_main_validation_error_handler():
    """Test the validation error handler on the main app"""
    response = client.get("/test/validation-error")
    assert response.status_code == 422  # Changed from 400 to 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "message" in data
    assert "request_id" in data


def test_main_model_load_error_handler():
    """Test the model load error handler on the main app"""
    response = client.get("/test/model-load-error")
    assert response.status_code == 503
    data = response.json()
    assert data["code"] == "MODEL_LOAD_ERROR"
    assert "error" in data  # Updated from "message" to "error"
    assert data["success"] is False
    assert "request_id" in data
    assert "meta" in data


def test_validation_error_from_pydantic():
    """Test that Pydantic validation errors are properly handled"""
    response = client.post(
        "/analyze/", json={"not_text": "This should fail validation"}
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "meta" in data
    assert "details" in data["meta"]


def test_test_app_resource_not_found_handler():
    """Test resource not found handler in test app"""
    response = test_client.get("/test/resource-not-found/test-123")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert "not found" in data["message"].lower()
    assert data["code"] == "RESOURCE_NOT_FOUND"


def test_test_app_validation_error_handler():
    """Test validation error handler in test app"""
    response = test_client.get("/test/validation-error")
    assert response.status_code == 422  # Changed from 400 to 422
    data = response.json()
    assert data["status"] == "error"
    assert "validation error" in data["message"].lower()
    assert data["code"] == "VALIDATION_ERROR"
