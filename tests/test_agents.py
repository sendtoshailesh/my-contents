"""
Unit Tests for Input Agent and Reasoning Agent

Tests T021-T028 implementation:
- T021-T024: Input Agent (topic extraction, focus area matching)
- T025-T028: Reasoning Agent (outline generation)
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict

from backend.agents.input_agent import InputAgent, get_input_agent
from backend.agents.reasoning_agent import ReasoningAgent, get_reasoning_agent


# ============================================================================
# INPUT AGENT TESTS (T021-T024)
# ============================================================================

class TestInputAgentTopicExtraction:
    """Test T021-T022: Topic extraction and intent classification."""

    @patch("backend.agents.input_agent.ModelRouter")
    @patch("backend.agents.input_agent.get_reference_data")
    def test_extract_topic_info_ai_topic(self, mock_ref_data, mock_model_router):
        """Test extraction of AI-related topic."""
        # Mock LLM response
        llm_response = json.dumps({
            "theme": "How artificial intelligence is transforming medical diagnosis and treatment",
            "audience": "Hospital administrators and medical professionals",
            "intent": "inform",
            "detected_focus_area": "AI"
        })
        
        mock_router = Mock()
        mock_router.call.return_value = llm_response
        mock_model_router.return_value = mock_router
        
        # Mock reference data
        mock_ref_inst = Mock()
        mock_ref_inst.get_focus_areas.return_value = [
            {"id": "AI", "name": "Artificial Intelligence", "description": "AI topics"},
            {"id": "CLOUD", "name": "Cloud Computing", "description": "Cloud topics"}
        ]
        mock_ref_data.return_value = mock_ref_inst
        
        # Test
        agent = InputAgent()
        result = agent.extract_topic_info("AI in healthcare")
        
        # Assertions
        assert result["topic"] == "AI in healthcare"
        assert "artificial intelligence" in result["theme"].lower()
        assert "hospital" in result["audience"].lower()
        assert result["intent"] == "inform"
        assert result["focus_area"] == "AI"
        assert result["is_out_of_scope"] == False
        assert result["confidence"] > 0.8

    @patch("backend.agents.input_agent.ModelRouter")
    @patch("backend.agents.input_agent.get_reference_data")
    def test_extract_topic_info_out_of_scope(self, mock_ref_data, mock_model_router):
        """Test extraction of out-of-scope topic."""
        # Mock LLM response with unknown focus area
        llm_response = json.dumps({
            "theme": "How to become a professional tennis player",
            "audience": "Aspiring athletes",
            "intent": "guide",
            "detected_focus_area": "Unknown"
        })
        
        mock_router = Mock()
        mock_router.call.return_value = llm_response
        mock_model_router.return_value = mock_router
        
        # Mock reference data
        mock_ref_inst = Mock()
        mock_ref_inst.get_focus_areas.return_value = [
            {"id": "AI", "name": "Artificial Intelligence", "description": "AI topics"}
        ]
        mock_ref_data.return_value = mock_ref_inst
        
        # Test
        agent = InputAgent()
        result = agent.extract_topic_info("Professional tennis")
        
        # Assertions
        assert result["focus_area"] == "OUT_OF_SCOPE"
        assert result["is_out_of_scope"] == True
        assert result["warning"] is not None
        assert "override" in result["warning"].lower()

    @patch("backend.agents.input_agent.ModelRouter")
    @patch("backend.agents.input_agent.get_reference_data")
    def test_extract_topic_info_multiple_intents(self, mock_ref_data, mock_model_router):
        """Test extraction with various intent types."""
        intents = ["educate", "inspire", "guide", "entertain", "challenge"]
        
        mock_router = Mock()
        mock_ref_inst = Mock()
        mock_ref_inst.get_focus_areas.return_value = [
            {"id": "AI", "name": "Artificial Intelligence", "description": "AI topics"}
        ]
        mock_ref_data.return_value = mock_ref_inst
        mock_model_router.return_value = mock_router
        
        agent = InputAgent()
        
        for intent in intents:
            llm_response = json.dumps({
                "theme": "Test theme",
                "audience": "Test audience",
                "intent": intent,
                "detected_focus_area": "AI"
            })
            mock_router.call.return_value = llm_response
            
            result = agent.extract_topic_info(f"Test topic with {intent}")
            
            assert result["intent"] == intent.lower()


class TestInputAgentFocusAreaMatching:
    """Test T023-T024: Focus area matching and keyword recognition."""

    @patch("backend.agents.input_agent.get_reference_data")
    def test_match_focus_area_exact_match(self, mock_ref_data):
        """Test exact focus area match."""
        mock_ref_inst = Mock()
        mock_ref_inst.get_focus_areas.return_value = [
            {"id": "AI", "name": "Artificial Intelligence", "description": "AI topics"}
        ]
        mock_ref_data.return_value = mock_ref_inst
        
        agent = InputAgent()
        focus_area, confidence = agent.match_focus_area("AI")
        
        assert focus_area == "AI"
        assert confidence == 1.0

    @patch("backend.agents.input_agent.get_reference_data")
    def test_match_focus_area_keyword_variations(self, mock_ref_data):
        """Test keyword matching with variations."""
        mock_ref_inst = Mock()
        mock_ref_inst.get_focus_areas.return_value = [
            {"id": "AI", "name": "Artificial Intelligence", "description": "AI topics"},
            {"id": "CLOUD", "name": "Cloud", "description": "Cloud topics"},
            {"id": "MIGRATION", "name": "Migration", "description": "Migration topics"}
        ]
        mock_ref_data.return_value = mock_ref_inst
        
        agent = InputAgent()
        
        # Test AI variations
        focus_area, confidence = agent.match_focus_area("Machine Learning")
        assert focus_area == "AI"
        assert confidence >= 0.7
        
        # Test Cloud variations
        focus_area, confidence = agent.match_focus_area("Kubernetes")
        assert focus_area == "CLOUD"
        assert confidence >= 0.7
        
        # Test Migration variations
        focus_area, confidence = agent.match_focus_area("Modernization")
        assert focus_area == "MIGRATION"
        assert confidence >= 0.7

    @patch("backend.agents.input_agent.get_reference_data")
    def test_match_focus_area_out_of_scope(self, mock_ref_data):
        """Test OUT_OF_SCOPE detection."""
        mock_ref_inst = Mock()
        mock_ref_inst.get_focus_areas.return_value = [
            {"id": "AI", "name": "Artificial Intelligence", "description": "AI topics"}
        ]
        mock_ref_data.return_value = mock_ref_inst
        
        agent = InputAgent()
        
        # Test various out-of-scope inputs
        test_cases = ["Unknown", "Random topic", "", "None"]
        
        for test_area in test_cases:
            focus_area, confidence = agent.match_focus_area(test_area)
            assert focus_area == "OUT_OF_SCOPE"
            assert confidence == 0.0


class TestInputAgentJsonParsing:
    """Test JSON parsing with various LLM response formats."""

    def test_parse_json_response_plain_json(self):
        """Test parsing plain JSON response."""
        response = """{"theme": "Test theme", "audience": "Developers", "intent": "inform", "detected_focus_area": "AI"}"""
        
        result = InputAgent._parse_json_response(response)
        
        assert result["theme"] == "Test theme"
        assert result["audience"] == "Developers"
        assert result["intent"] == "inform"
        assert result["detected_focus_area"] == "AI"

    def test_parse_json_response_with_markdown_code_block(self):
        """Test parsing JSON with markdown code block."""
        response = """```json
{
  "theme": "Test theme",
  "audience": "Developers",
  "intent": "inform",
  "detected_focus_area": "AI"
}
```"""
        
        result = InputAgent._parse_json_response(response)
        
        assert result["theme"] == "Test theme"
        assert result["audience"] == "Developers"

    def test_parse_json_response_malformed_fallback(self):
        """Test fallback for malformed JSON."""
        response = "This is not JSON"
        
        result = InputAgent._parse_json_response(response)
        
        # Should return structure with defaults
        assert "theme" in result
        assert "audience" in result
        assert "intent" in result
        assert "detected_focus_area" in result
        assert result["intent"] == "inform"
        assert result["detected_focus_area"] == "Unknown"


# ============================================================================
# REASONING AGENT TESTS (T025-T028)
# ============================================================================

class TestReasoningAgentOutlineGeneration:
    """Test T025-T027: Outline generation with GPT-4."""

    @patch("backend.agents.reasoning_agent.ModelRouter")
    def test_generate_outline_basic(self, mock_model_router):
        """Test basic outline generation."""
        outline_response = json.dumps({
            "content_angle": "Why AI is transforming healthcare through early diagnosis",
            "why_this_matters": "Early diagnosis saves lives and reduces healthcare costs",
            "outline_rationale": "Structure moves from problem to solution to implementation",
            "sections": [
                {
                    "title": "The Healthcare Diagnosis Challenge",
                    "description": "Current limitations in diagnosis speed and accuracy"
                },
                {
                    "title": "AI Technologies in Medical Imaging",
                    "description": "How machine learning analyzes X-rays, MRIs, and CT scans"
                },
                {
                    "title": "Real-World Hospital Case Studies",
                    "description": "Examples of AI implementation in major hospitals"
                },
                {
                    "title": "Implementation Challenges and Solutions",
                    "description": "Integration with existing hospital systems"
                },
                {
                    "title": "The Future of AI-Powered Diagnosis",
                    "description": "Where the technology is heading in the next 5 years"
                }
            ]
        })
        
        mock_router = Mock()
        mock_router.call.return_value = outline_response
        mock_model_router.return_value = mock_router
        
        topic_data = {
            "topic": "AI in healthcare",
            "theme": "How AI is transforming medical diagnosis",
            "audience": "Hospital administrators",
            "intent": "inform",
            "focus_area": "AI",
            "is_out_of_scope": False
        }
        
        agent = ReasoningAgent()
        outline = agent.generate_outline(topic_data)
        
        # Assertions
        assert outline["topic"] == "AI in healthcare"
        assert len(outline["sections"]) == 5
        assert outline["num_sections"] == 5
        assert "AI is transforming healthcare" in outline["content_angle"].lower()
        assert outline["target_audience"] == "Hospital administrators"
        assert outline["primary_intent"] == "inform"
        
        # Validate section structure
        for i, section in enumerate(outline["sections"]):
            assert "title" in section
            assert "description" in section
            assert "order" in section
            assert section["order"] == i + 1

    @patch("backend.agents.reasoning_agent.ModelRouter")
    def test_generate_outline_section_count(self, mock_model_router):
        """Test that outline has 4-6 sections."""
        def create_sections(count):
            return [
                {"title": f"Section {i+1}", "description": f"Description {i+1}"}
                for i in range(count)
            ]
        
        mock_router = Mock()
        mock_model_router.return_value = mock_router
        
        agent = ReasoningAgent()
        
        # Test various section counts
        for section_count in [4, 5, 6]:
            outline_response = json.dumps({
                "content_angle": "Test angle",
                "why_this_matters": "Test reason",
                "outline_rationale": "Test rationale",
                "sections": create_sections(section_count)
            })
            mock_router.call.return_value = outline_response
            
            topic_data = {
                "topic": "Test topic",
                "theme": "Test theme",
                "audience": "Test audience",
                "intent": "inform",
                "focus_area": "AI"
            }
            
            outline = agent.generate_outline(topic_data)
            
            assert outline["num_sections"] == section_count

    @patch("backend.agents.reasoning_agent.ModelRouter")
    def test_generate_outline_with_various_intents(self, mock_model_router):
        """Test outline generation with different intent types."""
        intents = ["inform", "persuade", "entertain", "guide", "challenge"]
        
        mock_router = Mock()
        mock_model_router.return_value = mock_router
        
        agent = ReasoningAgent()
        
        for intent in intents:
            outline_response = json.dumps({
                "content_angle": f"Angle for {intent}",
                "why_this_matters": "Test reason",
                "outline_rationale": "Test rationale",
                "sections": [
                    {"title": f"Section {i+1}", "description": f"Description {i+1}"}
                    for i in range(4)
                ]
            })
            mock_router.call.return_value = outline_response
            
            topic_data = {
                "topic": "Test topic",
                "theme": "Test theme",
                "audience": "Test audience",
                "intent": intent,
                "focus_area": "AI"
            }
            
            outline = agent.generate_outline(topic_data)
            
            assert outline["primary_intent"] == intent


class TestReasoningAgentJsonParsing:
    """Test JSON parsing for outline generation responses."""

    def test_parse_outline_json_plain(self):
        """Test parsing plain outline JSON."""
        response = json.dumps({
            "content_angle": "Test angle",
            "why_this_matters": "Test reason",
            "outline_rationale": "Test rationale",
            "sections": [
                {"title": "Section 1", "description": "Description 1"}
            ]
        })
        
        result = ReasoningAgent._parse_json_response(response)
        
        assert result["content_angle"] == "Test angle"
        assert result["why_this_matters"] == "Test reason"
        assert len(result["sections"]) == 1

    def test_parse_outline_json_with_markdown(self):
        """Test parsing outline JSON with markdown code block."""
        response = """```json
{
  "content_angle": "Test angle",
  "why_this_matters": "Test reason",
  "outline_rationale": "Test rationale",
  "sections": [
    {"title": "Section 1", "description": "Description 1"}
  ]
}
```"""
        
        result = ReasoningAgent._parse_json_response(response)
        
        assert result["content_angle"] == "Test angle"
        assert len(result["sections"]) == 1

    def test_parse_outline_json_malformed_fallback(self):
        """Test fallback for malformed outline JSON."""
        response = "Not valid JSON at all"
        
        result = ReasoningAgent._parse_json_response(response)
        
        # Should return structure with defaults
        assert "content_angle" in result
        assert "sections" in result
        assert result["content_angle"] == ""
        assert result["sections"] == []


class TestReasoningAgentValidation:
    """Test T028: Outline validation."""

    def test_validate_outline_valid(self):
        """Test validation of valid outline."""
        outline = {
            "topic": "Test topic",
            "sections": [
                {"title": "S1", "description": "D1", "order": 1},
                {"title": "S2", "description": "D2", "order": 2},
                {"title": "S3", "description": "D3", "order": 3},
                {"title": "S4", "description": "D4", "order": 4},
            ],
            "content_angle": "Test angle",
            "target_audience": "Test audience",
            "primary_intent": "inform"
        }
        
        agent = ReasoningAgent()
        assert agent.validate_outline(outline) == True

    def test_validate_outline_missing_required_fields(self):
        """Test validation fails with missing fields."""
        incomplete_outlines = [
            {"sections": []},  # Missing topic
            {"topic": "Test"},  # Missing sections
            {"topic": "Test", "sections": []},  # Missing content_angle, etc.
        ]
        
        agent = ReasoningAgent()
        
        for outline in incomplete_outlines:
            assert agent.validate_outline(outline) == False

    def test_validate_outline_insufficient_sections(self):
        """Test validation fails with too few sections."""
        outline = {
            "topic": "Test topic",
            "sections": [
                {"title": "S1", "description": "D1", "order": 1},
                {"title": "S2", "description": "D2", "order": 2},
                {"title": "S3", "description": "D3", "order": 3},
            ],  # Only 3 sections (need at least 4)
            "content_angle": "Test angle",
            "target_audience": "Test audience",
            "primary_intent": "inform"
        }
        
        agent = ReasoningAgent()
        assert agent.validate_outline(outline) == False

    def test_validate_outline_section_structure(self):
        """Test validation of section structure."""
        # Missing title in one section
        outline = {
            "topic": "Test topic",
            "sections": [
                {"title": "S1", "description": "D1", "order": 1},
                {"description": "D2", "order": 2},  # Missing title
                {"title": "S3", "description": "D3", "order": 3},
                {"title": "S4", "description": "D4", "order": 4},
            ],
            "content_angle": "Test angle",
            "target_audience": "Test audience",
            "primary_intent": "inform"
        }
        
        agent = ReasoningAgent()
        assert agent.validate_outline(outline) == False


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestAgentIntegration:
    """Test agents working together."""

    @patch("backend.agents.reasoning_agent.ModelRouter")
    @patch("backend.agents.input_agent.ModelRouter")
    @patch("backend.agents.input_agent.get_reference_data")
    def test_input_to_reasoning_workflow(
        self, mock_ref_data, mock_input_router, mock_reasoning_router
    ):
        """Test complete workflow from input extraction to outline generation."""
        # Set up input agent mocks
        input_response = json.dumps({
            "theme": "How AI is transforming healthcare",
            "audience": "Hospital administrators",
            "intent": "inform",
            "detected_focus_area": "AI"
        })
        
        mock_input_llm = Mock()
        mock_input_llm.call.return_value = input_response
        mock_input_router.return_value = mock_input_llm
        
        mock_ref_inst = Mock()
        mock_ref_inst.get_focus_areas.return_value = [
            {"id": "AI", "name": "Artificial Intelligence", "description": "AI topics"}
        ]
        mock_ref_data.return_value = mock_ref_inst
        
        # Set up reasoning agent mocks
        outline_response = json.dumps({
            "content_angle": "Why AI is transforming healthcare",
            "why_this_matters": "Early diagnosis saves lives",
            "outline_rationale": "Structure from problem to solution",
            "sections": [
                {"title": "The Problem", "description": "Current challenges"},
                {"title": "AI Solutions", "description": "How AI helps"},
                {"title": "Case Studies", "description": "Real examples"},
                {"title": "Implementation", "description": "How to adopt"},
                {"title": "Future", "description": "What's next"}
            ]
        })
        
        mock_reasoning_llm = Mock()
        mock_reasoning_llm.call.return_value = outline_response
        mock_reasoning_router.return_value = mock_reasoning_llm
        
        # Test workflow
        input_agent = InputAgent()
        topic_data = input_agent.extract_topic_info("AI in healthcare")
        
        reasoning_agent = ReasoningAgent()
        outline = reasoning_agent.generate_outline(topic_data)
        
        # Validate results
        assert topic_data["focus_area"] == "AI"
        assert topic_data["is_out_of_scope"] == False
        assert outline["num_sections"] == 5
        assert reasoning_agent.validate_outline(outline)


# ============================================================================
# SINGLETON TESTS
# ============================================================================

class TestSingletons:
    """Test singleton instances."""

    @patch("backend.agents.input_agent.InputAgent")
    def test_get_input_agent_singleton(self, mock_class):
        """Test InputAgent singleton behavior."""
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        # Import fresh
        from backend.agents.input_agent import get_input_agent as get_agent
        
        # Get instance twice
        instance1 = get_agent()
        instance2 = get_agent()
        
        # Should be same instance (singleton)
        assert instance1 is instance2

    @patch("backend.agents.reasoning_agent.ReasoningAgent")
    def test_get_reasoning_agent_singleton(self, mock_class):
        """Test ReasoningAgent singleton behavior."""
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        
        # Import fresh
        from backend.agents.reasoning_agent import get_reasoning_agent as get_agent
        
        # Get instance twice
        instance1 = get_agent()
        instance2 = get_agent()
        
        # Should be same instance (singleton)
        assert instance1 is instance2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
