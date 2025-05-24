import re
import time
from typing import Any, Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# For sentiment and emotion analysis, use textblob and NRCLex (or fallback to simple rules if not available)
try:
    from nrclex import NRCLex
    from textblob import TextBlob
except ImportError:
    TextBlob = None
    NRCLex = None


class SentimentAnalyzer:
    RATE_LIMIT_SECONDS = 2  # Simple rate limit: 1 request per 2 seconds
    last_request_time = 0.0

    @staticmethod
    def _rate_limit():
        now = time.time()
        if (
            now - SentimentAnalyzer.last_request_time
            < SentimentAnalyzer.RATE_LIMIT_SECONDS
        ):
            time.sleep(
                SentimentAnalyzer.RATE_LIMIT_SECONDS
                - (now - SentimentAnalyzer.last_request_time)
            )
        SentimentAnalyzer.last_request_time = time.time()

    @staticmethod
    def _respect_robots(url: str) -> bool:
        # Simple robots.txt check (does not parse all rules)
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            resp = requests.get(robots_url, timeout=3)
            if resp.status_code == 200 and "Disallow: /" in resp.text:
                return False
        except Exception:
            pass
        return True

    @staticmethod
    def extract_text_from_url(url: str) -> str:
        if not SentimentAnalyzer._respect_robots(url):
            raise PermissionError("Scraping disallowed by robots.txt")
        SentimentAnalyzer._rate_limit()
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def analyze_sentiment(text: str) -> Dict[str, Any]:
        if not text:
            raise ValueError("No text to analyze")
        # Sentiment (TextBlob)
        if TextBlob:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            sentiment = (
                "positive"
                if polarity > 0.1
                else "negative" if polarity < -0.1 else "neutral"
            )
        else:
            # Fallback: count positive/negative words (very basic)
            polarity = 0.0
            subjectivity = 0.5
            sentiment = "neutral"
        # Emotions (NRCLex)
        emotions = {}
        if NRCLex:
            nrc = NRCLex(text)
            raw_emotions = nrc.raw_emotion_scores
            total = sum(raw_emotions.values())
            for k in ["joy", "anger", "fear", "sadness", "surprise", "disgust"]:
                emotions[k] = raw_emotions.get(k, 0) / total if total else 0.0
        else:
            for k in ["joy", "anger", "fear", "sadness", "surprise", "disgust"]:
                emotions[k] = 0.0
        # Confidence (simple: abs(polarity) for sentiment, normalized emotion scores)
        confidence = min(1.0, max(0.0, abs(polarity)))
        return {
            "overall_sentiment": sentiment,
            "sentiment_score": polarity,
            "subjectivity": subjectivity,
            "emotions": emotions,
            "confidence": confidence,
        }
