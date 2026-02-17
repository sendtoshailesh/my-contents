"""
Platform Agent (T086-T095)

Generates platform-specific content versions from a ContentDraft.
Adapts tone, format, and length for each platform while maintaining core message.

Platforms Supported:
- LinkedIn: Professional, strategic (500-3000 chars)
- Twitter/X: Conversational, concise (280-28000 chars, thread format)  
- Reddit: Authentic, community-focused (300-40000 chars)
- Medium: Narrative, blog-style (1000-10000 chars)
- Substack: Conversational, intimate (800-8000 chars)
- Instagram: Visual-first, emoji-rich (100-2200 chars)

Usage:
    >>> agent = get_platform_agent()
    >>> versions = agent.generate_all_platforms(session_id="abc123")
    >>> linkedin_version = versions["linkedin"]
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from backend.models.models import (
    get_db_session, Session, ContentDraft, PlatformVersion, Platform
)
from services.llm_service import get_llm_service
from backend.utils.logger import backend_logger

logger = logging.getLogger("backend.agents.platform_agent")


class PlatformAgent:
    """
    Generates platform-specific content adaptations.
    
    Uses Llama 3.1 for cost-effective content reformatting.
    """
    
    def __init__(self):
        """Initialize platform agent with LLM service."""
        self.llm_service = get_llm_service()
        logger.info("✓ PlatformAgent initialized")
    
    def _load_platform_templates(self) -> Dict[str, Dict]:
        """
        Load all platform templates from database.
        
        Returns:
            Dict mapping platform_id → platform metadata
        """
        db = get_db_session()
        try:
            platforms = db.query(Platform).all()
            
            templates = {}
            for platform in platforms:
                templates[platform.id] = {
                    "name": platform.name,
                    "description": platform.description,
                    "tone": platform.tone,
                    "format": platform.format,
                    "min_length": platform.min_length,
                    "max_length": platform.max_length,
                    "visual_requirements": platform.visual_requirements
                }
            
            logger.info(f"✓ Loaded {len(templates)} platform templates")
            return templates
            
        finally:
            db.close()
    
    def _get_content_draft(self, session_id: str) -> Optional[ContentDraft]:
        """Retrieve the latest content draft for a session."""
        db = get_db_session()
        try:
            draft = db.query(ContentDraft).filter(
                ContentDraft.session_id == session_id
            ).order_by(ContentDraft.created_at.desc()).first()
            
            if not draft:
                logger.warning(f"No content draft found for session {session_id}")
                return None
            
            return draft
            
        finally:
            db.close()
    
    def generate_linkedin(
        self, 
        content_draft: Dict, 
        outline: Dict,
        template: Dict
    ) -> str:
        """
        Generate LinkedIn professional post/article.
        
        Features:
        - Professional, strategic tone
        - Bullet points for key insights
        - Hashtags for discoverability
        - 500-3000 characters
        """
        prompt = f"""You are a LinkedIn content strategist. Transform the following content draft into a professional LinkedIn post.

CONTENT DRAFT:
{content_draft.get('body_text', '')}

OUTLINE:
{json.dumps(outline, indent=2)}

REQUIREMENTS:
- Tone: {template['tone']}
- Format: {template['format']}
- Length: {template['min_length']}-{template['max_length']} characters
- Include: {template['visual_requirements']}

GUIDELINES:
1. Start with a compelling hook (question or insight)
2. Use bullet points for key takeaways
3. Professional but conversational tone
4. Include 3-5 relevant hashtags at the end
5. Call-to-action (invite discussion, share thoughts)

Generate LinkedIn post:"""

        response = self.llm_service.call_llm(
            model_name="llama-3.1",
            prompt=prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.strip()
    
    def generate_twitter(
        self, 
        content_draft: Dict, 
        outline: Dict,
        template: Dict
    ) -> str:
        """
        Generate Twitter/X thread.
        
        Features:
        - Conversational, concise tone
        - Thread format (numbered tweets)
        - Max 280 chars per tweet
        - 10 tweets max
        """
        prompt = f"""You are a Twitter content creator. Transform the following content into a Twitter/X thread.

