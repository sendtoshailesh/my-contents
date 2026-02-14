"""
New Session Page
User Story 1 - Input & Outline Generation
Path: streamlit run frontend/Home.py then select "New Session"
Run with: streamlit run frontend/pages/1_New_Session.py
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import requests
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.logger import frontend_logger
from backend.utils.reference_data import get_reference_data
from services.framework_engine import get_framework_engine
from frontend.components.framework_selector import render_framework_selector
from frontend.components.content_preview import render_content_preview

# Configure page
st.set_page_config(
    page_title="New Session - Content Studio",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("🎨 Content Studio")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "New Session", "History", "Settings"],
    index=1
)

# Navigate to other pages
if page == "Home":
    st.switch_page("pages/frontend/Home.py")
elif page == "History":
    st.switch_page("pages/2_History.py")
elif page == "Settings":
    st.switch_page("pages/3_Settings.py")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "current_step" not in st.session_state:
    st.session_state.current_step = "input"  # input, generating, review, approved
if "outline_data" not in st.session_state:
    st.session_state.outline_data = None
if "validation_report" not in st.session_state:
    st.session_state.validation_report = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "error_message" not in st.session_state:
    st.session_state.error_message = None
if "framework_plan" not in st.session_state:
    st.session_state.framework_plan = None
if "content_draft" not in st.session_state:
    st.session_state.content_draft = None
if "generation_attempts" not in st.session_state:
    st.session_state.generation_attempts = 0

# Backend API base URL
API_URL = "http://localhost:8000/api"


def _fetch_outline(session_id: str):
    response = requests.get(f"{API_URL}/sessions/{session_id}/outline", timeout=10)
    response.raise_for_status()
    return response.json()


def _fetch_validation(session_id: str):
    response = requests.get(f"{API_URL}/sessions/{session_id}/validation", timeout=10)
    response.raise_for_status()
    return response.json()


def _approve_outline(session_id: str, approved: bool):
    response = requests.post(
        f"{API_URL}/sessions/{session_id}/approve",
        json={"approved": approved},
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def _fetch_frameworks():
    response = requests.get(f"{API_URL}/frameworks", timeout=10)
    response.raise_for_status()
    return response.json().get("frameworks", [])


def _select_framework(session_id: str, framework_id: str, visual_opt_in: bool, visual_preferences):
    response = requests.post(
        f"{API_URL}/sessions/{session_id}/framework",
        json={
            "framework_id": framework_id,
            "visual_opt_in": visual_opt_in,
            "visual_preferences": visual_preferences
        },
        timeout=20
    )
    response.raise_for_status()
    return response.json()


def _generate_content(session_id: str, framework_choice: str, visual_plan, include_code: bool):
    response = requests.post(
        f"{API_URL}/sessions/{session_id}/content",
        json={
            "framework_choice": framework_choice,
            "visual_plan": visual_plan,
            "include_code": include_code
        },
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def _get_content(session_id: str):
    response = requests.get(f"{API_URL}/sessions/{session_id}/content", timeout=10)
    response.raise_for_status()
    return response.json()

# Main title
st.markdown("# ✍️ Start a New Session")
st.markdown("Enter a topic or URL and we'll generate a fact-checked outline.")

# Get reference data for focus areas
try:
    ref_data = get_reference_data()
    focus_areas = ref_data.get_focus_areas()
except Exception as e:
    frontend_logger.error(f"Error loading focus areas: {e}")
    focus_areas = {}

if isinstance(focus_areas, list):
    focus_area_map = {area.get("id", area.get("name", "")): area for area in focus_areas}
else:
    focus_area_map = focus_areas

# Step 1: Input
if st.session_state.current_step == "input":
    st.markdown("## 📝 Step 1: Tell us your topic")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic_input = st.text_area(
            "Topic or description",
            placeholder="e.g., AI and Emotional Intelligence in Leadership",
            height=100,
            help="Describe the topic you want to create content about"
        )
    
    with col2:
        st.markdown("### Focus Area")
        focus_area = st.selectbox(
            "Select a focus area",
            options=list(focus_area_map.keys()),
            format_func=lambda x: focus_area_map[x].get('name', x),
            help="Choose the closest match to your topic"
        )
    
    st.divider()
    
    # Optional: URL input
    with st.expander("📎 Add a URL (optional)"):
        url_input = st.text_input(
            "URL or link",
            placeholder="https://example.com/article...",
            help="Optionally provide a URL to extract content from"
        )
    
    st.divider()
    
    # Display selected focus area details
    if focus_area:
        focus_details = focus_area_map.get(focus_area, {})
        is_in_scope = focus_details.get('is_active', True)
        
        if not is_in_scope:
            st.warning(
                f"⚠️ **Out of Scope**: '{focus_details.get('name')}' is outside our primary focus areas. "
                f"You can continue, but content quality may be lower.",
                icon="⚠️"
            )
        else:
            st.info(
                f"✅ **{focus_details.get('name')}**: {focus_details.get('description')}",
                icon="ℹ️"
            )
    
    st.divider()
    
    # Create buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Generate Outline", key="generate_btn", type="primary"):
            if not topic_input.strip():
                st.error("❌ Please enter a topic")
            else:
                # Call backend to create session and generate outline
                try:
                    st.session_state.processing = True
                    
                    with st.spinner("🔄 Creating session and generating outline..."):
                        # Step 1: Create session
                        session_response = requests.post(
                            f"{API_URL}/sessions",
                            json={
                                "topic": topic_input,
                                "url": url_input
                            },
                            timeout=10
                        )
                        session_response.raise_for_status()
                        session_data = session_response.json()
                        st.session_state.session_id = session_data['id']
                        
                        frontend_logger.info(f"✅ Created session: {st.session_state.session_id}")
                        
                        # Step 2: Generate outline (placeholder endpoint for now)
                        # In Phase 3, this will call the actual agent workflow
                        st.session_state.current_step = "generating"
                        st.session_state.processing = False
                        st.rerun()
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error: {str(e)}")
                    frontend_logger.error(f"Error creating session: {e}")
                    st.session_state.processing = False
    
    with col2:
        pass
    
    with col3:
        if st.button("⚙️ Settings"):
            st.switch_page("pages/3_Settings.py")

# Step 2: Generating
elif st.session_state.current_step == "generating":
    st.markdown("## ⏳ Generating outline...")

    st.info("The backend is processing your outline. This can take a moment.")

    if st.session_state.generation_attempts < 1:
        st.session_state.generation_attempts += 1
        with st.spinner("Checking for outline..."):
            for _ in range(5):
                try:
                    outline_data = _fetch_outline(st.session_state.session_id)
                    validation_data = _fetch_validation(st.session_state.session_id)

                    st.session_state.outline_data = outline_data
                    st.session_state.validation_report = validation_data
                    st.session_state.current_step = "review"
                    st.rerun()
                except requests.exceptions.RequestException:
                    time.sleep(1)

    if st.button("🔄 Check status", type="primary"):
        try:
            outline_data = _fetch_outline(st.session_state.session_id)
            validation_data = _fetch_validation(st.session_state.session_id)

            st.session_state.outline_data = outline_data
            st.session_state.validation_report = validation_data
            st.session_state.current_step = "review"
            st.rerun()
        except requests.exceptions.RequestException as e:
            st.warning("Outline still processing or not ready yet.")
            frontend_logger.info(f"Outline not ready: {e}")

    if st.button("← Back to Input"):
        st.session_state.current_step = "input"
        st.session_state.session_id = None
        st.session_state.generation_attempts = 0
        st.rerun()

# Step 3: Review & Approve
elif st.session_state.current_step == "review":
    st.markdown("## 📋 Review & Approve Outline")

    outline_data = st.session_state.outline_data or {}
    validation_data = st.session_state.validation_report or {}

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Outline Preview")
        st.markdown(f"**Content angle:** {outline_data.get('content_angle', '')}")
        st.markdown("**Sections**")
        for section in outline_data.get("sections", []):
            st.markdown(f"- {section.get('order', '')}. {section.get('title', '')}")

    with col2:
        st.markdown("### Validation")
        st.metric("Confidence", f"{validation_data.get('confidence_score', 0) * 100:.0f}%")
        st.write(f"Claims checked: {validation_data.get('claims_checked', 0)}")
        st.write(f"Credible sources: {validation_data.get('credible_sources_found', 0)}")
        if not validation_data.get("passed_validation", False):
            st.warning("Validation failed. Please regenerate.")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Approve", type="primary", key="approve_btn"):
            try:
                _approve_outline(st.session_state.session_id, True)
                st.session_state.current_step = "framework"
                st.rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Approval failed: {e}")

    with col2:
        if st.button("🔄 Regenerate", key="regen_btn"):
            st.session_state.current_step = "generating"
            st.rerun()

    with col3:
        if st.button("← Start Over", key="restart_btn"):
            st.session_state.current_step = "input"
            st.session_state.session_id = None
            st.rerun()

# Step 4: Framework selection
elif st.session_state.current_step == "framework":
    st.markdown("## 🧭 Select Framework & Visuals")

    try:
        frameworks = _fetch_frameworks()
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to load frameworks: {e}")
        frameworks = []

    recommended_id = None
    if st.session_state.outline_data:
        try:
            engine = get_framework_engine()
            recommended_id = engine.recommend_framework(st.session_state.outline_data)
        except Exception as e:
            frontend_logger.warning(f"Framework recommendation failed: {e}")

    if recommended_id:
        st.info(f"Recommended framework: {recommended_id}")

    selected_framework, visual_opt_in, visual_preferences = render_framework_selector(
        frameworks,
        recommended_id=recommended_id,
        key_prefix="framework"
    )

    include_code = st.checkbox("Include code snippets", value=False)

    if st.button("🎯 Generate Visual Plan", type="primary"):
        try:
            plan = _select_framework(
                st.session_state.session_id,
                selected_framework,
                visual_opt_in,
                visual_preferences
            )
            st.session_state.framework_plan = plan
            st.success("Framework plan generated.")
        except requests.exceptions.RequestException as e:
            st.error(f"Framework selection failed: {e}")

    if st.session_state.framework_plan:
        st.markdown("### Visual Plan")
        for visual in st.session_state.framework_plan.get("visual_plan", []):
            st.markdown(f"- Visual {visual.get('visual_id')}: {visual.get('description')}")

        if st.button("✍️ Generate Content Draft", type="primary", key="gen_content"):
            try:
                content = _generate_content(
                    st.session_state.session_id,
                    st.session_state.framework_plan.get("framework_choice"),
                    st.session_state.framework_plan.get("visual_plan"),
                    include_code
                )
                st.session_state.content_draft = content
                st.session_state.current_step = "content"
                st.rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Content generation failed: {e}")

# Step 5: Content preview
elif st.session_state.current_step == "content":
    st.markdown("## ✅ Content Draft")

    if not st.session_state.content_draft and st.session_state.session_id:
        try:
            st.session_state.content_draft = _get_content(st.session_state.session_id)
        except requests.exceptions.RequestException as e:
            st.error(f"Unable to load content draft: {e}")

    render_content_preview(st.session_state.content_draft)

    if st.button("← Back to Framework Selection"):
        st.session_state.current_step = "framework"
        st.rerun()

# Error display
if st.session_state.error_message:
    st.error(f"❌ {st.session_state.error_message}")
    if st.button("Clear error"):
        st.session_state.error_message = None
        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    💡 Tip: More detailed outlines result from specific topics
    <br/>
    📌 Your session is saved and can be accessed from History
</div>
""", unsafe_allow_html=True)
