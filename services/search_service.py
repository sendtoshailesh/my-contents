"""
Web Search and Credibility Scoring Service

Validates claims in outlines by performing web searches and scoring credibility.

Features:
  - Bing Search API v7 integration
  - Domain credibility scoring (.edu, .gov, .org, .com, etc.)
  - Claim extraction using Claude 3.5
  - Outline validation with confidence scoring

Usage:
    from services.search_service import BingSearchService
    
    search_service = BingSearchService()
    
    # Perform web search
    results = search_service.search("AI content generation", count=10)
    
    # Validate outline
    report = search_service.validate_outline(outline_text)
    print(f"Confidence: {report['confidence']}")
    print(f"Passed: {report['passed']}")
"""

import json
import logging
import os
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse

from services.llm_service import ModelRouter
from services.secrets_service import get_secrets_service

# Initialize logger
logger = logging.getLogger("backend.services.search")


class BingSearchService:
    """Web search and credibility scoring using Bing Search API v7."""

    # Bing Search API configuration
    BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
    DEFAULT_MARKET = "en-US"
    DEFAULT_SAFE_SEARCH = "Moderate"
    
    # Credibility scoring by domain type
    CREDIBILITY_SCORES = {
        # High credibility (0.9)
        ".edu": 0.9,
        ".gov": 0.9,
        ".mil": 0.9,
        
        # Medium-high credibility (0.7) - reputable organizations and major news
        ".org": 0.7,
        "cnn.com": 0.7,
        "bbc.com": 0.7,
        "bbc.co.uk": 0.7,
        "reuters.com": 0.7,
        "apnews.com": 0.7,
        "nytimes.com": 0.7,
        "washingtonpost.com": 0.7,
        "theguardian.com": 0.7,
        "npr.org": 0.7,
        "nature.com": 0.7,
        "sciencemag.org": 0.7,
        "nih.gov": 0.9,  # Override for specific gov sites
        "cdc.gov": 0.9,
        "who.int": 0.7,
        
        # Medium credibility (0.5) - general commercial sites
        ".com": 0.5,
        ".net": 0.5,
        
        # Low credibility (0.3) - other/unknown
        "default": 0.3,
    }
    
    # Minimum sources required per claim
    MIN_SOURCES_PER_CLAIM = 2
    
    # Validation thresholds
    PASS_THRESHOLD = 0.7

    def __init__(self):
        """Initialize BingSearchService with API key and LLM router."""
        logger.info("🔍 Initializing BingSearchService...")
        
        # Get Bing Search API key from secrets
        self.secrets_service = get_secrets_service()
        self.bing_api_key = self.secrets_service.get("bing-search-key", required=True)
        
        # Initialize ModelRouter for claim extraction
        self.model_router = ModelRouter()
        
        logger.info("✓ BingSearchService initialized")

    def search(self, query: str, count: int = 10) -> List[Dict]:
        """
        Perform Bing web search.
        
        Args:
            query: Search query
            count: Number of results to return (default: 10)
        
        Returns:
            List of search results with:
              - title: Result title
              - url: Result URL
              - snippet: Text snippet
              - credibility: Credibility score (0.0-1.0)
        
        Raises:
            Exception: If Bing API call fails
        """
        logger.info(f"🔎 Searching Bing for: '{query}' (count={count})")
        
        # Prepare headers
        headers = {
            "Ocp-Apim-Subscription-Key": self.bing_api_key,
        }
        
        # Prepare query parameters
        params = {
            "q": query,
            "count": count,
            "mkt": self.DEFAULT_MARKET,
            "safeSearch": self.DEFAULT_SAFE_SEARCH,
            "textDecorations": True,
            "textFormat": "HTML",
        }
        
        try:
            # Make API request
            response = requests.get(
                self.BING_ENDPOINT,
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            web_pages = data.get("webPages", {})
            raw_results = web_pages.get("value", [])
            
            # Format results with credibility scores
            results = []
            for item in raw_results:
                url = item.get("url", "")
                credibility = self.calculate_credibility(url)
                
                result = {
                    "title": item.get("name", ""),
                    "url": url,
                    "snippet": item.get("snippet", ""),
                    "credibility": credibility,
                }
                results.append(result)
            
            logger.info(f"✓ Found {len(results)} results")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Bing API request failed: {e}")
            raise Exception(f"Bing search failed: {e}")
        except Exception as e:
            logger.error(f"❌ Error processing search results: {e}")
            raise

    def calculate_credibility(self, url: str) -> float:
        """
        Calculate credibility score based on domain.
        
        Args:
            url: URL to score
        
        Returns:
            Credibility score:
              - 0.9 for .edu, .gov, .mil
              - 0.7 for .org, major news sites
              - 0.5 for .com, .net
              - 0.3 for others
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove 'www.' prefix
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Check specific domains first (exact match)
            if domain in self.CREDIBILITY_SCORES:
                score = self.CREDIBILITY_SCORES[domain]
                logger.debug(f"Domain '{domain}' → credibility {score}")
                return score
            
            # Check TLD (top-level domain)
            for tld, score in self.CREDIBILITY_SCORES.items():
                if tld.startswith(".") and domain.endswith(tld):
                    logger.debug(f"TLD '{tld}' → credibility {score}")
                    return score
            
            # Default score
            score = self.CREDIBILITY_SCORES["default"]
            logger.debug(f"Domain '{domain}' → default credibility {score}")
            return score
            
        except Exception as e:
            logger.warning(f"Error parsing URL '{url}': {e}")
            return self.CREDIBILITY_SCORES["default"]

    def extract_claims(self, text: str) -> List[str]:
        """
        Extract factual claims from text using Claude 3.5.
        
        Uses structured output to get JSON array of claims.
        
        Args:
            text: Text to extract claims from
        
        Returns:
            List of claim statements
        
        Raises:
            Exception: If claim extraction fails
        """
        logger.info("📋 Extracting claims from text...")
        
        # Construct prompt for claim extraction
        prompt = f"""Extract all factual claims from the following text that can be fact-checked using web sources.

Return ONLY a JSON array of strings, where each string is a single factual claim.
Do not include opinions, subjective statements, or claims that cannot be verified.

Format your response as a valid JSON array like this:
["claim 1", "claim 2", "claim 3"]

Text to analyze:
{text}

Return only the JSON array, no additional text or explanation."""

        try:
            # Use structured task type for JSON output
            response = self.model_router.call(
                task_type="structured",
                prompt=prompt,
                temperature=0.3,  # Low temperature for factual extraction
                max_tokens=2048
            )
            
            # Parse JSON response
            # Clean response (remove markdown code blocks if present)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse JSON
            claims = json.loads(cleaned_response)
            
            if not isinstance(claims, list):
                raise ValueError("Expected JSON array of claims")
            
            logger.info(f"✓ Extracted {len(claims)} claims")
            return claims
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response}")
            raise Exception(f"Claim extraction failed: Invalid JSON response")
        except Exception as e:
            logger.error(f"❌ Claim extraction failed: {e}")
            raise

    def validate_outline(self, outline_text: str) -> Dict:
        """
        Validate outline by checking claims against web sources.
        
        Process:
        1. Extract claims from outline text using Claude
        2. For each claim, search Bing for supporting sources
        3. Calculate credibility score based on sources found
        4. Return validation report
        
        Args:
            outline_text: Outline content to validate
        
        Returns:
            {
                'claims': List[str] - Extracted claims,
                'sources': List[Dict] - URLs with credibility scores,
                'confidence': float - credible_sources / claims_checked,
                'passed': bool - True if confidence >= 0.7,
                'details': List[Dict] - Per-claim validation details
            }
        """
        logger.info("✅ Starting outline validation...")
        
        try:
            # Step 1: Extract claims
            claims = self.extract_claims(outline_text)
            
            if not claims:
                logger.warning("⚠ No claims extracted from outline")
                return {
                    "claims": [],
                    "sources": [],
                    "confidence": 0.0,
                    "passed": False,
                    "details": [],
                }
            
            # Step 2: Validate each claim
            all_sources = []
            claim_details = []
            total_credible_sources = 0
            
            for i, claim in enumerate(claims, 1):
                logger.info(f"📝 Validating claim {i}/{len(claims)}: {claim[:80]}...")
                
                # Search for sources
                try:
                    results = self.search(claim, count=10)
                except Exception as e:
                    logger.warning(f"Search failed for claim: {e}")
                    results = []
                
                # Filter sources by credibility (≥ 0.5)
                credible_sources = [r for r in results if r["credibility"] >= 0.5]
                
                # Track sources
                all_sources.extend(credible_sources)
                
                # Calculate claim validation status
                claim_passed = len(credible_sources) >= self.MIN_SOURCES_PER_CLAIM
                total_credible_sources += len(credible_sources)
                
                claim_detail = {
                    "claim": claim,
                    "sources_found": len(credible_sources),
                    "passed": claim_passed,
                    "top_sources": credible_sources[:3],  # Top 3 for reference
                }
                claim_details.append(claim_detail)
                
                logger.info(
                    f"  → Found {len(credible_sources)} credible sources "
                    f"({'PASS' if claim_passed else 'FAIL'})"
                )
            
            # Step 3: Calculate overall confidence
            # Confidence = average credible sources per claim
            confidence = total_credible_sources / len(claims) if claims else 0.0
            
            # Normalize confidence to 0-1 scale (cap at 1.0)
            # Having 2+ sources per claim = 100% confidence
            confidence = min(confidence / self.MIN_SOURCES_PER_CLAIM, 1.0)
            
            # Determine pass/fail
            passed = confidence >= self.PASS_THRESHOLD
            
            # Build validation report
            report = {
                "claims": claims,
                "sources": all_sources,
                "confidence": round(confidence, 2),
                "passed": passed,
                "details": claim_details,
            }
            
            logger.info(
                f"✓ Validation complete: {len(claims)} claims, "
                f"{total_credible_sources} sources, "
                f"confidence={confidence:.2f}, "
                f"{'PASSED' if passed else 'FAILED'}"
            )
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Outline validation failed: {e}")
            raise


# Singleton instance
_bing_search_service: Optional[BingSearchService] = None


def get_bing_search_service() -> BingSearchService:
    """Get global BingSearchService instance."""
    global _bing_search_service
    if _bing_search_service is None:
        _bing_search_service = BingSearchService()
    return _bing_search_service


# Example usage and testing
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add repo root to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 70)
    print("🔍 BING SEARCH SERVICE TEST")
    print("=" * 70)
    
    # Initialize service
    try:
        search_service = BingSearchService()
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        print("   Make sure to run: python scripts/setup_secrets.py")
        sys.exit(1)
    
    # Test 1: Domain credibility scoring
    print("\n🎯 Test 1: Domain Credibility Scoring")
    print("-" * 70)
    test_urls = [
        "https://www.stanford.edu/research/ai",
        "https://www.cdc.gov/health",
        "https://www.nature.com/articles/science",
        "https://www.bbc.com/news",
        "https://www.example.com/blog",
        "https://random-site.xyz/info",
    ]
    for url in test_urls:
        score = search_service.calculate_credibility(url)
        print(f"  {url:50s} → {score:.1f}")
    
    # Test 2: Web search (mock mode - don't call real API in automated tests)
    print("\n🔎 Test 2: Web Search")
    print("-" * 70)
    print("Skipping live search test (set ENABLE_LIVE_TESTS=1 to enable)")
    
    # Only run live tests if explicitly enabled
    if os.environ.get("ENABLE_LIVE_TESTS") == "1":
        try:
            results = search_service.search("artificial intelligence", count=5)
            print(f"✓ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n  {i}. {result['title']}")
                print(f"     URL: {result['url']}")
                print(f"     Credibility: {result['credibility']:.2f}")
                print(f"     Snippet: {result['snippet'][:100]}...")
        except Exception as e:
            print(f"❌ Search test failed: {e}")
    
    # Test 3: Claim extraction (mock mode)
    print("\n📋 Test 3: Claim Extraction")
    print("-" * 70)
    sample_text = """
    Python is a high-level programming language that was created by Guido van Rossum.
    It is widely used for data science and machine learning applications.
    The language was first released in 1991.
    """
    print(f"Sample text: {sample_text.strip()}")
    print("\nSkipping live claim extraction (set ENABLE_LIVE_TESTS=1 to enable)")
    
    if os.environ.get("ENABLE_LIVE_TESTS") == "1":
        try:
            claims = search_service.extract_claims(sample_text)
            print(f"✓ Extracted {len(claims)} claims:")
            for i, claim in enumerate(claims, 1):
                print(f"  {i}. {claim}")
        except Exception as e:
            print(f"❌ Claim extraction test failed: {e}")
    
    # Test 4: Outline validation (mock mode)
    print("\n✅ Test 4: Outline Validation")
    print("-" * 70)
    sample_outline = """
    # The History of Python Programming Language
    
    ## Introduction
    Python was created by Guido van Rossum and first released in 1991.
    The language emphasizes code readability with significant whitespace.
    
    ## Popularity
    Python is one of the most popular programming languages in the world.
    It is widely used in data science, machine learning, and web development.
    """
    print(f"Sample outline:\n{sample_outline}")
    print("\nSkipping live validation (set ENABLE_LIVE_TESTS=1 to enable)")
    
    if os.environ.get("ENABLE_LIVE_TESTS") == "1":
        try:
            report = search_service.validate_outline(sample_outline)
            print(f"\n✓ Validation Report:")
            print(f"   Claims checked: {len(report['claims'])}")
            print(f"   Sources found: {len(report['sources'])}")
            print(f"   Confidence: {report['confidence']}")
            print(f"   Status: {'PASSED' if report['passed'] else 'FAILED'}")
            
            print(f"\n   Claims:")
            for detail in report['details']:
                status = "✓" if detail['passed'] else "✗"
                print(f"   {status} {detail['claim'][:60]}... ({detail['sources_found']} sources)")
        except Exception as e:
            print(f"❌ Validation test failed: {e}")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    print("\nTo run live API tests:")
    print("  ENABLE_LIVE_TESTS=1 python3 -m services.search_service")
    print("=" * 70)

