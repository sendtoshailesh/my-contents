"""
Storytelling Agent (US2)
Applies a framework and generates a visual plan.
"""

from typing import Dict, List, Optional
import logging

from services.framework_engine import get_framework_engine
from backend.utils.reference_data import get_reference_data
from backend.agents.mock_agents import MockStorytellingAgent

logger = logging.getLogger("backend.agents.storytelling")


class StorytellingAgent:
    """Applies a storytelling framework and proposes visuals."""

    def __init__(self):
        self.framework_engine = get_framework_engine()
        self.reference_data = get_reference_data()

    def recommend_framework(self, outline: Dict) -> str:
        """Recommend a framework based on outline heuristics."""
        return self.framework_engine.recommend_framework(outline)

    def generate_framework_plan(
        self,
        outline: Dict,
        framework_choice: Optional[str] = None,
        visual_opt_in: bool = True,
        visual_preferences: Optional[List[str]] = None,
    ) -> Dict:
        """Generate framework mapping and visual plan."""
        if not framework_choice:
            framework_choice = self.recommend_framework(outline)

        outline_sections = self._extract_section_titles(outline.get("sections", []))
        framework_structure = self.framework_engine.map_outline_to_framework(
            outline_sections=outline_sections,
            framework_id=framework_choice
        )

        visual_plan = self._build_visual_plan(
            outline_sections=outline_sections,
            visual_opt_in=visual_opt_in,
            visual_preferences=visual_preferences
        )

        return {
            "framework_choice": framework_choice,
            "framework_explanation": self._framework_explanation(framework_choice),
            "framework_structure": framework_structure,
            "visual_plan": visual_plan,
            "total_visuals": len(visual_plan),
            "opt_out_visuals": not visual_opt_in
        }

    def _build_visual_plan(
        self,
        outline_sections: List[str],
        visual_opt_in: bool,
        visual_preferences: Optional[List[str]]
    ) -> List[Dict]:
        if not visual_opt_in:
            return []

        visual_types = self.reference_data.get_visual_types()
        if visual_preferences:
            preferred = {v.lower() for v in visual_preferences}
            visual_types = [v for v in visual_types if v["id"].lower() in preferred or v["name"].lower() in preferred]

        if not visual_types:
            visual_types = self.reference_data.get_visual_types()

        mermaid_types = [v for v in visual_types if v.get("mermaid_capable")]
        pool = mermaid_types or visual_types
        target_count = min(3, max(1, len(outline_sections)))

        visuals = []
        for i in range(target_count):
            visual_type = pool[i % len(pool)]
            section_index = min(i + 1, max(1, len(outline_sections)))
            visuals.append({
                "visual_id": i + 1,
                "type": visual_type["name"].lower(),
                "location": f"section_{section_index}",
                "recommended_tool": "mermaid" if visual_type.get("mermaid_capable") else "svg",
                "description": f"Visual summary for {outline_sections[section_index - 1]}",
                "draft_code": self._default_mermaid_code(outline_sections, section_index)
            })

        return visuals

    @staticmethod
    def _extract_section_titles(sections: List[Dict]) -> List[str]:
        titles = []
        for section in sections:
            if isinstance(section, dict):
                titles.append(section.get("title", "Untitled"))
            else:
                titles.append(str(section))
        return titles

    @staticmethod
    def _framework_explanation(framework_choice: str) -> str:
        return f"Selected {framework_choice} for a clear narrative arc and progression."

    @staticmethod
    def _default_mermaid_code(outline_sections: List[str], section_index: int) -> str:
        if len(outline_sections) < 2:
            return "flowchart LR\n  A[Idea] --> B[Impact]"

        left = outline_sections[0][:24]
        right = outline_sections[min(section_index, len(outline_sections)) - 1][:24]
        return f"flowchart LR\n  A[{left}] --> B[{right}]"


_storytelling_agent = None


def get_storytelling_agent() -> StorytellingAgent:
    """Get a singleton storytelling agent instance."""
    global _storytelling_agent
    if _storytelling_agent is None:
        try:
            _storytelling_agent = StorytellingAgent()
        except Exception as exc:
            logger.warning("Falling back to MockStorytellingAgent: %s", exc)
            _storytelling_agent = MockStorytellingAgent()
    return _storytelling_agent
