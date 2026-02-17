"""
Platform Versions Component

Displays all 6 platform-specific content versions with formatting appropriate for each platform.

Platforms:
- LinkedIn: Professional post with hashtags
- Twitter/X: Thread format
- Reddit: Markdown post
- Medium: Article format
- Substack: Newsletter format
- Instagram: Caption with emojis

Usage:
    from frontend.components.platform_versions import render_platform_versions
    
    versions = {...}  # Platform versions dict
    render_platform_versions(versions, session_id)
"""

import streamlit as st
from typing import Dict, List, Optional


def render_platform_versions(
    versions: List[Dict],
    session_id: str,
    show_regenerate: bool = True
):
    """
    Render all platform content versions.
    
    Args:
        versions: List of platform version dicts
        session_id: Current session ID
        show_regenerate: Show regenerate buttons
    """
    st.markdown("### 📱 Platform-Specific Versions")
    st.markdown("Your content adapted for 6 platforms:")
    
    # Platform metadata
    platform_info = {
        "linkedin": {
            "icon": "💼",
            "name": "LinkedIn",
            "description": "Professional network",
            "format": "Article/Post"
        },
        "twitter": {
            "icon": "🐦",
            "name": "Twitter/X",
            "description": "Real-time conversation",
            "format": "Thread"
        },
        "reddit": {
            "icon": "🤖",
            "name": "Reddit",
            "description": "Discussion communities",
            "format": "Markdown Post"
        },
        "medium": {
            "icon": "📝",
            "name": "Medium",
            "description": "Curated blog",
            "format": "Article"
        },
        "substack": {
            "icon": "📧",
            "name": "Substack",
            "description": "Newsletter platform",
            "format": "Newsletter"
        },
        "instagram": {
            "icon": "📸",
            "name": "Instagram",
            "description": "Visual-first social",
            "format": "Caption"
        }
    }
    
    # Display each platform version
    for version in versions:
        platform_id = version.get("platform_name")
        content = version.get("content", "")
        char_count = version.get("character_count", len(content))
        version_num = version.get("version", 1)
        
        if platform_id not in platform_info:
            continue
        
        info = platform_info[platform_id]
        
        with st.expander(
            f"{info['icon']} {info['name']} ({char_count:,} chars) - v{version_num}",
            expanded=False
        ):
            # Platform header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"**{info['description']}** • {info['format']}")
            with col2:
                if show_regenerate:
                    if st.button(f"🔄 Regenerate", key=f"regen_{platform_id}"):
                        st.session_state[f"regenerate_{platform_id}"] = True
                        st.rerun()
            
            # Content preview
            st.markdown("---")
            
            # Platform-specific formatting
            if platform_id == "twitter":
                # Display as numbered thread
                _render_twitter_thread(content)
            
            elif platform_id == "linkedin":
                # Display with professional formatting
                _render_linkedin_post(content)
            
            elif platform_id == "reddit":
                # Display with markdown
                st.markdown(content)
            
            elif platform_id == "medium":
                # Display as article
                _render_medium_article(content)
            
            elif platform_id == "substack":
                # Display as newsletter
                _render_substack_newsletter(content)
            
            elif platform_id == "instagram":
                # Display with emoji formatting
                _render_instagram_caption(content)
            
            else:
                # Default: plain text
                st.text_area(
                    "Content",
                    content,
                    height=200,
                    disabled=True,
                    key=f"content_{platform_id}"
                )
            
            # Copy button
            if st.button(f"📋 Copy to Clipboard", key=f"copy_{platform_id}"):
                st.code(content, language=None)
                st.success(f"✓ {info['name']} content ready to copy!")


def _render_twitter_thread(content: str):
    """Render Twitter thread with tweet numbering."""
    tweets = content.split("\n\n")
    
    for i, tweet in enumerate(tweets, 1):
        if tweet.strip():
            st.markdown(f"**Tweet {i}:**")
            st.info(tweet.strip())


