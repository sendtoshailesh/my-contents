"""
Reasoning Agent (T025-T028)

Generates compelling content outline from topic metadata.

Role:
  - Generate outline structure from topic data using GPT-4 Turbo
  - Create 4-6 outline sections with titles and descriptions
  - Specify content_angle and target audience
  - Return structured outline with all fields
  
Input:
  - topic_data: dict from InputAgent with theme, audience, intent, focus_area
  
Output:
  - outline: dict with sections, angle, audience, intent
"""

import json
import logging
from typing import Dict, List, Optional

from services.llm_service import ModelRouter
from backend.utils.logger import backend_logger
from backend.agents.mock_agents import MockReasoningAgent

# Logger
logger = logging.getLogger("backend.agents.reasoning_agent")


class ReasoningAgent:
    """Generates content outlines using advanced reasoning."""

    def __init__(self):
        """Initialize ReasoningAgent with LLM router."""
        try:
            self.llm = ModelRouter()
            self.use_mock = False
        except Exception as e:
            logger.warning(f"⚠️  Failed to initialize LLM: {e}. Using mock agent for development.")
            self.llm = None
            self.use_mock = True
        logger.info(f"✓ ReasoningAgent initialized (mock={self.use_mock})")

    def generate_outline(self, topic_data: Dict) -> Dict:
        """
        Generate detailed content outline from topic data.
        
        Uses GPT-4 Turbo for complex reasoning and outline generation.
        
        Args:
            topic_data: Dictionary from InputAgent with keys:
            - topic: str
            - theme: str (what this is really about)
            - audience: str (target audience)
            - intent: str (inform, persuade, entertain, guide, challenge)
            - focus_area: str (focus area ID or "OUT_OF_SCOPE")
            - is_out_of_scope: bool
        
        Returns:
            Dictionary with keys:
            - topic: str
            - sections: list[dict] with 'title', 'description', 'order'
            - content_angle: str (why this angle matters)
            - target_audience: str
            - primary_intent: str
            - num_sections: int
            - outline_rationale: str (explanation of structure)
        
        Example:
            >>> agent = ReasoningAgent()
            >>> topic_data = {
            ...     'topic': 'AI in healthcare',
            ...     'theme': 'How AI is transforming medical diagnosis',
            ...     'audience': 'Hospital administrators',
            ...     'intent': 'inform',
            ...     'focus_area': 'AI'
            ... }
            >>> outline = agent.generate_outline(topic_data)
            >>> len(outline['sections'])
            5
        """
        logger.info(f"🧠 Generating outline for: {topic_data.get('topic', 'Unknown')}")
        
        # Use mock agent for development without API keys
        if self.use_mock:
            logger.debug("🎭 Using mock agent")
            return MockReasoningAgent.generate_outline(topic_data)
        
        # Build prompt for GPT-4 Turbo
        prompt = self._build_outline_prompt(topic_data)
        
        try:
            # Use GPT-4 Turbo for reasoning (complex outline generation)
            response = self.llm.call(
                task_type="reasoning",
                prompt=prompt,
                max_tokens=1500
            )
            
            # Parse JSON response
            outline_data = self._parse_json_response(response)
            
            # Build result with sections
            sections = []
            for i, section in enumerate(outline_data.get("sections", []), 1):
                sections.append({
                    "title": section.get("title", f"Section {i}"),
                    "description": section.get("description", ""),
                    "order": i
                })
            
            result = {
                "topic": topic_data.get("topic", ""),
                "sections": sections,
                "content_angle": outline_data.get("content_angle", ""),
                "target_audience": topic_data.get("audience", ""),
                "primary_intent": topic_data.get("intent", "inform"),
                "num_sections": len(sections),
                "outline_rationale": outline_data.get("outline_rationale", ""),
                "why_this_matters": outline_data.get("why_this_matters", "")
            }
            
            logger.info(f"✓ Outline generated: {result['num_sections']} sections")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to generate outline: {e}. Falling back to mock agent.")
            # Fall back to mock agent if LLM call fails
            logger.info(f"✓ Using mock outline for topic: {topic_data.get('topic')}")
            return MockReasoningAgent.generate_outline(topic_data)

    def _build_outline_prompt(self, topic_data: Dict) -> str:
        """Build LLM prompt for outline generation."""
        return f"""Create a compelling outline for this content:

Topic: {topic_data.get('topic', 'Unknown')}
Theme: {topic_data.get('theme', 'Not provided')}
Target Audience: {topic_data.get('audience', 'General audience')}
Primary Intent: {topic_data.get('intent', 'inform')}
Focus Area: {topic_data.get('focus_area', 'General')}

Generate 4-6 outline sections. Each section should:
1. Have a clear, descriptive title
2. Include a brief description explaining what will be covered
3. Build logically from the previous section

Also explain:
- Why this content angle is compelling
- What makes this approach different or unique
- How the structure maps to the primary intent

Respond with VALID JSON (no markdown, no code block):
{{
  "content_angle": "single compelling reason why this angle works for the audience",
  "why_this_matters": "explanation of why this topic/angle matters now",
  "outline_rationale": "explanation of why this section structure works",
  "sections": [
    {{"title": "Section title", "description": "brief description (1-2 sentences)"}},
    {{"title": "Section title", "description": "brief description (1-2 sentences)"}},
    {{"title": "Section title", "description": "brief description (1-2 sentences)"}}
  ]
}}
"""

    @staticmethod
    def _parse_json_response(response: str) -> Dict:
        """
        Parse JSON response from LLM.
        
        Handles various formatting issues and validates structure.
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
            parsed = json.loads(response)
            
            # Validate required fields
            if "sections" not in parsed:
                parsed["sections"] = []
            if "content_angle" not in parsed:
                parsed["content_angle"] = ""
            if "why_this_matters" not in parsed:
                parsed["why_this_matters"] = ""
            if "outline_rationale" not in parsed:
                parsed["outline_rationale"] = ""
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response}")
            # Return empty structure with defaults
            return {
                "content_angle": "",
                "why_this_matters": "",
                "outline_rationale": "",
                "sections": []
            }

    def validate_outline(self, outline: Dict) -> bool:
        """
        Validate outline structure.
        
        Args:
            outline: Outline dictionary
        
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["topic", "sections", "content_angle", "target_audience", "primary_intent"]
        
        for field in required_fields:
            if field not in outline:
                logger.warning(f"Missing required field in outline: {field}")
                return False
        
        if not isinstance(outline["sections"], list) or len(outline["sections"]) < 4:
            logger.warning(f"Outline must have at least 4 sections, got {len(outline.get('sections', []))}")
            return False
        
        # Validate each section
        for i, section in enumerate(outline["sections"]):
            if not isinstance(section, dict) or "title" not in section or "description" not in section:
                logger.warning(f"Section {i} missing required fields (title, description)")
                return False
        
        return True


# Singleton instance
_reasoning_agent: Optional[ReasoningAgent] = None


def get_reasoning_agent() -> ReasoningAgent:
    """Get global ReasoningAgent instance."""
    global _reasoning_agent
    if _reasoning_agent is None:
        _reasoning_agent = ReasoningAgent()
    return _reasoning_agent
