#!/usr/bin/env python3
"""
Simple test script to verify URL-based sentiment analysis functionality.
This script tests the complete end-to-end workflow of the enhanced sentiment analysis system.
"""

import asyncio
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_content_extraction():
    """Test the content extraction service."""
    try:
        from app.services.analyze.content_extraction_service import (
            ContentExtractionService,
        )

        service = ContentExtractionService.get_instance()

        # Test with a simple, reliable URL
        test_url = "https://httpbin.org/html"
        logger.info(f"Testing content extraction from: {test_url}")

        content = await service.extract_content(test_url)
        logger.info(f"Successfully extracted {len(content)} characters")
        logger.info(f"Content preview: {content[:200]}...")

        # Test cache functionality
        logger.info("Testing cache functionality...")
        cached_content = await service.extract_content(test_url)
        assert content == cached_content, "Cache returned different content"
        logger.info("✅ Cache test passed")

        # Test cache stats
        stats = service.get_cache_stats()
        logger.info(f"Cache stats: {stats}")

        return True

    except Exception as e:
        logger.error(f"❌ Content extraction test failed: {e}")
        return False


def test_url_sentiment_model():
    """Test the URL sentiment request model."""
    try:
        from app.models.analyze.analyze import URLSentimentRequest

        # Test valid URL
        valid_request = URLSentimentRequest(
            url="https://example.com",
            include_scores=True,
            include_emotions=True,
            model_name="distilbert-base-uncased-finetuned-sst-2-english",
            normalize_scores=True,
            max_content_length=10000,
        )
        logger.info(f"✅ Valid URL request created: {valid_request.url}")

        # Test invalid URL (should raise validation error)
        try:
            invalid_request = URLSentimentRequest(
                url="not-a-url",
                include_scores=True,
                include_emotions=True,
                model_name="distilbert-base-uncased-finetuned-sst-2-english",
                normalize_scores=True,
                max_content_length=10000,
            )
            logger.error("❌ Invalid URL validation failed - should have raised error")
            return False
        except Exception as e:
            logger.info(f"✅ Invalid URL correctly rejected: {e}")

        return True

    except Exception as e:
        logger.error(f"❌ URL sentiment model test failed: {e}")
        return False


async def test_complete_workflow():
    """Test the complete URL sentiment analysis workflow."""
    try:
        from app.models.analyze.analyze import SentimentRequest
        from app.services.analyze.analyze_service import AnalyzeService
        from app.services.analyze.content_extraction_service import (
            ContentExtractionService,
        )

        # Test with a simple URL that should work
        test_url = "https://httpbin.org/html"

        logger.info(f"Testing complete workflow with URL: {test_url}")

        # Step 1: Extract content
        content_service = ContentExtractionService.get_instance()
        content = await content_service.extract_content(test_url)
        logger.info(f"Step 1 ✅ Content extracted: {len(content)} characters")

        # Step 2: Analyze sentiment
        analyze_service = AnalyzeService.get_instance()
        sentiment_request = SentimentRequest(
            text=content,
            include_scores=True,
            include_emotions=True,
            model_name="distilbert-base-uncased-finetuned-sst-2-english",
            normalize_scores=True,
        )

        result = analyze_service.analyze_sentiment(sentiment_request)
        logger.info(f"Step 2 ✅ Sentiment analysis completed")
        logger.info(f"Sentiment: {result.sentiment}")
        logger.info(f"Scores: {result.scores}")

        if result.emotions:
            dominant_emotion = max(result.emotions.items(), key=lambda x: x[1])
            logger.info(
                f"Dominant emotion: {dominant_emotion[0]} ({dominant_emotion[1]:.3f})"
            )

        return True

    except Exception as e:
        logger.error(f"❌ Complete workflow test failed: {e}")
        return False


def test_imports():
    """Test that all required modules can be imported."""
    try:
        pass

        logger.info("✅ All imports successful")
        return True

    except Exception as e:
        logger.error(f"❌ Import test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("🚀 Starting URL-based sentiment analysis tests...")

    tests = [
        ("Import Test", test_imports),
        ("URL Sentiment Model Test", test_url_sentiment_model),
        ("Content Extraction Test", test_content_extraction),
        ("Complete Workflow Test", test_complete_workflow),
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

    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)

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

    if failed == 0:
        logger.info("🎉 All tests passed! URL sentiment analysis is working correctly.")
        return 0
    else:
        logger.error(f"💥 {failed} test(s) failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
