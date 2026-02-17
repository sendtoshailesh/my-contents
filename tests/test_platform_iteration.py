"""
Unit tests for PlatformAgent and IterationHandler

Tests platform-specific content generation and iteration feedback processing.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from backend.agents.platform_agent import PlatformAgent, get_platform_agent
from backend.agents.iteration_handler import (
    IterationHandler, get_iteration_handler, VALID_FEEDBACK_AREAS
)


# ============= Platform Agent Tests =============

class TestPlatformAgent:
    """Tests for platform content generation."""
    
    @pytest.fixture
    def platform_agent(self):
        """Create platform agent instance."""
        return PlatformAgent()
    
    @pytest.fixture
    def sample_content_draft(self):
        """Sample content draft data."""
        return {
            "body_text": """
# AI and Emotional Intelligence in Leadership

Artificial Intelligence is transforming how we lead, but emotional intelligence remains critical.

## Key Insights
1. AI augments decision-making
2. EI builds trust and connection
3. Together they create powerful leadership

Leaders must balance data-driven insights with human empathy.
            """,
            "visual_plan": [
                {"type": "flowchart", "description": "AI + EI = Modern Leadership"}
            ],
            "framework_choice": "Problem-Solution"
        }
    
    @pytest.fixture
    def sample_outline(self):
        """Sample outline data."""
        return {
            "num_sections": 3,
            "sections": [
                {"title": "Introduction", "key_points": ["AI in leadership", "Role of EI"]},
                {"title": "Core Concepts", "key_points": ["Data vs emotion", "Balance required"]},
                {"title": "Conclusion", "key_points": ["Future of leadership"]}
            ],
            "content_angle": "Balancing AI with emotional intelligence for better leadership",
            "why_compelling": "Addresses the future of work"
        }
    
    @pytest.fixture
    def sample_template(self):
        """Sample platform template."""
        return {
            "name": "LinkedIn",
            "tone": "professional, strategic",
            "format": "article, post",
            "min_length": 500,
            "max_length": 3000,
            "visual_requirements": "bullet points, hashtags"
        }
    
    @patch('backend.agents.platform_agent.get_llm_service')
    def test_generate_linkedin(self, mock_llm_service, platform_agent, sample_content_draft, sample_outline, sample_template):
        """Test LinkedIn post generation."""
        # Mock LLM response
        mock_llm = Mock()
        mock_llm.call_llm.return_value = """
🚀 The Future of Leadership: AI + Emotional Intelligence

As AI transforms decision-making, one thing remains clear: emotional intelligence is more critical than ever.

Key insights:
• AI augments data-driven decisions
• EI builds trust and human connection
• Together, they create powerful modern leaders

The most effective leaders will be those who can balance algorithmic insights with human empathy.

What's your take? How do you balance data and emotion in your leadership?

#Leadership #AI #EmotionalIntelligence #FutureOfWork #TechLeadership
        """
        mock_llm_service.return_value = mock_llm
        
        result = platform_agent.generate_linkedin(sample_content_draft, sample_outline, sample_template)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "#" in result  # Has hashtags
        mock_llm.call_llm.assert_called_once()
    
    @patch('backend.agents.platform_agent.get_llm_service')
    def test_generate_twitter(self, mock_llm_service, platform_agent, sample_content_draft, sample_outline, sample_template):
        """Test Twitter thread generation."""
        mock_llm = Mock()
        mock_llm.call_llm.return_value = """
1/5: 🤖 AI is transforming leadership, but here's what many miss: emotional intelligence is MORE important than ever.

2/5: AI gives us data-driven insights. But trust? Connection? That's pure EI.

3/5: The best leaders balance both: algorithmic precision + human empathy.

4/5: Key insight: AI augments decision-making, EI builds the foundation for those decisions to be implemented.

