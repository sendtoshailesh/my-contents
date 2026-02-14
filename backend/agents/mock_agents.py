"""
Mock Agents for Local Development & Testing

These mock agents simulate the behavior of real AI agents for testing without API keys.
Used when real LLM APIs are not available.
"""

import json
from datetime import datetime
from typing import Dict, List, Any


class MockInputAgent:
    """Mock Input Agent - simulates topic extraction"""
    
    @staticmethod
    def extract_topic_info(topic: str) -> Dict[str, Any]:
        """Extract simulated topic information"""
        return {
            "theme": topic.split()[0][:10],
            "target_audience": "general_public",
            "primary_intent": "educate",
            "focus_area": topic[:50],
            "is_out_of_scope": False,
            "warning": None,
            "keywords": topic.split()[:3]
        }


class MockReasoningAgent:
    """Mock Reasoning Agent - simulates outline generation"""
    
    @staticmethod
    def generate_outline(topic_data: Dict) -> Dict[str, Any]:
        """Generate simulated outline with all required fields"""
        return {
            "topic": topic_data.get("topic", ""),
            "content_angle": f"Technical exploration of {topic_data['focus_area']}",
            "target_audience": topic_data.get("audience", "general_public"),
            "primary_intent": topic_data.get("intent", "educate"),
            "sections": [
                {
                    "title": "Introduction",
                    "description": "Overview and context",
                    "order": 1,
                    "key_points": ["Background", "Relevance", "Scope"]
                },
                {
                    "title": "Main Concepts",
                    "description": "Core ideas and frameworks",
                    "order": 2,
                    "key_points": ["Definition", "Applications", "Characteristics"]
                },
                {
                    "title": "Current State",
                    "description": "Recent developments",
                    "order": 3,
                    "key_points": ["Trends", "Research", "Examples"]
                },
                {
                    "title": "Future Implications",
                    "description": "What's next",
                    "order": 4,
                    "key_points": ["Opportunities", "Challenges", "Timeline"]
                },
                {
                    "title": "Conclusion",
                    "description": "Summary and takeaways",
                    "order": 5,
                    "key_points": ["Key insights", "Recommendations", "Resources"]
                }
            ],
            "num_sections": 5,
            "estimated_read_time": 8,
            "difficulty_level": "intermediate",
            "why_this_matters": "This perspective helps readers understand the broader implications",
            "outline_rationale": "5-part structure provides comprehensive coverage with practical examples"
        }
    
    @staticmethod
    def validate_outline(outline: Dict) -> bool:
        """Validate outline structure"""
        required_fields = ['content_angle', 'target_audience', 'sections']
        return all(field in outline for field in required_fields)


class MockResearchAgent:
    """Mock Research Agent - simulates validation through web research"""
    
    @staticmethod
    def validate_outline(outline: Dict) -> Dict[str, Any]:
        """Validate outline and return simulated research results"""
        return {
            "passed_validation": True,
            "confidence_score": 0.85,  # 85% confidence
            "credible_sources_found": 12,
            "claims_checked": 8,
            "validation_details": {
                "sources": [
                    "https://example.com/article1",
                    "https://example.com/article2",
                    "https://example.com/article3"
                ],
                "verified_claims": 7,
                "unverified_claims": 1,
                "contradictions": 0,
                "missing_citations": []
            },
            "research_timestamp": datetime.utcnow().isoformat()
        }


class MockStorytellingAgent:
    """Mock Storytelling Agent - simulates framework mapping and visuals"""

    @staticmethod
    def generate_framework_plan(outline: Dict, framework_choice: str, visual_opt_in: bool = True) -> Dict[str, Any]:
        """Generate simulated framework mapping and visual plan"""
        sections = outline.get("sections", [])
        framework_structure = []
        for i, section in enumerate(sections, 1):
            framework_structure.append({
                "framework_step": i,
                "outline_section": i,
                "title": section.get("title", f"Section {i}")
            })

        visual_plan = []
        if visual_opt_in:
            visual_plan = [
                {
                    "visual_id": 1,
                    "type": "flowchart",
                    "location": "section_2",
                    "recommended_tool": "mermaid",
                    "description": "High-level flow of the main idea",
                    "draft_code": "flowchart LR\n  A[Problem] --> B[Insight]\n  B --> C[Impact]"
                },
                {
                    "visual_id": 2,
                    "type": "timeline",
                    "location": "section_3",
                    "recommended_tool": "mermaid",
                    "description": "Timeline of key developments",
                    "draft_code": "timeline\n  title Evolution\n  2022 : Early signals\n  2023 : Adoption\n  2024 : Maturity"
                }
            ]

        return {
            "framework_choice": framework_choice,
            "framework_explanation": "Mock recommendation based on outline shape.",
            "framework_structure": framework_structure,
            "visual_plan": visual_plan,
            "total_visuals": len(visual_plan),
            "opt_out_visuals": not visual_opt_in
        }


class MockContentAgent:
    """Mock Content Agent - simulates content draft generation"""

    @staticmethod
    def generate_content(
        outline: Dict,
        framework_choice: str,
        framework_structure: List[Dict],
        visual_plan: List[Dict],
        include_code: bool = False
    ) -> Dict[str, Any]:
        """Generate simulated content draft"""
        title = outline.get("content_angle", "Generated Content")
        body_lines = [f"# {title}", "", "## Overview", "", "This is a mock content draft."]

        for step in framework_structure:
            body_lines.append("")
            body_lines.append(f"## {step.get('title', 'Section')}")
            body_lines.append("Key ideas and examples go here.")

        if visual_plan:
            body_lines.append("")
            body_lines.append("## Visuals")
            for visual in visual_plan:
                body_lines.append(f"- See Visual {visual['visual_id']}: {visual['description']}")

        code_snippets = []
        if include_code:
            code_snippets.append({
                "section": 2,
                "language": "python",
                "code": "def summarize_topic(topic):\n    return f'Key takeaways on {topic}'",
                "explanation": "Minimal example for a topic summary helper.",
                "expected_output": "Key takeaways on <topic>"
            })

        return {
            "framework_choice": framework_choice,
            "body_text": "\n".join(body_lines),
            "visual_integration_points": [],
            "code_snippets": code_snippets,
            "content_quality_score": 0.82,
            "warnings": []
        }