CONTENT DRAFT:
{content_draft.get('body_text', '')}

OUTLINE:
{json.dumps(outline, indent=2)}

REQUIREMENTS:
- Tone: {template['tone']}
- Format: Thread with numbered tweets
- Max 280 characters per tweet
- Max 10 tweets total
- Make it engaging and shareable

GUIDELINES:
1. Tweet 1/10: Hook - grab attention with a question or bold statement
2. Tweets 2-8: Core insights (one idea per tweet)
3. Tweet 9: Summary or key takeaway
4. Tweet 10: Call-to-action or closing thought
5. Use line breaks for readability
6. Include emojis strategically (not excessive)

Generate Twitter thread (format as "1/10: [tweet text]"):"""

        response = self.llm_service.call_llm(
            model_name="llama-3.1",
            prompt=prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.strip()
    
    def generate_reddit(
        self, 
        content_draft: Dict, 
        outline: Dict,
        template: Dict
    ) -> str:
        """
        Generate Reddit post.
        
        Features:
        - Authentic, engaging tone
        - Markdown formatting
        - Community-friendly language
        - 300-40000 characters
        """
        prompt = f"""You are a Reddit community member. Transform the following content into a Reddit post.

CONTENT DRAFT:
{content_draft.get('body_text', '')}

OUTLINE:
{json.dumps(outline, indent=2)}

REQUIREMENTS:
- Tone: {template['tone']}
- Format: Markdown, community norms
- Length: {template['min_length']}-{template['max_length']} characters
- Be authentic and value-adding

GUIDELINES:
1. Use markdown formatting (headers, bullet points, code blocks)
2. Conversational and authentic voice (avoid marketing speak)
3. Provide value - insights, experiences, or useful information
4. Invite discussion with open-ended questions
5. Respect community norms (no self-promotion)

Generate Reddit post:"""

        response = self.llm_service.call_llm(
            model_name="llama-3.1",
            prompt=prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.strip()
    
    def generate_medium(
        self, 
        content_draft: Dict, 
        outline: Dict,
        template: Dict
    ) -> str:
        """
        Generate Medium article.
        
        Features:
        - Narrative, blog-style tone
        - Section headers
        - 1000-10000 characters
        """
        prompt = f"""You are a Medium writer. Transform the following content into a Medium article.

CONTENT DRAFT:
{content_draft.get('body_text', '')}

OUTLINE:
{json.dumps(outline, indent=2)}

REQUIREMENTS:
- Tone: {template['tone']}
- Format: {template['format']}
- Length: {template['min_length']}-{template['max_length']} characters
- Include: {template['visual_requirements']}

GUIDELINES:
1. Engaging title and subtitle
2. Strong opening paragraph (hook reader)
3. Section headers for each main point
4. Narrative flow with storytelling elements
5. Embedded insights and examples
6. Conclusion with takeaway message

Generate Medium article:"""

        response = self.llm_service.call_llm(
            model_name="llama-3.1",
            prompt=prompt,
            temperature=0.7,
            max_tokens=3000
        )
        
        return response.strip()
    
    def generate_substack(
        self, 
        content_draft: Dict, 
        outline: Dict,
        template: Dict
    ) -> str:
        """
        Generate Substack newsletter.
        
        Features:
        - Conversational, intimate tone
        - Author voice, sections
        - 800-8000 characters
        """
        prompt = f"""You are a Substack newsletter writer. Transform the following content into a newsletter.

CONTENT DRAFT:
{content_draft.get('body_text', '')}

OUTLINE:
{json.dumps(outline, indent=2)}

REQUIREMENTS:
- Tone: {template['tone']}
- Format: Newsletter with sections
- Length: {template['min_length']}-{template['max_length']} characters
- Voice: Personal, author-driven