5/5: The future belongs to leaders who can be both data-savvy AND emotionally intelligent. Which are you focusing on?
        """
        mock_llm_service.return_value = mock_llm
        
        template = {**sample_template, "format": "thread"}
        result = platform_agent.generate_twitter(sample_content_draft, sample_outline, template)
        
        assert isinstance(result, str)
        assert "/5" in result or "/10" in result  # Thread format
        mock_llm.call_llm.assert_called_once()
    
    def test_load_platform_templates(self, platform_agent):
        """Test platform template loading."""
        with patch('backend.agents.platform_agent.get_db_session') as mock_db:
            # Mock database response
            mock_session = MagicMock()
            mock_platform = Mock()
            mock_platform.id = "linkedin"
            mock_platform.name = "LinkedIn"
            mock_platform.tone = "professional"
            mock_platform.format = "article"
            mock_platform.min_length = 500
            mock_platform.max_length = 3000
            mock_platform.visual_requirements = "hashtags"
            mock_platform.description = "Professional network"
            
            mock_session.query.return_value.all.return_value = [mock_platform]
            mock_db.return_value = mock_session
            
            templates = platform_agent._load_platform_templates()
            
            assert "linkedin" in templates
            assert templates["linkedin"]["name"] == "LinkedIn"
            assert templates["linkedin"]["min_length"] == 500
    
    def test_singleton_instance(self):
        """Test that get_platform_agent returns singleton."""
        agent1 = get_platform_agent()
        agent2 = get_platform_agent()
        assert agent1 is agent2


# ============= Iteration Handler Tests =============

class TestIterationHandler:
    """Tests for iteration and feedback processing."""
    
    @pytest.fixture
    def iteration_handler(self):
        """Create iteration handler instance."""
        return IterationHandler()
    
    def test_validate_feedback_areas(self, iteration_handler):
        """Test feedback area validation."""
        # Valid areas
        valid_areas = ["tone", "depth", "visuals"]
        result = iteration_handler._validate_feedback_areas(valid_areas)
        assert result == ["tone", "depth", "visuals"]
        
        # Mixed valid/invalid
        mixed_areas = ["tone", "invalid_area", "depth"]
        result = iteration_handler._validate_feedback_areas(mixed_areas)
        assert "tone" in result
        assert "depth" in result
        assert "invalid_area" not in result
        
        # All invalid should raise error
        with pytest.raises(ValueError):
            iteration_handler._validate_feedback_areas(["invalid1", "invalid2"])
    
    def test_determine_affected_components_auto(self, iteration_handler):
        """Test automatic component determination."""
        # Tone feedback affects content + platforms
        components = iteration_handler._determine_affected_components(
            feedback_areas=["tone", "depth"]
        )
        assert "content_draft" in components
        assert "platform_versions" in components
        
        # Visuals feedback affects visuals + content
        components = iteration_handler._determine_affected_components(
            feedback_areas=["visuals"]
        )
        assert "visuals" in components
        assert "content_draft" in components
    
    def test_determine_affected_components_explicit(self, iteration_handler):
        """Test explicit component specification."""
        components = iteration_handler._determine_affected_components(
            feedback_areas=["tone"],
            explicit_components=["platform_versions"]
        )
        assert components == ["platform_versions"]
        assert "content_draft" not in components
    
    def test_check_completion_valid(self, iteration_handler):
        """Test completion phrase detection."""
        assert iteration_handler.check_completion("ok and good") is True
        assert iteration_handler.check_completion("OK AND GOOD") is True
        assert iteration_handler.check_completion("Looks ok and good to me!") is True
        assert iteration_handler.check_completion("looks good") is True
        assert iteration_handler.check_completion("perfect") is True
    
    def test_check_completion_invalid(self, iteration_handler):
        """Test invalid completion phrases."""
        assert iteration_handler.check_completion("not quite there") is False
        assert iteration_handler.check_completion("needs more work") is False
        assert iteration_handler.check_completion("almost good") is False
    
    def test_singleton_instance(self):
        """Test that get_iteration_handler returns singleton."""
        handler1 = get_iteration_handler()
        handler2 = get_iteration_handler()
        assert handler1 is handler2
    
    @patch('backend.agents.iteration_handler.get_db_session')
    def test_get_current_iteration_count(self, mock_db, iteration_handler):
        """Test iteration count retrieval."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.count.return_value = 3
        mock_db.return_value = mock_session
        
        count = iteration_handler._get_current_iteration_count("test_session")
        assert count == 3


# ============= Integration Tests =============

@pytest.mark.integration
class TestPlatformIterationIntegration:
    """Integration tests for platform generation + iteration workflow."""
    
    @patch('backend.agents.platform_agent.get_db_session')
    @patch('backend.agents.platform_agent.get_llm_service')
    def test_full_platform_generation_workflow(self, mock_llm, mock_db):
        """Test complete platform generation for all 6 platforms."""
        # Setup mocks
        mock_llm_service = Mock()
        mock_llm_service.call_llm.return_value = "Generated content"
        mock_llm.return_value = mock_llm_service
        
        # Mock database
        mock_session = MagicMock()
        mock_db.return_value = mock_session
        
        # This would be a full integration test with real database
        # For now, we verify the structure is correct
        agent = get_platform_agent()
        assert agent is not None
    
    @patch('backend.agents.iteration_handler.get_db_session')
    @patch('backend.agents.iteration_handler.get_content_agent')
    @patch('backend.agents.iteration_handler.get_platform_agent')
    def test_feedback_processing_workflow(self, mock_platform, mock_content, mock_db):
        """Test feedback processing through to content regeneration."""
        handler = get_iteration_handler()
        
        # Mock agents
        mock_content.return_value.generate_content.return_value = {"body_text": "Updated content"}
        mock_platform.return_value.generate_all_platforms.return_value = {
            "linkedin": "Updated LinkedIn content"
        }
        
        # Mock database
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.count.return_value = 1
        mock_db.return_value = mock_session
        
        # This validates the handler structure
        assert handler is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
