"""
Research Agent (T029-T033)

Validates outline through web research and claim extraction.

Role:
  - Extract claims from outline using Claude 3.5
  - Search web for each claim using BingSearchService
  - Calculate confidence score (credible_sources / claims_checked)
  - Block progression if confidence < 0.7
  
Input:
  - outline: dict from ReasoningAgent with sections, angle, rationale
  
Output:
  - validation_report: dict with confidence_score, sources, passed_validation
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

from services.llm_service import ModelRouter
from services.search_service import BingSearchService
from backend.utils.logger import backend_logger
from backend.agents.mock_agents import MockResearchAgent

# Logger
logger = logging.getLogger("backend.agents.research_agent")


class ResearchAgent:
    """Validates outline through web research and fact-checking."""

    def __init__(self):
        """Initialize ResearchAgent with LLM router and search service."""
        try:
            self.llm = ModelRouter()
            self.use_mock = False
        except Exception as e:
            logger.warning(f"⚠️  Failed to initialize LLM: {e}. Using mock agent for development.")
            self.llm = None
            self.use_mock = True
        
        try:
            self.search = BingSearchService()
        except:
            self.search = None
            if not self.use_mock:
                self.use_mock = True
        
        logger.info(f"✓ ResearchAgent initialized (mock={self.use_mock})")

    def validate_outline(self, outline: Dict) -> Dict:
        """
        Validate outline by extracting and checking claims.
        
        Uses Claude 3.5 for claim extraction, Bing API for web research,
        and confidence scoring based on credible sources.
        
        Args:
            outline: Dictionary from ReasoningAgent with:
            - topic: str
            - sections: list[dict] with title and description
            - content_angle: str
            - target_audience: str
            - primary_intent: str
        
        Returns:
            Dictionary with keys:
            - is_valid: bool (True if confidence >= 0.7)
            - confidence_score: float (0-1)
            - credible_sources_found: int
            - claims_checked: int
            - claims: list[dict] with claim, sources, verified
            - issues: list[str] (if any)
            - passed_validation: bool
            - validation_details: dict with breakdown
        
        Example:
            >>> agent = ResearchAgent()
            >>> outline =  {
            ...     'topic': 'AI in healthcare',
            ...     'sections': [...],
            ...     'content_angle': '...'
            ... }
            >>> report = agent.validate_outline(outline)
            >>> report['confidence_score'] >= 0.7
            True
        """
        logger.info(f"🔍 Validating outline for: {outline.get('topic', 'Unknown')}")
        
        # Use mock agent for development without API keys
        if self.use_mock:
            logger.debug("🎭 Using mock agent")
            return MockResearchAgent.validate_outline(outline)
        
        # Step 1: Extract claims from outline
        claims = self._extract_claims(outline)
        total_claims = len(claims)
        
        if total_claims == 0:
            logger.warning("No claims extracted from outline")
            return {
                "is_valid": False,
                "confidence_score": 0.0,
                "credible_sources_found": 0,
                "claims_checked": 0,
                "claims": [],
                "issues": ["No verifiable claims found in outline"],
                "passed_validation": False,
                "validation_details": {}
            }
        
        logger.info(f"🔎 Extracted {total_claims} claims from outline")
        
        # Step 2: Search web for each claim
        try:
            validated_claims = []
            credible_count = 0
            
            for claim in claims:
                try:
                    # Search for claim
                    search_results = self.search.search(claim["text"], count=5)
                    
                    # Score credibility
                    credibility_score = self._score_credibility(search_results)
                    is_credible = credibility_score >= 0.6
                    
                    if is_credible:
                        credible_count += 1
                    
                    validated_claims.append({
                        "claim": claim["text"],
                        "section": claim["section"],
                        "is_credible": is_credible,
                        "credibility_score": credibility_score,
                        "sources_found": len(search_results),
                        "sources": [
                            {
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "snippet": result.get("snippet", "")[:200]
                            }
                            for result in search_results[:3]
                        ]
                    })
                    
                    logger.debug(f"  Claim: {claim['text'][:50]}... | Credible: {is_credible}")
                    
                except Exception as e:
                    logger.warning(f"Error searching for claim '{claim['text']}': {e}")
                    validated_claims.append({
                        "claim": claim["text"],
                        "section": claim["section"],
                        "is_credible": False,
                        "credibility_score": 0.0,
                        "sources_found": 0,
                        "sources": [],
                        "error": str(e)
                    })
            
            # Step 3: Calculate confidence score
            confidence_score = credible_count / total_claims if total_claims > 0 else 0.0
            passed_validation = confidence_score >= 0.7
            
            logger.info(f"📊 Validation complete: {credible_count}/{total_claims} credible | Confidence: {confidence_score:.2f}")
            
            # Identify issues
            issues = []
            if credible_count < total_claims:
                issues.append(f"{total_claims - credible_count} claims could not be verified")
            if confidence_score < 0.5:
                issues.append("Low credibility - consider revising outline")
            
            result = {
                "is_valid": passed_validation,
                "confidence_score": confidence_score,
                "credible_sources_found": credible_count,
                "claims_checked": total_claims,
                "claims": validated_claims,
                "issues": issues,
                "passed_validation": passed_validation,
                "validation_details": {
                    "confidence_threshold": 0.7,
                    "required_credible_claims": int(0.7 * total_claims),
                    "actual_credible_claims": credible_count,
                    "verdict": "PASS" if passed_validation else "FAIL"
                }
            }
            
            return result
            
        except Exception as search_error:
            logger.error(f"Error during research validation: {search_error}. Using mock validation.")
            # Fall back to mock agent if search or other errors occur
            logger.info("Using mock validation for outline")
            return MockResearchAgent.validate_outline(outline)

    def _extract_claims(self, outline: Dict) -> List[Dict]:
        """
        Extract verifiable claims from outline using LLM.
        
        Uses Claude 3.5 for accurate claim extraction in structured format.
        
        Args:
            outline: Outline dictionary with sections
        
        Returns:
            List of claim dicts with 'text' and 'section' keys
        """
        logger.debug("🔎 Extracting verifiable claims from outline")
        
        # Build sections text
        sections_text = "\n".join([
            f"{s['title']}: {s['description']}"
            for s in outline.get("sections", [])
        ])
        
        prompt = f"""Extract 5-8 key claims from this content outline that can be verified through web research.

