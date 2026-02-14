"""
Tests for Framework Engine
Tests framework recommendation and outline-to-framework mapping
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.framework_engine import FrameworkEngine


class TestFrameworkEngine:
    """Test suite for FrameworkEngine"""
    
    @pytest.fixture
    def engine(self):
        """Create framework engine instance"""
        return FrameworkEngine()
    
    def test_get_frameworks(self, engine):
        """Test retrieving all frameworks"""
        frameworks = engine.get_frameworks()
        
        assert len(frameworks) == 6
        framework_ids = [f['id'] for f in frameworks]
        
        assert 'ted-talk' in framework_ids
        assert 'heros-journey' in framework_ids
        assert 'problem-solution' in framework_ids
        assert 'listicle' in framework_ids
        assert 'comparison' in framework_ids
        assert 'tutorial' in framework_ids
    
    def test_get_framework_by_id(self, engine):
        """Test retrieving specific framework"""
        framework = engine.get_framework('ted-talk')
        
        assert framework is not None
        assert framework['id'] == 'ted-talk'
        assert framework['name'] == 'TED Talk'
        assert len(framework['steps']) == 5
        assert 'Hook' in framework['steps']
        assert 'Call to action' in framework['steps']
    
    def test_get_framework_invalid_id(self, engine):
        """Test retrieving non-existent framework"""
        framework = engine.get_framework('non-existent')
        assert framework is None
    
    def test_recommend_listicle(self, engine):
        """Test recommending listicle framework"""
        outline = {
            'content_angle': '5 ways to improve your productivity',
            'sections': ['Intro', 'Tip 1', 'Tip 2', 'Tip 3', 'Tip 4', 'Tip 5'],
            'target_audience': 'Professionals'
        }
        
        recommendation = engine.recommend_framework(outline)
        assert recommendation == 'listicle'
    
    def test_recommend_problem_solution(self, engine):
        """Test recommending problem-solution framework"""
        outline = {
            'content_angle': 'Solving the scalability problem in microservices',
            'sections': ['The problem', 'Why it matters', 'Our solution'],
            'target_audience': 'Developers'
        }
        
        recommendation = engine.recommend_framework(outline)
        assert recommendation == 'problem-solution'
    
    def test_recommend_tutorial(self, engine):
        """Test recommending tutorial framework"""
        outline = {
            'content_angle': 'How to build a REST API with FastAPI',
            'sections': ['Introduction', 'Step 1: Setup', 'Step 2: Create routes', 'Step 3: Test'],
            'target_audience': 'Developers'
        }
        
        recommendation = engine.recommend_framework(outline)
        assert recommendation == 'tutorial'
    
    def test_recommend_comparison(self, engine):
        """Test recommending comparison framework"""
        outline = {
            'content_angle': 'AWS vs Azure vs GCP: Which cloud provider is best?',
            'sections': ['Introduction', 'Pricing', 'Features', 'Recommendation'],
            'target_audience': 'CTOs'
        }
        
        recommendation = engine.recommend_framework(outline)
        assert recommendation == 'comparison'
    
    def test_recommend_heros_journey(self, engine):
        """Test recommending hero's journey framework"""
        outline = {
            'content_angle': 'My journey from burnout to startup success',
            'sections': ['The challenge', 'Overcoming obstacles', 'Lessons learned'],
            'target_audience': 'Entrepreneurs'
        }
        
        recommendation = engine.recommend_framework(outline)
        assert recommendation == 'heros-journey'
    
    def test_recommend_default_ted_talk(self, engine):
        """Test default recommendation is TED Talk"""
        outline = {
            'content_angle': 'The future of artificial intelligence',
            'sections': ['Introduction', 'Current state', 'Future outlook'],
            'target_audience': 'General'
        }
        
        recommendation = engine.recommend_framework(outline)
        assert recommendation == 'ted-talk'
    
    def test_map_outline_to_ted_talk(self, engine):
        """Test mapping outline to TED Talk framework"""
        sections = [
            'Introduction: Why AI matters',
            'Background on machine learning',
            'Key insight: AGI is closer than we think',
            'Example: GPT-4 capabilities',
            'Conclusion: What we should do now'
        ]
        
        mapping = engine.map_outline_to_framework(sections, 'ted-talk')
        
        assert len(mapping) == 5
        assert mapping[0]['framework_step'] == 'Hook'
        assert mapping[0]['outline_section'] == sections[0]
        assert mapping[0]['order'] == 1
        
        # Check that all steps are mapped
        mapped_steps = [m['framework_step'] for m in mapping]
        assert 'Hook' in mapped_steps
        assert 'Build context' in mapped_steps
        assert 'Key insight' in mapped_steps
        assert 'Story examples' in mapped_steps
        assert 'Call to action' in mapped_steps
    
    def test_map_outline_to_listicle(self, engine):
        """Test mapping outline to listicle framework"""
        sections = [
            'Introduction to productivity tips',
            'Tip 1: Time blocking',
            'Tip 2: Pomodoro technique',
            'Tip 3: Digital detox',
            'Conclusion'
        ]
        
        mapping = engine.map_outline_to_framework(sections, 'listicle')
        
        assert len(mapping) == 5
        assert mapping[0]['framework_step'] == 'Intro'
        assert mapping[-1]['framework_step'] == 'Conclusion'
        
        # Items should be in the middle
        item_steps = [m['framework_step'] for m in mapping[1:-1]]
        assert 'Item 1' in item_steps
        assert 'Item 2' in item_steps
        assert 'Item 3+' in item_steps
    
    def test_map_outline_to_tutorial(self, engine):
        """Test mapping outline to tutorial framework"""
        sections = [
            'Introduction and prerequisites',
            'Step 1: Install dependencies',
            'Step 2: Configure environment',
            'Step 3: Write your first endpoint',
            'Expected results',
            'Common errors and fixes'
        ]
        
        mapping = engine.map_outline_to_framework(sections, 'tutorial')
        
        assert len(mapping) > 0
        
        # Check that steps are mapped
        mapped_steps = [m['framework_step'] for m in mapping]
        assert 'Intro & tools needed' in mapped_steps
        assert 'Step 1' in mapped_steps
        assert 'Step 2' in mapped_steps
    
    def test_validate_mapping_complete(self, engine):
        """Test validating a complete mapping"""
        sections = [
            'Introduction',
            'Background',
            'Main point',
            'Examples',
            'Conclusion'
        ]
        
        mapping = engine.map_outline_to_framework(sections, 'ted-talk')
        validation = engine.validate_mapping(mapping, 'ted-talk')
        
        assert validation['is_complete'] == True
        assert len(validation['missing_steps']) == 0
    
    def test_validate_mapping_incomplete(self, engine):
        """Test validating an incomplete mapping"""
        # Create incomplete mapping (missing some steps)
        incomplete_mapping = [
            {
                'framework_step': 'Hook',
                'outline_section': 'Introduction',
                'order': 1
            },
            {
                'framework_step': 'Key insight',
                'outline_section': 'Main point',
                'order': 2
            }
        ]
        
        validation = engine.validate_mapping(incomplete_mapping, 'ted-talk')
        
        assert validation['is_complete'] == False
        assert len(validation['missing_steps']) > 0
        assert 'Build context' in validation['missing_steps']
        assert 'Story examples' in validation['missing_steps']
        assert 'Call to action' in validation['missing_steps']
    
    def test_map_invalid_framework(self, engine):
        """Test mapping with invalid framework ID"""
        sections = ['Section 1', 'Section 2']
        
        with pytest.raises(ValueError, match="Framework 'invalid' not found"):
            engine.map_outline_to_framework(sections, 'invalid')
    
    def test_validate_invalid_framework(self, engine):
        """Test validating with invalid framework ID"""
        mapping = [{'framework_step': 'Test', 'outline_section': 'Test', 'order': 1}]
        
        with pytest.raises(ValueError, match="Framework 'invalid' not found"):
            engine.validate_mapping(mapping, 'invalid')
    
    def test_framework_cache(self, engine):
        """Test that frameworks are cached after first load"""
        # First call loads from database
        frameworks1 = engine.get_frameworks()
        
        # Second call should use cache
        frameworks2 = engine.get_frameworks()
        
        assert frameworks1 == frameworks2
        assert len(frameworks1) == 6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
