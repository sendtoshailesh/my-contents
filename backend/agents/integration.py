"""
Agent Integration Example

Demonstrates how to use InputAgent and ReasoningAgent together
to process a topic from extraction to outline generation.

This is the foundation for the orchestration layer (separate task).
"""

from typing import Dict, Optional
import logging

from backend.agents.input_agent import get_input_agent
from backend.agents.reasoning_agent import get_reasoning_agent

logger = logging.getLogger("backend.agents.integration")


class ContentOutlineWorkflow:
    """
    Simple workflow combining InputAgent and ReasoningAgent.
    
    This demonstrates the MVP 1 critical path:
    User Topic → InputAgent (T021-T024) → ReasoningAgent (T025-T028) → Outline
    
    Example:
        >>> workflow = ContentOutlineWorkflow()
        >>> outline = workflow.process_topic("AI in healthcare")
        >>> print(f"Generated {outline['num_sections']} sections")
    """

    def __init__(self):
        """Initialize workflow with both agents."""
        self.input_agent = get_input_agent()
        self.reasoning_agent = get_reasoning_agent()
        logger.info("✓ ContentOutlineWorkflow initialized")

    def process_topic(self, topic: str, allow_out_of_scope: bool = False) -> Optional[Dict]:
        """
        Process topic through full workflow.
        
        Args:
            topic: User-provided topic string
            allow_out_of_scope: If True, allow processing of out-of-scope topics
        
        Returns:
            Outline dictionary with sections and metadata, or None if failed
        
        Example:
            >>> workflow = ContentOutlineWorkflow()
            >>> outline = workflow.process_topic("AI in healthcare")
            >>> if outline:
            ...     for section in outline['sections']:
            ...         print(f"- {section['title']}")
        """
        logger.info(f"🚀 Processing topic: {topic}")
        
        try:
            # Step 1: Extract topic information (T021-T024)
            logger.info("Step 1: Extracting topic information...")
            topic_data = self.input_agent.extract_topic_info(topic)
            
            # Check out-of-scope status
            if topic_data["is_out_of_scope"]:
                if not allow_out_of_scope:
                    logger.warning(f"⚠ Topic is OUT_OF_SCOPE. Pass allow_out_of_scope=True to override.")
                    logger.warning(f"  Warning: {topic_data['warning']}")
                    return None
                else:
                    logger.warning(f"⚠ Proceeding with OUT_OF_SCOPE topic (override enabled)")
            
            # Log extracted info
            logger.info(f"✓ Topic extracted:")
            logger.info(f"  Theme: {topic_data['theme']}")
            logger.info(f"  Audience: {topic_data['audience']}")
            logger.info(f"  Intent: {topic_data['intent']}")
            logger.info(f"  Focus Area: {topic_data['focus_area']}")
            logger.info(f"  Confidence: {topic_data['confidence']:.2%}")
            
            # Step 2: Generate outline (T025-T028)
            logger.info("Step 2: Generating outline...")
            outline = self.reasoning_agent.generate_outline(topic_data)
            
            # Validate outline
            if not self.reasoning_agent.validate_outline(outline):
                logger.error("❌ Generated outline failed validation")
                return None
            
            # Log outline summary
            logger.info(f"✓ Outline generated:")
            logger.info(f"  Content Angle: {outline['content_angle']}")
            logger.info(f"  Sections: {outline['num_sections']}")
            for section in outline['sections']:
                logger.info(f"    {section['order']}. {section['title']}")
            
            logger.info("✅ Workflow complete")
            return outline
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            raise

    def process_topics_batch(self, topics: list[str]) -> list[Dict]:
        """
        Process multiple topics.
        
        Args:
            topics: List of topic strings
        
        Returns:
            List of outline dictionaries (skips failed topics)
        """
        logger.info(f"📦 Processing batch of {len(topics)} topics...")
        
        outlines = []
        for i, topic in enumerate(topics, 1):
            try:
                logger.info(f"\n[{i}/{len(topics)}] Processing: {topic}")
                outline = self.process_topic(topic)
                if outline:
                    outlines.append(outline)
            except Exception as e:
                logger.warning(f"Skipping topic '{topic}' due to: {e}")
        
        logger.info(f"✓ Processed {len(outlines)}/{len(topics)} topics successfully")
        return outlines


# Example usage
if __name__ == "__main__":
    import logging
    from backend.utils.logger import setup_logging
    
    # Set up logging
    logger = setup_logging("agent_example", level=logging.INFO)
    
    print("\n" + "=" * 80)
    print("🤖 CONTENT OUTLINE WORKFLOW EXAMPLE")
    print("=" * 80)
    
    # Initialize workflow
    workflow = ContentOutlineWorkflow()
    
    # Example 1: Single topic
    print("\n" + "-" * 80)
    print("Example 1: Single Topic (In Scope)")
    print("-" * 80)
    
    outline = workflow.process_topic("AI in healthcare")
    if outline:
        print(f"\n✅ Generated outline for: {outline['topic']}")
        print(f"Content Angle: {outline['content_angle']}")
        print(f"\nOutline Structure ({outline['num_sections']} sections):")
        for section in outline['sections']:
            print(f"\n  {section['order']}. {section['title']}")
            print(f"     {section['description']}")
    
    # Example 2: Out-of-scope topic (without override)
    print("\n" + "-" * 80)
    print("Example 2: Out-of-Scope Topic (Default Behavior)")
    print("-" * 80)
    
    outline = workflow.process_topic("Professional tennis")
    if not outline:
        print("❌ Topic rejected (not in scope)")
    
    # Example 3: Out-of-scope topic (with override)
    print("\n" + "-" * 80)
    print("Example 3: Out-of-Scope Topic (With Override)")
    print("-" * 80)
    
    outline = workflow.process_topic("Professional tennis", allow_out_of_scope=True)
    if outline:
        print(f"✅ Generated outline despite out-of-scope: {outline['topic']}")
    
    # Example 4: Batch processing
    print("\n" + "-" * 80)
    print("Example 4: Batch Processing")
    print("-" * 80)
    
    topics = [
        "Cloud migration strategies",
        "Emotional intelligence in leadership",
        "Quantum computing fundamentals"
    ]
    
    outlines = workflow.process_topics_batch(topics)
    print(f"\n✅ Successfully processed {len(outlines)} topics")
    
    print("\n" + "=" * 80)
    print("✅ EXAMPLE COMPLETE")
    print("=" * 80)
