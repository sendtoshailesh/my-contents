"""
Iteration Handler (T096-T101)

Processes user feedback and coordinates content regeneration.
Manages the improvement loop until user says "ok and good".

Feedback Areas:
- tone: Adjust formality, emotion, voice
- depth: More/less detail, technical depth
- visuals: Add/remove/modify visual elements
- technicality: Increase/decrease technical complexity
- humor: Adjust humor level
- examples: Add/remove/change examples
- structure: Reorganize sections, flow

Affected Components:
- content_draft: Main content body
- platform_versions: Platform-specific adaptations
- visuals: Visual plan and diagrams

Usage:
    >>> handler = get_iteration_handler()
    >>> result = handler.process_feedback(
    ...     session_id="abc123",
    ...     feedback_areas=["tone", "depth"],
    ...     feedback_text="Make it more conversational and add more examples",
    ...     affected_components=["content_draft", "platform_versions"]
    ... )
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import re

from backend.models.models import (
    get_db_session, Session, IterationFeedback, ContentDraft, PlatformVersion
)
from backend.agents.content_agent import get_content_agent
from backend.agents.platform_agent import get_platform_agent
from backend.utils.logger import backend_logger

logger = logging.getLogger("backend.agents.iteration_handler")


# Valid feedback areas
VALID_FEEDBACK_AREAS = {
    "tone", "depth", "visuals", "technicality", 
    "humor", "examples", "structure"
}

# Component mapping
VALID_COMPONENTS = {
    "content_draft", "platform_versions", "visuals"
}

# "ok and good" phrase variations (case-insensitive)
COMPLETION_PATTERNS = [
    r"ok\s+and\s+good",
    r"okay\s+and\s+good",
    r"ok\s+&\s+good",
    r"looks\s+good",
    r"all\s+good",
    r"perfect"
]


class IterationHandler:
    """
    Processes user feedback and coordinates regeneration.
    """
    
    def __init__(self):
        """Initialize iteration handler with agents."""
        self.content_agent = get_content_agent()
        self.platform_agent = get_platform_agent()
        logger.info("✓ IterationHandler initialized")
    
    def _get_current_iteration_count(self, session_id: str) -> int:
        """Get the current iteration number for a session."""
        db = get_db_session()
        try:
            count = db.query(IterationFeedback).filter(
                IterationFeedback.session_id == session_id
            ).count()
            return count
        finally:
            db.close()
    
    def _validate_feedback_areas(self, feedback_areas: List[str]) -> List[str]:
        """
        Validate and normalize feedback areas.
        
        Args:
            feedback_areas: List of feedback area names
        
        Returns:
            Validated list of feedback areas
        
        Raises:
            ValueError: If any feedback area is invalid
        """
        validated = []
        for area in feedback_areas:
            area_normalized = area.lower().strip()
            if area_normalized not in VALID_FEEDBACK_AREAS:
                logger.warning(f"Invalid feedback area: {area}")
                continue
            validated.append(area_normalized)
        
        if not validated:
            raise ValueError(
                f"No valid feedback areas provided. Valid areas: {VALID_FEEDBACK_AREAS}"
            )
        
        return validated
    
    def _determine_affected_components(
        self, 
        feedback_areas: List[str],
        explicit_components: Optional[List[str]] = None
    ) -> List[str]:
        """
        Determine which components need regeneration based on feedback.
        
        Args:
            feedback_areas: List of feedback area names
            explicit_components: User-specified components (if any)
        
        Returns:
            List of component names to regenerate
        """
        if explicit_components:
            # User explicitly specified components
            return [c for c in explicit_components if c in VALID_COMPONENTS]
        
        # Auto-determine based on feedback areas
        components = set()
        
        # Mapping: feedback area → affected components
        area_component_map = {
            "tone": ["content_draft", "platform_versions"],
            "depth": ["content_draft", "platform_versions"],
            "visuals": ["visuals", "content_draft"],
            "technicality": ["content_draft", "platform_versions"],
            "humor": ["content_draft", "platform_versions"],
            "examples": ["content_draft", "platform_versions"],
            "structure": ["content_draft", "platform_versions"]
        }
        
        for area in feedback_areas:
            if area in area_component_map:
                components.update(area_component_map[area])
        
        return list(components)
    
    def _regenerate_content_draft(
        self, 
        session_id: str, 
        feedback_text: str,
        feedback_areas: List[str]
    ) -> Dict:
        """
        Regenerate content draft incorporating feedback.
        
        Args:
            session_id: Session identifier
            feedback_text: User feedback text
            feedback_areas: List of feedback areas
        
        Returns:
            Updated content draft data
        """
        logger.info(f"  → Regenerating content draft for session {session_id}")
        
        # Get current content draft
        db = get_db_session()
        try:
            draft = db.query(ContentDraft).filter(
                ContentDraft.session_id == session_id
            ).order_by(ContentDraft.created_at.desc()).first()
            
            if not draft:
                raise ValueError(f"No content draft found for session {session_id}")
            
            current_content = draft.body_text
            visual_plan = json.loads(draft.visual_plan) if draft.visual_plan else []
            framework = draft.framework_choice
            
        finally:
            db.close()
        
        # Build improvement prompt
        improvement_context = f"""
