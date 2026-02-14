"""
Input Agent (T021-T024)

Extracts topic information from user input and classifies against focus areas.

Role:
  - Extract topic, audience, intent from user input
  - Match to focus areas (AI, Cloud, Migration, Emotional Intelligence, Emerging Tech)
  - Warn if OUT_OF_SCOPE but allow override
  
Input:
  - topic: str (user-provided topic)
  
Output:
  - topic_data: dict with theme, audience, intent, focus_area, is_out_of_scope
"""

import json
import logging
from typing import Dict, Optional, Tuple

from services.llm_service import ModelRouter
from backend.utils.reference_data import get_reference_data
from backend.utils.logger import backend_logger
from backend.agents.mock_agents import MockInputAgent

# Logger
logger = logging.getLogger("backend.agents.input_agent")


class InputAgent:
    """Extracts and classifies topic metadata."""

    def __init__(self):
        """Initialize InputAgent with LLM router and reference data."""
        try:
            self.llm = ModelRouter()
            self.use_mock = False
        except Exception as e:
            logger.warning(f"⚠️  Failed to initialize LLM: {e}. Using mock agent for development.")
            self.llm = None
            self.use_mock = True
        
        self.reference_data = get_reference_data()
        logger.info(f"✓ InputAgent initialized (mock={self.use_mock})")

    def extract_topic_info(self, topic: str) -> Dict:
        """
        Extract topic information using LLM classification.
        
        Uses Llama 3.1 for cost-effective topic extraction.
        Falls back to mock agent if API not available.
        
        Args:
            topic: User-provided topic (e.g., "AI in healthcare", "Financial independence")
        
        Returns:
            Dictionary with keys:
            - topic: str (original topic)
            - theme: str (what this is really about)
            - audience: str (target audience)
            - intent: str (inform, persuade, entertain, guide, challenge)
            - focus_area: str (matched focus area ID or "OUT_OF_SCOPE")
            - is_out_of_scope: bool
            - warning: str or None
            - confidence: float (0-1)
        
        Example:
            >>> agent = InputAgent()
            >>> result = agent.extract_topic_info("AI in healthcare")
            >>> result['theme']
            'How artificial intelligence is transforming medical diagnosis and treatment'
        """
        logger.info(f"🔍 Extracting topic info from: {topic}")
        
        # Use mock agent for development without API keys
        if self.use_mock:
            logger.debug("🎭 Using mock agent")
            mock_result = MockInputAgent.extract_topic_info(topic)
            mock_result["topic"] = topic
            focus_area, confidence = self.match_focus_area(mock_result.get("focus_area", "AI"))
            mock_result["focus_area"] = focus_area
            mock_result["is_out_of_scope"] = focus_area == "OUT_OF_SCOPE"
            mock_result["confidence"] = confidence
            return mock_result
        
        # Prompt LLM to extract topic metadata
        prompt = self._build_extraction_prompt(topic)
        
        try:
            # Use Llama 3.1 for classification (cost-effective)
            response = self.llm.call(
                task_type="classification",
                prompt=prompt,
                max_tokens=500
            )
            
            # Parse JSON response
            extracted = self._parse_json_response(response)
            
            # Match to focus areas
            focus_area, confidence = self.match_focus_area(extracted.get("detected_focus_area", ""))
            
            # Determine if out of scope
            is_out_of_scope = focus_area == "OUT_OF_SCOPE"
            warning = None
            if is_out_of_scope:
                warning = f"Topic '{topic}' does not match any focus area. Override allowed."
                logger.warning(f"⚠ OUT_OF_SCOPE: {warning}")
            
            # Build result
            result = {
                "topic": topic,
                "theme": extracted.get("theme", ""),
                "audience": extracted.get("audience", ""),
                "intent": extracted.get("intent", "").lower(),
                "focus_area": focus_area,
                "is_out_of_scope": is_out_of_scope,
                "warning": warning,
                "confidence": confidence,
                "detected_focus_area_raw": extracted.get("detected_focus_area", "Unknown")
            }
            
            logger.info(f"✓ Extraction complete: focus_area={focus_area}, confidence={confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to extract topic info: {e}. Falling back to mock agent.")
            # Fall back to mock agent if LLM call fails
            mock_result = MockInputAgent.extract_topic_info(topic)
            mock_result["topic"] = topic
            focus_area, confidence = self.match_focus_area(mock_result.get("focus_area", "AI"))
            mock_result["focus_area"] = focus_area
            mock_result["is_out_of_scope"] = focus_area == "OUT_OF_SCOPE"
            mock_result["confidence"] = confidence
            logger.info(f"✓ Using mock extraction for topic: {topic}")
            return mock_result

    def match_focus_area(self, detected_area: str) -> Tuple[str, float]:
        """
        Match detected focus area to reference data.
        
        Uses keyword matching against available focus areas.
        
        Args:
            detected_area: Focus area detected by LLM (e.g., "AI", "Cloud", "Migration")
        
        Returns:
            Tuple of (focus_area_id, confidence)
            - focus_area_id: str (ID from reference data or "OUT_OF_SCOPE")
            - confidence: float (0-1, based on match quality)
        
        Example:
            >>> agent = InputAgent()
            >>> area, conf = agent.match_focus_area("Artificial Intelligence")
            >>> area, conf
            ('AI', 0.95)
        """
        logger.debug(f"🎯 Matching focus area: {detected_area}")
        
        if not detected_area or detected_area.lower() in ["unknown", "none", ""]:
            logger.debug("No focus area detected")
            return "OUT_OF_SCOPE", 0.0
        
        detected_lower = detected_area.lower()
        
        # Get active focus areas from reference data
        focus_areas = self.reference_data.get_focus_areas(active_only=True)
        
        if not focus_areas:
            logger.warning("No active focus areas found in reference data")
            return "OUT_OF_SCOPE", 0.0
        
        # Build keyword mappings
        focus_keywords = {
            "ai": ["artificial intelligence", "ai", "machine learning", "deep learning", "neural", "llm"],
            "cloud": ["cloud", "azure", "aws", "gcp", "serverless", "containers", "kubernetes"],
            "migration": ["migration", "modernization", "upgrade", "refactor", "transformation"],
            "emotional_intelligence": ["emotional", "empathy", "wellness", "mental health", "leadership", "relationship"],
            "emerging_tech": ["quantum", "blockchain", "metaverse", "iot", "edge", "5g", "ar", "vr"]
        }
        
        best_match = None
        best_score = 0.0
        
        # Try to match detected area to focus areas
        for focus_area in focus_areas:
            area_id = focus_area["id"]
            area_name = focus_area["name"].lower()
            
            # Direct name match
            if area_name == detected_lower:
                return area_id, 1.0
            
            # Keyword matching
            keywords = focus_keywords.get(area_id.lower(), [])
            for keyword in keywords:
                if keyword in detected_lower or detected_lower in keyword:
                    score = 0.9 if keyword == detected_lower else 0.7
                    if score > best_score:
                        best_score = score
                        best_match = area_id
            
            # Partial name match in detected area
            if area_name in detected_lower and best_score < 0.8:
                best_score = 0.8
                best_match = area_id
        
        if best_match:
            logger.debug(f"✓ Matched to {best_match} (confidence: {best_score:.2f})")
            return best_match, best_score
        
        logger.debug(f"No match found for '{detected_area}'")
        return "OUT_OF_SCOPE", 0.0

    def _build_extraction_prompt(self, topic: str) -> str:
        """Build LLM prompt for topic extraction."""
        return f"""Extract the core information from this topic:
"{topic}"

Respond with VALID JSON (no markdown, no code block):
{{
  "theme": "single-sentence summary of what this is really about",
  "audience": "target audience (e.g., 'Educators and administrators', 'Software engineers')",
  "intent": "primary intent (educate/persuade/entertain/guide/challenge)",
  "detected_focus_area": "likely focus area (AI, Cloud, Migration, Emotional Intelligence, Emerging Tech, or 'Unknown')"
}}
"""

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
            # Return empty structure with defaults
            return {
                "theme": "",
                "audience": "",
                "intent": "inform",
                "detected_focus_area": "Unknown"
            }


# Singleton instance
_input_agent: Optional[InputAgent] = None


def get_input_agent() -> InputAgent:
    """Get global InputAgent instance."""
    global _input_agent
    if _input_agent is None:
        _input_agent = InputAgent()
    return _input_agent
