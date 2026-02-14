# Search Service - Usage Examples

## Overview

The `BingSearchService` validates claims in content outlines by performing web searches and scoring source credibility.

## Setup

1. **Install dependencies**:
```bash
pip install requests anthropic openai
```

2. **Configure secrets** (required):
```bash
python scripts/setup_secrets.py
```

Set the following secret:
- `bing-search-key`: Your Bing Search API v7 subscription key

## Basic Usage

### Initialize Service

```python
from services.search_service import BingSearchService

search_service = BingSearchService()
```

### 1. Perform Web Search

```python
# Search for content on a topic
results = search_service.search("artificial intelligence ethics", count=10)

for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Credibility: {result['credibility']:.2f}")
    print(f"Snippet: {result['snippet']}")
    print()
```

### 2. Calculate Domain Credibility

```python
# Score individual URLs
score1 = search_service.calculate_credibility("https://stanford.edu/research")
# Returns: 0.9 (high credibility - .edu domain)

score2 = search_service.calculate_credibility("https://www.bbc.com/news")
# Returns: 0.7 (medium-high credibility - major news)

score3 = search_service.calculate_credibility("https://example.com/blog")
# Returns: 0.5 (medium credibility - general .com)

score4 = search_service.calculate_credibility("https://random-site.xyz")
# Returns: 0.3 (low credibility - unknown domain)
```

### 3. Extract Claims from Text

```python
outline_text = """
# The History of Python

Python was created by Guido van Rossum and first released in 1991.
The language emphasizes code readability and uses significant whitespace.
Python is one of the most popular programming languages for data science.
"""

# Extract factual claims using Claude 3.5
claims = search_service.extract_claims(outline_text)

print("Extracted claims:")
for i, claim in enumerate(claims, 1):
    print(f"{i}. {claim}")
```

Output:
```
Extracted claims:
1. Python was created by Guido van Rossum
2. Python was first released in 1991
3. Python is one of the most popular programming languages for data science
```

### 4. Validate Outline (Full Pipeline)

```python
outline_text = """
# Climate Change Impact

Global temperatures have risen by approximately 1.1°C since pre-industrial times.
The Arctic is warming at twice the global average rate.
Sea levels have risen by about 8-9 inches since 1880.
"""

# Validate entire outline
report = search_service.validate_outline(outline_text)

print(f"Claims checked: {len(report['claims'])}")
print(f"Sources found: {len(report['sources'])}")
print(f"Confidence score: {report['confidence']:.2f}")
print(f"Validation status: {'PASSED ✓' if report['passed'] else 'FAILED ✗'}")

print("\nClaim Details:")
for detail in report['details']:
    status = "✓" if detail['passed'] else "✗"
    print(f"{status} {detail['claim']}")
    print(f"  Sources: {detail['sources_found']}")
    if detail['top_sources']:
        print(f"  Top source: {detail['top_sources'][0]['url']}")
```

Output:
```
Claims checked: 3
Sources found: 12
Confidence score: 1.00
Validation status: PASSED ✓

Claim Details:
✓ Global temperatures have risen by approximately 1.1°C since pre-industrial times
  Sources: 5
  Top source: https://www.nasa.gov/climate
✓ The Arctic is warming at twice the global average rate
  Sources: 4
  Top source: https://www.noaa.gov/arctic
✓ Sea levels have risen by about 8-9 inches since 1880
  Sources: 3
  Top source: https://climate.nasa.gov/sea-level
```

## Credibility Scoring System

| Domain Type | Example | Score |
|-------------|---------|-------|
| Educational | stanford.edu, mit.edu | 0.9 |
| Government | cdc.gov, nasa.gov | 0.9 |
| Major News | bbc.com, reuters.com, nytimes.com | 0.7 |
| Organizations | nature.org, who.int | 0.7 |
| Commercial | example.com, blog.com | 0.5 |
| Others | random-site.xyz | 0.3 |

## Validation Criteria

**Pass Threshold**: Confidence ≥ 0.7

**Confidence Calculation**:
```python
total_credible_sources = sum(sources with credibility ≥ 0.5 for all claims)
confidence = min(total_credible_sources / (claims_checked * 2), 1.0)
```

**Requirements**:
- Minimum 2 credible sources per claim for individual claim to pass
- Overall confidence ≥ 0.7 for outline to pass validation

## Integration with Content Pipeline

```python
from services.search_service import BingSearchService

# In outline generation flow
def generate_and_validate_outline(topic: str) -> dict:
    """Generate outline and validate claims."""
    
    # 1. Generate outline (using reasoning agent)
    outline = reasoning_agent.generate_outline(topic)
    
    # 2. Validate claims
    search_service = BingSearchService()
    validation_report = search_service.validate_outline(outline)
    
    # 3. Return outline with validation metadata
    return {
        "outline": outline,
        "validated": validation_report['passed'],
        "confidence": validation_report['confidence'],
        "claims_checked": len(validation_report['claims']),
        "sources_found": len(validation_report['sources'])
    }
```

## Error Handling

```python
from services.search_service import BingSearchService

try:
    search_service = BingSearchService()
    results = search_service.search("python programming")
except ValueError as e:
    # Missing API key
    print(f"Configuration error: {e}")
    print("Run: python scripts/setup_secrets.py")
except Exception as e:
    # API error or network issue
    print(f"Search failed: {e}")
```

## Testing

Run unit tests (no API key required - uses mocks):
```bash
python3 -m pytest tests/test_search_service.py -v
```

Run integration tests (requires API key):
```bash
ENABLE_LIVE_TESTS=1 python3 -m services.search_service
```

## API Rate Limits

Bing Search API v7 has rate limits based on your subscription tier:
- Free tier: 1,000 transactions/month
- S1 tier: 1,000 transactions/second

Best practices:
- Cache search results when possible
- Batch claim validation
- Use appropriate result counts (default: 10)

## Performance Tips

1. **Parallel claim validation**: Consider async/await for multiple claims
2. **Result caching**: Cache search results for common queries
3. **Batch processing**: Validate multiple outlines in batches
4. **Timeout handling**: Set appropriate timeouts for API calls (default: 10s)

