#!/usr/bin/env python3
"""
Integration test for the sentiment analysis API endpoints.

This script tests the complete sentiment analysis workflow including:
- Text-based sentiment analysis
- URL-based sentiment analysis with content extraction
- Error handling and validation
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.analyze import router
from app.models.analyze.analyze import SentimentRequest, URLSentimentRequest
from app.services.analyze.content_extraction_service import ContentExtractionService

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

logger = logging.getLogger(__name__)


def test_text_sentiment_analysis():
    """Test direct text sentiment analysis."""
    logger.info("🧪 Testing text-based sentiment analysis...")

    try:
        # Create a test app
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/sentiment")

        with TestClient(app) as client:
            # Test positive sentiment
            response = client.post(
                "/api/v1/sentiment",
                json={
                    "text": "I love this amazing product! It's fantastic and wonderful.",
                    "model": "distilbert-base-uncased-finetuned-sst-2-english",
                    "batch_size": 1,
                    "include_probabilities": True,
                },
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    f"✅ Positive sentiment analysis successful: {result.get('data', {}).get('sentiment', 'N/A')}"
                )
                return True
            else:
                logger.error(
                    f"❌ Text sentiment analysis failed with status {response.status_code}: {response.text}"
                )
                return False

    except Exception as e:
        logger.error(f"❌ Text sentiment analysis test failed with exception: {e}")
        return False


async def test_content_extraction():
    """Test content extraction from a publicly available URL."""
    logger.info("🧪 Testing content extraction...")

    try:
        content_service = ContentExtractionService()

        # Use a URL that typically allows scraping
        test_url = "https://jsonplaceholder.typicode.com/"

        extracted_content = await content_service.extract_content(test_url)

        if extracted_content and len(extracted_content.strip()) > 0:
            logger.info(
                f"✅ Content extraction successful. Extracted {len(extracted_content)} characters"
            )
            logger.info(f"Preview: {extracted_content[:100]}...")
            return True
        else:
            logger.error("❌ Content extraction returned empty content")
            return False

    except Exception as e:
        logger.error(f"❌ Content extraction test failed: {e}")
        return False


def test_url_sentiment_api():
    """Test URL-based sentiment analysis API endpoint."""
    logger.info("🧪 Testing URL-based sentiment analysis API...")

    try:
        # Create a test app
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/sentiment")

        with TestClient(app) as client:
            # Test with a simple URL that should have neutral/positive content
            response = client.post(
                "/api/v1/sentiment/url",
                json={
                    "url": "https://jsonplaceholder.typicode.com/",
                    "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
                    "include_scores": True,
                    "include_emotions": True,
                    "normalize_scores": True,
                    "max_content_length": 10000,
                },
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    f"✅ URL sentiment analysis successful: {result.get('data', {}).get('sentiment', 'N/A')}"
                )
                return True
            else:
                logger.error(
                    f"❌ URL sentiment analysis failed with status {response.status_code}: {response.text}"
                )
                return False

    except Exception as e:
        logger.error(f"❌ URL sentiment analysis API test failed with exception: {e}")
        return False


def test_validation_and_error_handling():
    """Test input validation and error handling."""
    logger.info("🧪 Testing validation and error handling...")

    try:
        # Test invalid URL validation
        try:
            request = URLSentimentRequest(
                url="not-a-valid-url",
                model_name="distilbert-base-uncased-finetuned-sst-2-english",
                include_scores=True,
                include_emotions=True,
                normalize_scores=True,
                max_content_length=10000,
            )
            logger.error(
                "❌ Invalid URL validation failed - should have raised an error"
            )
            return False
        except Exception:
            logger.info("✅ Invalid URL correctly rejected")

        # Test valid URL validation
        try:
            request = URLSentimentRequest(
                url="https://example.com",
                model_name="distilbert-base-uncased-finetuned-sst-2-english",
                include_scores=True,
                include_emotions=True,
                normalize_scores=True,
                max_content_length=10000,
            )
            logger.info("✅ Valid URL correctly accepted")
        except Exception as e:
            logger.error(f"❌ Valid URL incorrectly rejected: {e}")
            return False

        # Test text sentiment validation
        try:
            request = SentimentRequest(
                text="This is a test",
                model_name="distilbert-base-uncased-finetuned-sst-2-english",
                include_scores=True,
                include_emotions=True,
                normalize_scores=True,
            )
            logger.info("✅ Text sentiment request validation successful")
        except Exception as e:
            logger.error(f"❌ Text sentiment request validation failed: {e}")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Validation test failed with exception: {e}")
        return False


async def main():
    """Run all integration tests."""
    logger.info("🚀 Starting comprehensive integration tests...")
    logger.info("=" * 60)

    tests = [
        ("Text Sentiment Analysis", test_text_sentiment_analysis),
        ("Content Extraction", test_content_extraction),
        ("URL Sentiment API", test_url_sentiment_api),
        ("Validation & Error Handling", test_validation_and_error_handling),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 INTEGRATION TEST SUMMARY")
    logger.info("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    logger.info(f"\nTotal: {len(results)} tests")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")

    if failed > 0:
        logger.error(f"💥 {failed} test(s) failed. Please check the implementation.")
        return False
    else:
        logger.info("🎉 All integration tests passed!")
        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