GUIDELINES:
1. Personal greeting (e.g., "Hey friends,")
2. Conversational and intimate tone (like writing to a friend)
3. Clear sections with headers
4. Share personal insights or experiences
5. Direct reader engagement (questions, reflections)
6. Warm sign-off

Generate Substack newsletter:"""

        response = self.llm_service.call_llm(
            model_name="llama-3.1",
            prompt=prompt,
            temperature=0.7,
            max_tokens=2500
        )
        
        return response.strip()
    
    def generate_instagram(
        self, 
        content_draft: Dict, 
        outline: Dict,
        template: Dict
    ) -> str:
        """
        Generate Instagram caption.
        
        Features:
        - Visual-first, casual tone
        - Emojis for engagement
        - 100-2200 characters
        """
        prompt = f"""You are an Instagram content creator. Transform the following content into an Instagram caption.

CONTENT DRAFT:
{content_draft.get('body_text', '')}

OUTLINE:
{json.dumps(outline, indent=2)}

REQUIREMENTS:
- Tone: {template['tone']}
- Format: Visual-first caption
- Length: {template['min_length']}-{template['max_length']} characters
- Include: Emojis, line breaks for readability

GUIDELINES:
1. Start with an emoji and hook
2. Short, punchy sentences with line breaks
3. Strategic emoji use (enhance, don't overwhelm)
4. Hashtags at the end (5-10 relevant ones)
5. Call-to-action (tag a friend, share your thoughts, etc.)
6. Acknowledge this is a caption for a visual post

Generate Instagram caption:"""

        response = self.llm_service.call_llm(
            model_name="llama-3.1",
            prompt=prompt,
            temperature=0.8,  # More creative for Instagram
            max_tokens=800
        )
        
        return response.strip()
    
    def generate_all_platforms(
        self, 
        session_id: str,
        regenerate: bool = False
    ) -> Dict[str, str]:
        """
        Generate content versions for all 6 platforms.
        
        Args:
            session_id: Session identifier
            regenerate: If True, overwrite existing versions (for iteration)
        
        Returns:
            Dict mapping platform_id → generated content
        
        Raises:
            ValueError: If no content draft exists for session
        """
        logger.info(f"▶ Generating platform versions for session {session_id}")
        
        # Load content draft
        content_draft = self._get_content_draft(session_id)
        if not content_draft:
            raise ValueError(f"No content draft found for session {session_id}")
        
        # Parse content draft data
        draft_data = {
            "body_text": content_draft.body_text,
            "visual_plan": json.loads(content_draft.visual_plan) if content_draft.visual_plan else [],
            "framework_choice": content_draft.framework_choice
        }
        
        # Load session outline
        db = get_db_session()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session or not session.outlines:
                raise ValueError(f"No outline found for session {session_id}")
            
            # Get latest approved outline
            outline = None
            for out in sorted(session.outlines, key=lambda x: x.version, reverse=True):
                if out.user_approved:
                    outline = json.loads(out.outline_data)
                    break
            
            if not outline:
                raise ValueError(f"No approved outline found for session {session_id}")
            
        finally:
            db.close()
        
        # Load platform templates
        templates = self._load_platform_templates()
        
        # Generate content for each platform
        versions = {}
        
        # LinkedIn
        logger.info("  → Generating LinkedIn version...")
        versions["linkedin"] = self.generate_linkedin(draft_data, outline, templates["linkedin"])
        
        # Twitter
        logger.info("  → Generating Twitter thread...")
        versions["twitter"] = self.generate_twitter(draft_data, outline, templates["twitter"])
        
        # Reddit
        logger.info("  → Generating Reddit post...")
        versions["reddit"] = self.generate_reddit(draft_data, outline, templates["reddit"])
        
        # Medium
        logger.info("  → Generating Medium article...")
        versions["medium"] = self.generate_medium(draft_data, outline, templates["medium"])
        
        # Substack
        logger.info("  → Generating Substack newsletter...")
        versions["substack"] = self.generate_substack(draft_data, outline, templates["substack"])
        
        # Instagram
        logger.info("  → Generating Instagram caption...")
        versions["instagram"] = self.generate_instagram(draft_data, outline, templates["instagram"])
        
        # Save to database
        self._save_platform_versions(session_id, versions, regenerate)
        
        logger.info(f"✓ Generated {len(versions)} platform versions")
        return versions
    
    def _save_platform_versions(
        self, 
        session_id: str, 
        versions: Dict[str, str],
        regenerate: bool = False
    ):
        """
        Save platform versions to database.
        
        Args:
            session_id: Session identifier
            versions: Dict mapping platform_id → content
            regenerate: If True, increment version number
        """
        db = get_db_session()
        try:
            for platform_id, content in versions.items():
                # Check if version exists
                existing = db.query(PlatformVersion).filter(
                    PlatformVersion.session_id == session_id,
                    PlatformVersion.platform_name == platform_id
                ).order_by(PlatformVersion.version.desc()).first()
                
                version_number = 1
                if existing and regenerate:
                    version_number = existing.version + 1
                elif existing:
                    # Update existing version
                    existing.content = content
                    existing.updated_at = datetime.utcnow()
                    db.commit()
                    continue
                
                # Create new version
                platform_version = PlatformVersion(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    platform_name=platform_id,
                    version=version_number,
                    content=content
                )
                db.add(platform_version)
            
            db.commit()
            logger.info(f"✓ Saved platform versions to database")
            
        except Exception as e:
            db.rollback()
            logger.error(f"✗ Failed to save platform versions: {e}")
            raise
        finally:
            db.close()
    
    def regenerate_platform(
        self, 
        session_id: str, 
        platform_id: str,
        feedback: Optional[str] = None
    ) -> str:
        """
        Regenerate content for a specific platform based on feedback.
        
        Args:
            session_id: Session identifier
            platform_id: Platform to regenerate (e.g., "linkedin")
            feedback: Optional user feedback to incorporate
        
        Returns:
            Regenerated content string
        """
        logger.info(f"▶ Regenerating {platform_id} for session {session_id}")
        
        # Load templates
        templates = self._load_platform_templates()
        if platform_id not in templates:
            raise ValueError(f"Unknown platform: {platform_id}")
        
        # Load content draft
        content_draft = self._get_content_draft(session_id)
        if not content_draft:
            raise ValueError(f"No content draft found for session {session_id}")
        
        draft_data = {
            "body_text": content_draft.body_text,
            "visual_plan": json.loads(content_draft.visual_plan) if content_draft.visual_plan else [],
            "framework_choice": content_draft.framework_choice
        }
        
        # Load outline
        db = get_db_session()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            outline = None
            for out in sorted(session.outlines, key=lambda x: x.version, reverse=True):
                if out.user_approved:
                    outline = json.loads(out.outline_data)
                    break
        finally:
            db.close()
        
        # Generate based on platform
        generator_map = {
            "linkedin": self.generate_linkedin,
            "twitter": self.generate_twitter,
            "reddit": self.generate_reddit,
            "medium": self.generate_medium,
            "substack": self.generate_substack,
            "instagram": self.generate_instagram
        }
        
        regenerated = generator_map[platform_id](draft_data, outline, templates[platform_id])
        
        # Save as new version
        self._save_platform_versions(session_id, {platform_id: regenerated}, regenerate=True)
        
        logger.info(f"✓ Regenerated {platform_id} version")
        return regenerated


# Singleton instance
_platform_agent = None


def get_platform_agent() -> PlatformAgent:
    """Get or create platform agent singleton."""
    global _platform_agent
    if _platform_agent is None:
        _platform_agent = PlatformAgent()
    return _platform_agent
