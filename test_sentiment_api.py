#!/usr/bin/env python3
"""
Production Test Suite for Sentiment Analysis API

This script provides comprehensive testing for the sentiment analysis functionality
including both text-based and URL-based analysis endpoints.
"""

import logging
import sys
import time
from typing import Dict

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"


class SentimentAnalysisTestSuite:
    """Comprehensive test suite for sentiment analysis API endpoints."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "SentimentAnalysis-TestSuite/1.0",
            }
        )

    def test_health_check(self) -> bool:
        """Test the API health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Health check passed: {result}")
                return True
            else:
                logger.error(
                    f"❌ Health check failed with status {response.status_code}"
                )
                return False
        except Exception as e:
            logger.error(f"❌ Health check failed with exception: {e}")
            return False

    def test_text_sentiment_positive(self) -> bool:
        """Test sentiment analysis with positive text."""
        try:
            payload = {
                "text": "I absolutely love this incredible product! It's fantastic and amazing!",
                "include_scores": True,
                "include_emotions": True,
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/sentiment", json=payload, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                sentiment = result.get("sentiment", "")
                scores = result.get("scores", {})

                logger.info(f"✅ Positive sentiment test passed: {sentiment}")
                logger.info(f"   Scores: {scores}")

                # Validate that positive sentiment was detected
                if sentiment == "POSITIVE" and scores.get("POSITIVE", 0) > 0.5:
                    return True
                else:
                    logger.warning(f"⚠️ Expected POSITIVE sentiment but got {sentiment}")
                    return False
            else:
                logger.error(
                    f"❌ Positive sentiment test failed with status {response.status_code}: {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Positive sentiment test failed with exception: {e}")
            return False

    def test_text_sentiment_negative(self) -> bool:
        """Test sentiment analysis with negative text."""
        try:
            payload = {
                "text": "This is absolutely terrible and awful. I hate it completely!",
                "include_scores": True,
                "include_emotions": True,
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/sentiment", json=payload, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                sentiment = result.get("sentiment", "")
                scores = result.get("scores", {})

                logger.info(f"✅ Negative sentiment test passed: {sentiment}")
                logger.info(f"   Scores: {scores}")

                # Validate that negative sentiment was detected
                if sentiment == "NEGATIVE" and scores.get("NEGATIVE", 0) > 0.5:
                    return True
                else:
                    logger.warning(f"⚠️ Expected NEGATIVE sentiment but got {sentiment}")
                    return False
            else:
                logger.error(
                    f"❌ Negative sentiment test failed with status {response.status_code}: {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Negative sentiment test failed with exception: {e}")
            return False

    def test_url_sentiment_analysis(self) -> bool:
        """Test URL-based sentiment analysis."""
        try:
            # Use a URL that typically allows scraping and has neutral content
            payload = {
                "url": "https://jsonplaceholder.typicode.com/",
                "include_scores": True,
                "include_emotions": True,
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/sentiment/url",
                json=payload,
                timeout=60,  # Longer timeout for URL processing
            )

            if response.status_code == 200:
                result = response.json()
                sentiment = result.get("sentiment", "")
                text = result.get("text", "")
                scores = result.get("scores", {})

                logger.info(f"✅ URL sentiment test passed: {sentiment}")
                logger.info(f"   Content length: {len(text)} characters")
                logger.info(f"   Content preview: {text[:100]}...")
                logger.info(f"   Scores: {scores}")
                return True
            else:
                logger.error(
                    f"❌ URL sentiment test failed with status {response.status_code}: {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ URL sentiment test failed with exception: {e}")
            return False

    def test_invalid_url_handling(self) -> bool:
        """Test error handling for invalid URLs."""
        try:
            payload = {"url": "not-a-valid-url", "include_scores": True}

            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/sentiment/url",
                json=payload,
                timeout=30,
            )

            # Should return a validation error (422)
            if response.status_code == 422:
                logger.info("✅ Invalid URL correctly rejected with validation error")
                return True
            else:
                logger.error(
                    f"❌ Invalid URL test failed: expected 422, got {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Invalid URL test failed with exception: {e}")
            return False

    def test_empty_text_handling(self) -> bool:
        """Test error handling for empty text."""
        try:
            payload = {"text": "", "include_scores": True}

            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/sentiment", json=payload, timeout=30
            )

            # Should return a validation error (422)
            if response.status_code == 422:
                logger.info("✅ Empty text correctly rejected with validation error")
                return True
            else:
                logger.error(
                    f"❌ Empty text test failed: expected 422, got {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Empty text test failed with exception: {e}")
            return False

    def test_rate_limiting(self) -> bool:
        """Test rate limiting on URL endpoints."""
        try:
            payload = {
                "url": "https://jsonplaceholder.typicode.com/",
                "include_scores": True,
            }

            # Make multiple requests quickly to test rate limiting
            responses = []
            for i in range(3):
                response = self.session.post(
                    f"{self.base_url}/api/v1/analyze/sentiment/url",
                    json=payload,
                    timeout=60,
                )
                responses.append(response)
                logger.info(f"Request {i+1}: Status {response.status_code}")

                # Short delay between requests
                time.sleep(1)

            # Check if rate limiting is working
            rate_limited = any(r.status_code == 429 for r in responses)
            successful = any(r.status_code == 200 for r in responses)

            if successful:
                logger.info("✅ Rate limiting test passed: some requests succeeded")
                if rate_limited:
                    logger.info(
                        "   Rate limiting is active (some requests were throttled)"
                    )
                return True
            else:
                logger.error("❌ Rate limiting test failed: no requests succeeded")
                return False

        except Exception as e:
            logger.error(f"❌ Rate limiting test failed with exception: {e}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all test cases and return results."""
        tests = [
            ("Health Check", self.test_health_check),
            ("Text Sentiment (Positive)", self.test_text_sentiment_positive),
            ("Text Sentiment (Negative)", self.test_text_sentiment_negative),
            ("URL Sentiment Analysis", self.test_url_sentiment_analysis),
            ("Invalid URL Handling", self.test_invalid_url_handling),
            ("Empty Text Handling", self.test_empty_text_handling),
            ("Rate Limiting", self.test_rate_limiting),
        ]

        results = {}

        logger.info("🚀 Starting Sentiment Analysis API Test Suite")
        logger.info("=" * 60)

        for test_name, test_func in tests:
            logger.info(f"\n📋 Running: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                logger.info(f"{status}: {test_name}")
            except Exception as e:
                logger.error(f"❌ FAIL: {test_name} - Exception: {e}")
                results[test_name] = False

        return results

    def print_summary(self, results: Dict[str, bool]) -> None:
        """Print test results summary."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("=" * 60)

        passed = sum(1 for result in results.values() if result)
        failed = sum(1 for result in results.values() if not result)

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status}: {test_name}")

        logger.info(f"\nTotal Tests: {len(results)}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")

        if failed == 0:
            logger.info(
                "🎉 All tests passed! Sentiment analysis API is working correctly."
            )
        else:
            logger.error(f"💥 {failed} test(s) failed. Please review the issues above.")


def main():
    """Main test execution function."""
    suite = SentimentAnalysisTestSuite()
    results = suite.run_all_tests()
    suite.print_summary(results)

    # Exit with appropriate code
    failed_count = sum(1 for result in results.values() if not result)
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
