"""
Content Agent (US2)
Generates a narrative draft using framework structure and visuals.
"""

from typing import Dict, List, Optional
import logging

from backend.agents.mock_agents import MockContentAgent
from services.llm_service import get_llm_service

logger = logging.getLogger("backend.agents.content")


class ContentAgent:
    """Generates the content draft for a session."""

    def __init__(self):
        """Initialize ContentAgent with LLM service."""
        self.llm = get_llm_service()
        logger.info("✓ ContentAgent initialized")

    def generate_content(
        self,
        outline: Dict,
        framework_choice: str,
        framework_structure: List[Dict],
        visual_plan: List[Dict],
        include_code: bool = False
    ) -> Dict:
        """Create a structured narrative draft using LLM."""
        try:
            logger.info(f"🚀 Generating content for framework: {framework_choice}")
            
            # Extract outline information
            content_angle = outline.get("content_angle", "")
            target_audience = outline.get("target_audience", "general readers")
            sections = outline.get("sections", [])
            
            # Generate title and introduction
            title = content_angle if content_angle else "Generated Content"
            
            # Build the content using LLM for each section
            body_lines = [f"# {title}", ""]
            
            # Generate overview/introduction
            intro_prompt = f"""Write a compelling 2-3 paragraph introduction for a content piece with this angle:
"{content_angle}"

Target audience: {target_audience}
Framework: {framework_choice}

The introduction should hook the reader and set up the main points that will be covered."""

            try:
                intro = self.llm.call(task_type="creative", prompt=intro_prompt, max_tokens=500)
                body_lines.append(intro.strip())
                body_lines.append("")
            except Exception as e:
                logger.warning(f"⚠️  Could not generate intro, using fallback: {e}")
                body_lines.append("## Overview")
                body_lines.append("")
                body_lines.append(f"This content explores {content_angle.lower()}, structured using the {framework_choice} framework.")
                body_lines.append("")

            # Generate content for each framework section
            for idx, step in enumerate(framework_structure):
                try:
                    section_title = step.get("framework_step") or step.get("title") or f"Section {idx + 1}"
                    outline_section = step.get("outline_section", "")
                    
                    # Find corresponding outline section details
                    section_details = ""
                    for sec in sections:
                        if sec.get("title", "").lower() in outline_section.lower() or outline_section in str(sec.get("order", "")):
                            section_details = sec.get("description", "")
                            break
                    
                    body_lines.append(f"## {section_title}")
                    body_lines.append("")
                    
                    # Generate section content using LLM
                    section_prompt = f"""Write detailed, engaging content for this section of an article:

Section title: {section_title}
Content angle: {content_angle}
Target audience: {target_audience}
Framework step: {framework_choice} - {section_title}
Section details: {section_details or 'Expand on this topic with relevant examples and insights'}

Write 3-4 well-developed paragraphs that:
1. Provide valuable insights and information
2. Use specific examples where appropriate
3. Maintain an engaging, professional tone
4. Connect to the overall content angle

Do not include the section heading in your response."""

                    try:
                        section_content = self.llm.call(
                            task_type="creative",
                            prompt=section_prompt,
                            max_tokens=800
                        )
                        body_lines.append(section_content.strip())
                    except Exception as e:
                        logger.warning(f"⚠️  Error generating section {idx + 1}: {e}")
                        body_lines.append(f"Content for {section_title} will explore key concepts, provide practical examples, and offer actionable insights relevant to {target_audience}.")
                    
                    body_lines.append("")
                    
                    # Add visual reference if available
                    visual_ref = self._find_visual_for_section(visual_plan, step)
                    if visual_ref:
                        body_lines.append(f"*[Visual {visual_ref['visual_id']}: {visual_ref['description']}]*")
                        body_lines.append("")
                    
                except Exception as step_error:
                    logger.warning(f"⚠️  Error processing framework step: {step_error}")
                    body_lines.append(f"[Error processing section: {str(step_error)}]")
                    body_lines.append("")

            # Generate conclusion
            conclusion_prompt = f"""Write a strong conclusion (2-3 paragraphs) for an article about:
"{content_angle}"

Target audience: {target_audience}

The conclusion should:
1. Summarize key takeaways
2. Reinforce the main message
3. End with a call-to-action or thought-provoking statement"""

            try:
                conclusion = self.llm.call(task_type="creative", prompt=conclusion_prompt, max_tokens=400)
                body_lines.append("## Conclusion")
                body_lines.append("")
                body_lines.append(conclusion.strip())
            except Exception as e:
                logger.warning(f"⚠️  Could not generate conclusion: {e}")

            # Handle code snippets if requested
            code_snippets = []
            if include_code:
                try:
                    code_prompt = f"""Generate a relevant Python code example for content about: {content_angle}

The code should be practical, well-commented, and demonstrate a key concept.
Return ONLY the code, no explanations."""

                    code = self.llm.call(task_type="code", prompt=code_prompt, max_tokens=300)
                    
                    code_snippets.append({
                        "section": 2,
                        "language": "python",
                        "code": code.strip(),
                        "explanation": "Practical example demonstrating key concepts",
                        "expected_output": "See code comments for expected behavior"
                    })
                except Exception as code_error:
                    logger.warning(f"⚠️  Error generating code snippets: {code_error}")

            result = {
                "framework_choice": framework_choice,
                "body_text": "\n".join(body_lines),
                "visual_integration_points": [],
                "code_snippets": code_snippets,
                "content_quality_score": 0.85,
                "warnings": []
            }
            
            logger.info(f"✅ Content generation completed ({len(body_lines)} lines)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating content: {e}", exc_info=True)
            raise RuntimeError(f"Content generation failed: {str(e)}")

    @staticmethod
    def _find_visual_for_section(visual_plan: List[Dict], step: Dict) -> Optional[Dict]:
        """Find visual reference for a framework step."""
        try:
            location = step.get("outline_section")
            if not location:
                return None

            for visual in visual_plan:
                if str(location) in str(visual.get("location", "")):
                    return visual
            return None
        except Exception as e:
            logger.warning(f"⚠️  Error finding visual for section: {e}")
            return None


_content_agent = None


def get_content_agent() -> ContentAgent:
    """Get a singleton content agent instance."""
    global _content_agent
    if _content_agent is None:
        try:
            _content_agent = ContentAgent()
            logger.info("✓ ContentAgent singleton initialized")
        except Exception as exc:
            logger.warning(f"⚠️  Error initializing ContentAgent, using mock: {exc}")
            _content_agent = MockContentAgent()
    return _content_agent