CURRENT CONTENT:
{current_content}

USER FEEDBACK:
{feedback_text}

FEEDBACK AREAS TO ADDRESS:
{json.dumps(feedback_areas)}

INSTRUCTIONS:
Revise the content to address the user's feedback. Focus specifically on:
"""
        
        for area in feedback_areas:
            area_instructions = {
                "tone": "- Adjust the tone (formality, emotion, voice) as requested",
                "depth": "- Modify the level of detail and depth",
                "visuals": "- Update visual references or add new ones",
                "technicality": "- Adjust technical complexity",
                "humor": "- Adjust humor level",
                "examples": "- Add, remove, or change examples",
                "structure": "- Reorganize sections or flow"
            }
            improvement_context += f"\n{area_instructions.get(area, '')}"
        
        # Call content agent to regenerate
        # Note: This is a simplified version. In practice, you'd pass feedback to content_agent
        regenerated = self.content_agent.generate_content(
            session_id=session_id,
            feedback_context=improvement_context
        )
        
        return regenerated
    
    def _regenerate_platform_versions(
        self, 
        session_id: str,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Regenerate platform-specific versions.
        
        Args:
            session_id: Session identifier
            platforms: Specific platforms to regenerate (None = all)
        
        Returns:
            Dict mapping platform_id → regenerated content
        """
        logger.info(f"  → Regenerating platform versions for session {session_id}")
        
        if platforms:
            # Regenerate specific platforms
            versions = {}
            for platform_id in platforms:
                versions[platform_id] = self.platform_agent.regenerate_platform(
                    session_id=session_id,
                    platform_id=platform_id
                )
            return versions
        else:
            # Regenerate all platforms
            return self.platform_agent.generate_all_platforms(
                session_id=session_id,
                regenerate=True
            )
    
    def process_feedback(
        self,
        session_id: str,
        feedback_areas: List[str],
        feedback_text: str,
        affected_components: Optional[List[str]] = None,
        specific_platforms: Optional[List[str]] = None
    ) -> Dict:
        """
        Process user feedback and regenerate affected content.
        
        Args:
            session_id: Session identifier
            feedback_areas: List of feedback area names
            feedback_text: Freeform feedback text
            affected_components: Explicit components to regenerate (optional)
            specific_platforms: Specific platforms to regenerate (optional)
        
        Returns:
            Dict with iteration results:
            {
                "iteration_number": int,
                "affected_components": List[str],
                "regenerated_content": bool,
                "updated_platform_versions": bool,
                "status": "iterating"
            }
        
        Raises:
            ValueError: If feedback areas are invalid or session not found
        """
        logger.info(f"▶ Processing feedback for session {session_id}")
        
        # Validate feedback areas
        validated_areas = self._validate_feedback_areas(feedback_areas)
        
        # Determine components to regenerate
        components = self._determine_affected_components(
            feedback_areas=validated_areas,
            explicit_components=affected_components
        )
        
        # Get iteration number
        iteration_number = self._get_current_iteration_count(session_id) + 1
        
        logger.info(f"  Iteration #{iteration_number}")
        logger.info(f"  Feedback areas: {validated_areas}")
        logger.info(f"  Affected components: {components}")
        
        # Regenerate components
        regenerated_data = {}
        regenerated_content = False
        updated_platforms = False
        
        if "content_draft" in components or "visuals" in components:
            # Regenerate content draft
            regenerated_data["content_draft"] = self._regenerate_content_draft(
                session_id=session_id,
                feedback_text=feedback_text,
                feedback_areas=validated_areas
            )
            regenerated_content = True
        
        if "platform_versions" in components:
            # Regenerate platform versions
            regenerated_data["platform_versions"] = self._regenerate_platform_versions(
                session_id=session_id,
                platforms=specific_platforms
            )
            updated_platforms = True
        
        # Save iteration feedback to database
        self._save_iteration_feedback(
            session_id=session_id,
            iteration_number=iteration_number,
            feedback_areas=validated_areas,
            feedback_text=feedback_text,
            regenerated_content=regenerated_data,
            affected_components=components
        )
        
        # Update session status
        self._update_session_status(session_id, "iterating")
        
        logger.info(f"✓ Completed iteration #{iteration_number}")
        
        return {
            "iteration_number": iteration_number,
            "affected_components": components,
            "regenerated_content": regenerated_content,
            "updated_platform_versions": updated_platforms,
            "status": "iterating"
        }
    
    def _save_iteration_feedback(
        self,
        session_id: str,
        iteration_number: int,
        feedback_areas: List[str],
        feedback_text: str,
        regenerated_content: Dict,
        affected_components: List[str]
    ):
        """Save iteration feedback to database."""
        db = get_db_session()
        try:
            feedback = IterationFeedback(
                id=str(uuid.uuid4()),
                session_id=session_id,
                iteration_number=iteration_number,
                feedback_areas=json.dumps(feedback_areas),
                feedback_text=feedback_text,
                regenerated_content=json.dumps(regenerated_content),
                affected_components=json.dumps(affected_components)
            )
            db.add(feedback)
            db.commit()
            
            logger.info(f"✓ Saved iteration feedback to database")
            
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Failed to save iteration feedback: {e}")
            raise
        finally:
            db.close()
    
    def _update_session_status(self, session_id: str, status: str):
        """Update session status."""
        db = get_db_session()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            if session:
                session.status = status
                session.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    def check_completion(self, text: str) -> bool:
        """
        Check if text contains "ok and good" completion phrase.
        
        Args:
            text: User input text
        
        Returns:
            True if completion phrase detected, False otherwise
        """
        text_normalized = text.lower().strip()
        
        for pattern in COMPLETION_PATTERNS:
            if re.search(pattern, text_normalized):
                logger.info(f"✓ Completion phrase detected: {pattern}")
                return True
        
        return False
    
    def complete_session(
        self, 
        session_id: str,
        completion_phrase: str
    ) -> Dict:
        """
        Mark session as complete with "ok and good" phrase.
        
        Args:
            session_id: Session identifier
            completion_phrase: User's completion phrase
        
        Returns:
            Dict with completion results:
            {
                "session_id": str,
                "status": "completed",
                "completed_at": str (ISO8601),
                "iteration_count": int,
                "summary": str
            }
        
        Raises:
            ValueError: If completion phrase not valid or session not found
        """
        logger.info(f"▶ Completing session {session_id}")
        
        # Validate completion phrase
        if not self.check_completion(completion_phrase):
            raise ValueError(
                f"Invalid completion phrase. Must contain 'ok and good' or similar."
            )
        
        # Get session
        db = get_db_session()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            # Get iteration count
            iteration_count = self._get_current_iteration_count(session_id)
            
            # Update session
            session.status = "completed"
            session.completed_phrase = completion_phrase
            session.completed_at = datetime.utcnow()
            session.updated_at = datetime.utcnow()
            db.commit()
            
            # Generate summary
            summary = self._generate_session_summary(session, iteration_count)
            
            logger.info(f"✓ Session {session_id} marked as completed")
            
            return {
                "session_id": session_id,
                "status": "completed",
                "completed_at": session.completed_at.isoformat(),
                "iteration_count": iteration_count,
                "summary": summary
            }
            
        finally:
            db.close()
    
    def _generate_session_summary(self, session: Session, iteration_count: int) -> str:
        """Generate a summary of the completed session."""
        return f"""Session completed successfully!
        
Topic: {session.topic}
Iterations: {iteration_count}
Status: {session.status}
Completed: {session.completed_at.strftime('%Y-%m-%d %H:%M:%S')}

Your content has been generated across 6 platforms and refined through {iteration_count} iteration(s).
"""


# Singleton instance
_iteration_handler = None


def get_iteration_handler() -> IterationHandler:
    """Get or create iteration handler singleton."""
    global _iteration_handler
    if _iteration_handler is None:
        _iteration_handler = IterationHandler()
    return _iteration_handler