def _render_linkedin_post(content: str):
    """Render LinkedIn post with professional styling."""
    st.markdown(content)
    
    # Extract hashtags (last line usually)
    lines = content.split("\n")
    if lines and "#" in lines[-1]:
        st.caption(lines[-1])


def _render_medium_article(content: str):
    """Render Medium article with headers."""
    # Medium uses markdown, so just render it
    st.markdown(content)


def _render_substack_newsletter(content: str):
    """Render Substack newsletter format."""
    st.markdown(content)


def _render_instagram_caption(content: str):
    """Render Instagram caption with emoji support."""
    st.markdown(content)
    st.caption("💡 Pair with a relevant visual for best engagement")


def render_iteration_controls(session_id: str):
    """
    Render iteration feedback controls.
    
    Args:
        session_id: Current session ID
    """
    st.markdown("### 🔄 Request Improvements")
    
    st.markdown("""
    Not quite perfect yet? Request specific improvements:
    """)
    
    # Feedback areas checkboxes
    st.markdown("**What would you like to improve?**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tone_feedback = st.checkbox("Tone (formality, emotion)")
        depth_feedback = st.checkbox("Depth (level of detail)")
        technical_feedback = st.checkbox("Technicality")
        humor_feedback = st.checkbox("Humor level")
    
    with col2:
        visual_feedback = st.checkbox("Visuals (add/remove/modify)")
        examples_feedback = st.checkbox("Examples")
        structure_feedback = st.checkbox("Structure (organization)")
    
    # Collect selected areas
    feedback_areas = []
    if tone_feedback:
        feedback_areas.append("tone")
    if depth_feedback:
        feedback_areas.append("depth")
    if technical_feedback:
        feedback_areas.append("technicality")
    if humor_feedback:
        feedback_areas.append("humor")
    if visual_feedback:
        feedback_areas.append("visuals")
    if examples_feedback:
        feedback_areas.append("examples")
    if structure_feedback:
        feedback_areas.append("structure")
    
    # Freeform feedback
    feedback_text = st.text_area(
        "Additional feedback (optional):",
        placeholder="E.g., Make it more conversational, add an example about healthcare...",
        height=100
    )
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("🔄 Submit Feedback & Regenerate", type="primary", disabled=not feedback_areas):
            if feedback_areas:
                st.session_state.feedback_areas = feedback_areas
                st.session_state.feedback_text = feedback_text
                st.session_state.submit_feedback = True
                st.rerun()
            else:
                st.warning("Please select at least one improvement area")
    
    with col2:
        if st.button("✅ Ok and Good - Complete Session", type="secondary"):
            st.session_state.complete_session = True
            st.rerun()
    
    with col3:
        if st.button("ℹ️ Help"):
            st.info("""
            **Feedback Areas:**
            - **Tone**: Adjust formality, emotion, voice
            - **Depth**: More/less technical detail
            - **Visuals**: Add, remove, or modify diagrams
            - **Technicality**: Increase/decrease complexity
            - **Humor**: Adjust humor level
            - **Examples**: Add, remove, or change examples
            - **Structure**: Reorganize sections or flow
            
            You can iterate multiple times until satisfied!
            """)


def show_iteration_history(iterations: List[Dict]):
    """
    Show iteration history for a session.
    
    Args:
        iterations: List of iteration feedback dicts
    """
    if not iterations:
        st.info("No iterations yet - content was perfect on first try! ✨")
        return
    
    st.markdown("### 📊 Iteration History")
    
    for iteration in iterations:
        iteration_num = iteration.get("iteration_number", 0)
        feedback_areas = iteration.get("feedback_areas", [])
        feedback_text = iteration.get("feedback_text", "")
        created_at = iteration.get("created_at", "")
        
        with st.expander(f"Iteration #{iteration_num} - {created_at}"):
            st.markdown(f"**Improvement areas:** {', '.join(feedback_areas)}")
            if feedback_text:
                st.markdown(f"**Feedback**: {feedback_text}")
