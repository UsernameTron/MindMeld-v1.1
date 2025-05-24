# Sentiment Analysis API Documentation

## Overview

The MindMeld Sentiment Analysis API provides both text-based and URL-based sentiment analysis capabilities. The API uses state-of-the-art transformer models to analyze sentiment and emotions in text content.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Text-Based Sentiment Analysis

**Endpoint:** `POST /api/v1/analyze/sentiment`

Analyzes sentiment and emotions in provided text content.

#### Request Body

```json
{
  "text": "I love this amazing product!",
  "include_scores": true,
  "include_emotions": true,
  "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
  "normalize_scores": true
}
```

#### Parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `text` | string | Yes | - | Text content to analyze for sentiment |
| `include_scores` | boolean | No | `true` | Include detailed sentiment scores in response |
| `include_emotions` | boolean | No | `true` | Include emotion category scores |
| `model_name` | string | No | `null` | Specific model to use for analysis |
| `normalize_scores` | boolean | No | `true` | Normalize sentiment scores to range 0-1 |

#### Response

```json
{
  "text": "I love this amazing product!",
  "sentiment": "POSITIVE",
  "scores": {
    "POSITIVE": 0.999889612197876,
    "NEGATIVE": 0.000110387802124
  },
  "emotions": {
    "joy": 0.85,
    "anger": 0.02,
    "fear": 0.01,
    "sadness": 0.02,
    "surprise": 0.08,
    "disgust": 0.02
  }
}
```

#### Example cURL

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/sentiment" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love this amazing product!",
    "include_scores": true,
    "include_emotions": true
  }'
```

### 2. URL-Based Sentiment Analysis

**Endpoint:** `POST /api/v1/analyze/sentiment/url`

Extracts content from a URL and analyzes its sentiment and emotions.

#### Request Body

```json
{
  "url": "https://example.com/article",
  "include_scores": true,
  "include_emotions": true,
  "model_name": "distilbert-base-uncased-finetuned-sst-2-english",
  "normalize_scores": true,
  "max_content_length": 10000
}
```

#### Parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `url` | string | Yes | - | Valid HTTP/HTTPS URL to extract content from |
| `include_scores` | boolean | No | `true` | Include detailed sentiment scores in response |
| `include_emotions` | boolean | No | `true` | Include emotion category scores |
| `model_name` | string | No | `null` | Specific model to use for analysis |
| `normalize_scores` | boolean | No | `true` | Normalize sentiment scores to range 0-1 |
| `max_content_length` | integer | No | `10000` | Maximum content length to analyze (characters) |

#### Response

```json
{
  "text": "When to use JSONPlaceholder is a free online REST API...",
  "sentiment": "NEUTRAL",
  "scores": {
    "POSITIVE": 0.25,
    "NEGATIVE": 0.15,
    "NEUTRAL": 0.60
  },
  "emotions": {
    "neutral": 0.70,
    "joy": 0.15,
    "anger": 0.05,
    "fear": 0.02,
    "sadness": 0.03,
    "surprise": 0.03,
    "disgust": 0.02
  }
}
```

#### Example cURL

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/sentiment/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://jsonplaceholder.typicode.com/",
    "include_scores": true,
    "include_emotions": true
  }'
```

### 3. Health Check

**Endpoint:** `GET /health`

Returns the health status of the API.

#### Response

```json
{
  "status": "healthy"
}
```

## Rate Limiting

The URL-based sentiment analysis endpoint includes rate limiting to prevent abuse:

- **Limit:** 10 requests per 5 minutes per IP address
- **Headers:** Rate limit information is included in response headers
- **429 Response:** When rate limit is exceeded

### Rate Limit Headers

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1640995200
Retry-After: 300
```

## Content Extraction Features

The URL-based sentiment analysis includes advanced content extraction:

### Robots.txt Compliance
- Automatically checks and respects robots.txt files
- Returns error if scraping is disallowed

### Content Caching
- In-memory caching with 24-hour TTL
- MD5-based cache keys for efficient lookup
- Reduces repeated requests to the same URLs

### HTML Processing
- Extracts clean text from HTML content
- Removes scripts, styles, and navigation elements
- Preserves meaningful content structure

### Content Validation
- Maximum content length limits (configurable)
- Automatic content truncation if needed
- Error handling for invalid or inaccessible URLs

## Error Responses

### Validation Errors (422)

```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Rate Limit Exceeded (429)

```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

### Content Extraction Errors (400)

```json
{
  "detail": "Scraping disallowed by robots.txt for https://example.com"
}
```

## Supported Models

The API supports various sentiment analysis models:

### Default Models
- `distilbert-base-uncased-finetuned-sst-2-english` (default)
- `cardiffnlp/twitter-roberta-base-sentiment-latest`
- `nlptown/bert-base-multilingual-uncased-sentiment`

### Custom Models
You can specify custom Hugging Face model names in the `model_name` parameter.

## Emotion Categories

When `include_emotions` is true, the API returns scores for these emotion categories:

- **Joy** - Happiness, pleasure, satisfaction
- **Anger** - Irritation, frustration, rage
- **Fear** - Anxiety, worry, nervousness
- **Sadness** - Sorrow, disappointment, grief
- **Surprise** - Astonishment, amazement
- **Disgust** - Revulsion, distaste
- **Neutral** - No strong emotional content

## Integration Examples

### JavaScript/TypeScript

```typescript
interface SentimentRequest {
  text: string;
  include_scores?: boolean;
  include_emotions?: boolean;
}

interface SentimentResponse {
  text: string;
  sentiment: string;
  scores: Record<string, number>;
  emotions?: Record<string, number>;
}

async function analyzeSentiment(text: string): Promise<SentimentResponse> {
  const response = await fetch('/api/v1/analyze/sentiment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      include_scores: true,
      include_emotions: true,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}
```

### Python

```python
import requests
from typing import Dict, Any

def analyze_sentiment(text: str, base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Analyze sentiment of text content."""
    response = requests.post(
        f"{base_url}/api/v1/analyze/sentiment",
        json={
            "text": text,
            "include_scores": True,
            "include_emotions": True,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

def analyze_url_sentiment(url: str, base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Analyze sentiment of content from URL."""
    response = requests.post(
        f"{base_url}/api/v1/analyze/sentiment/url",
        json={
            "url": url,
            "include_scores": True,
            "include_emotions": True,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()
```

## Performance Considerations

### Text Analysis
- **Latency:** ~100-500ms per request
- **Throughput:** ~10-50 requests/second (model dependent)
- **Memory:** ~2GB RAM for model loading

### URL Analysis
- **Latency:** ~2-10 seconds per request (network dependent)
- **Caching:** Subsequent requests to same URL are ~100ms
- **Rate Limiting:** 10 requests per 5 minutes

## Best Practices

1. **Caching:** Implement client-side caching for repeated analyses
2. **Error Handling:** Always handle rate limiting and validation errors
3. **Timeouts:** Use appropriate timeouts, especially for URL analysis
4. **Content Length:** Keep text under 10,000 characters for optimal performance
5. **Rate Limits:** Respect rate limits and implement exponential backoff

## Changelog

### Version 1.1.0
- Added URL-based sentiment analysis
- Implemented content extraction service with robots.txt compliance
- Added rate limiting and caching
- Enhanced error handling and validation
- Added emotion analysis capabilities

### Version 1.0.0
- Initial release with text-based sentiment analysis
- Basic sentiment classification (POSITIVE/NEGATIVE)
- Score confidence levels