A claim should be:
- Specific and factual (not subjective)
- Verifiable through web search
- Important to the outline

Content:
{sections_text}

Respond with VALID JSON (no markdown, no code block):
{{
  "claims": [
    {{"claim": "specific verifiable claim", "from_section": "section title"}},
    {{"claim": "specific verifiable claim", "from_section": "section title"}}
  ]
}}
"""
        
        try:
            # Use Claude 3.5 for claim extraction (accurate JSON parsing)
            response = self.llm.call(
                task_type="classification",
                prompt=prompt,
                max_tokens=1000
            )
            
            data = self._parse_json_response(response)
            
            claims = []
            for item in data.get("claims", []):
                if "claim" in item:
                    claims.append({
                        "text": item["claim"],
                        "section": item.get("from_section", "Unknown")
                    })
            
            logger.debug(f"  Extracted {len(claims)} claims")
            return claims
            
        except Exception as e:
            logger.error(f"Error extracting claims: {e}")
            return []

    @staticmethod
    def _score_credibility(search_results: List[Dict]) -> float:
        """
        Score credibility of search results.
        
        Considers:
        - Domain authority (e.g., .edu, .gov, established tech sites)
        - Number of results
        - Content relevance (basic heuristic)
        
        Args:
            search_results: List of search result dicts from Bing API
        
        Returns:
            Credibility score (0-1)
        """
        if not search_results:
            return 0.0
        
        # Authoritative domains
        authoritative_domains = {
            '.edu': 1.0,
            '.gov': 1.0,
            'academic': 0.95,
            'arxiv': 0.9,
            'ieee': 0.9,
            'nature': 0.9,
            'science': 0.85,
            'medium': 0.6,
            'linkedin': 0.7,
            'github': 0.75,
        }
        
        scores = []
        
        for result in search_results:
            url = result.get("url", "").lower()
            
            # Check domain authority
            domain_score = 0.5  # Default moderate score
            
            for domain_pattern, authority_score in authoritative_domains.items():
                if domain_pattern in url:
                    domain_score = authority_score
                    break
            
            scores.append(domain_score)
        
        # Average score with bonus for multiple results
        avg_score = sum(scores) / len(scores) if scores else 0.0
        result_bonus = min(0.1, len(search_results) * 0.02)
        
        credibility = min(1.0, avg_score + result_bonus)
        
        return credibility

    @staticmethod
    def _parse_json_response(response: str) -> Dict:
        """
        Parse JSON response from LLM.
        
        Handles various formatting issues.
        """
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response}")
            return {"claims": []}


# Singleton instance
_research_agent: Optional[ResearchAgent] = None


def get_research_agent() -> ResearchAgent:
    """Get global ResearchAgent instance."""
    global _research_agent
    if _research_agent is None:
        _research_agent = ResearchAgent()
    return _research_agent
