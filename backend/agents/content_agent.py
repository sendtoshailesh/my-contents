"""
Content Agent (US2)
Generates a narrative draft using framework structure and visuals.
"""

from typing import Dict, List, Optional
import logging

from backend.agents.mock_agents import MockContentAgent

logger = logging.getLogger("backend.agents.content")


class ContentAgent:
    """Generates the content draft for a session."""

    def generate_content(
        self,
        outline: Dict,
        framework_choice: str,
        framework_structure: List[Dict],
        visual_plan: List[Dict],
        include_code: bool = False
    ) -> Dict:
        """Create a structured narrative draft."""
        title = outline.get("content_angle") or outline.get("topic") or "Generated Content"
        body_lines = [f"# {title}", "", "## Overview", "", "This draft follows the selected framework."]

        for step in framework_structure:
            section_title = step.get("title") or step.get("framework_step") or "Section"
            body_lines.append("")
            body_lines.append(f"## {section_title}")
            body_lines.append("Key points, examples, and context go here.")

            visual_ref = self._find_visual_for_section(visual_plan, step)
            if visual_ref:
                body_lines.append("")
                body_lines.append(f"[See Visual {visual_ref['visual_id']}: {visual_ref['description']}] ")

        code_snippets = []
        if include_code:
            code_snippets.append({
                "section": 2,
                "language": "python",
                "code": "def outline_summary(topic):\n    return f'Key takeaways about {topic}'",
                "explanation": "Simple helper to illustrate a summary routine.",
                "expected_output": "Key takeaways about <topic>"
            })

        return {
            "framework_choice": framework_choice,
            "body_text": "\n".join(body_lines),
            "visual_integration_points": [],
            "code_snippets": code_snippets,
            "content_quality_score": 0.8,
            "warnings": []
        }

    @staticmethod
    def _find_visual_for_section(visual_plan: List[Dict], step: Dict) -> Optional[Dict]:
        location = step.get("outline_section")
        if not location:
            return None

        for visual in visual_plan:
            if str(location) in str(visual.get("location", "")):
                return visual
        return None


_content_agent = None


def get_content_agent() -> ContentAgent:
    """Get a singleton content agent instance."""
    global _content_agent
    if _content_agent is None:
        try:
            _content_agent = ContentAgent()
        except Exception as exc:
            logger.warning("Falling back to MockContentAgent: %s", exc)
            _content_agent = MockContentAgent()
    return _content_agent
