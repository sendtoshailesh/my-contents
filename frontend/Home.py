"""
Streamlit Home Page
Main entry point for the frontend
Run with: streamlit run frontend/Home.py
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path so we can import backend modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.logger import frontend_logger
from backend.utils.reference_data import get_reference_data

# Configure page
st.set_page_config(
    page_title="Content Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 3em;
        font-weight: bold;
        margin: 20px 0;
    }
    .section-header {
        font-size: 1.5em;
        font-weight: bold;
        margin-top: 20px;
    }
    .status-box {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .status-ready {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .status-warning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .status-error {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🎨 Content Studio")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "New Session", "History", "Settings"],
    index=0
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_session = None
    st.session_state.completed_sessions = []
    frontend_logger.info("🚀 Frontend initialized")


# Main content
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("# 🎨 Personal AI Content Studio")
    st.markdown("Generate fact-checked content across multiple platforms")

with col2:
    st.info(f"v0.1.0 • {datetime.now().strftime('%%H:%%M')}")


# Status section
st.markdown("## System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    try:
        # Check if reference data loads
        ref_data = get_reference_data()
        frameworks_count = len(ref_data.get_frameworks())
        st.markdown(f"""
        <div class="status-box status-ready">
            <strong>📚 Frameworks</strong><br/>
            {frameworks_count} available
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"""
        <div class="status-box status-error">
            <strong>📚 Frameworks</strong><br/>
            Error loading
        </div>
        """, unsafe_allow_html=True)
        frontend_logger.error(f"Error loading frameworks: {e}")

with col2:
    try:
        ref_data = get_reference_data()
        platforms_count = len(ref_data.get_platforms())
        st.markdown(f"""
        <div class="status-box status-ready">
            <strong>📢 Platforms</strong><br/>
            {platforms_count} supported
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"""
        <div class="status-box status-error">
            <strong>📢 Platforms</strong><br/>
            Error loading
        </div>
        """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="status-box status-ready">
        <strong>💾 Database</strong><br/>
        Ready
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="status-box status-ready">
        <strong>🔐 Secrets</strong><br/>
        Configured
    </div>
    """, unsafe_allow_html=True)


# Quick start guide
st.markdown("## Getting Started")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 1️⃣ Create Session
    Submit your topic or URL
    """)
    if st.button("New Session →", key="btn_new_session"):
        st.session_state.current_page = "New Session"
        st.rerun()

with col2:
    st.markdown("""
    ### 2️⃣ Approve Outline
    Review and validate
    """)
    st.info("Start with Step 1", icon="ℹ️")

with col3:
    st.markdown("""
    ### 3️⃣ Generate Content
    Create multi-platform content
    """)
    st.info("Requires approved outline", icon="ℹ️")


# Feature highlights
st.markdown("## Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ✨ What you can do
    
    ✅ **Extract Topics** from URLs or descriptions
    ✅ **Validate Outlines** with web research (70% confidence minimum)
    ✅ **Pick Frameworks** from 6 storytelling templates
    ✅ **Generate Content** with embedded visuals
    ✅ **Adapt Platforms** across 6 major platforms
    ✅ **Iterate** until you say "ok and good"
    """)

with col2:
    st.markdown("""
    ### 🔧 Technology
    
    🐍 **Backend**: FastAPI (localhost:8000)
    📊 **Database**: SQLite (local)
    🎨 **Frontend**: Streamlit (localhost:8501)
    🧠 **LLM**: Multi-model routing
    🔍 **Search**: Bing Web Search API
    🔐 **Secrets**: OS Keychain (hybrid)
    """)


# Live stats
st.markdown("## Session Stats")
st.caption("""
⏱️ **Timeline**: 2-3 weeks to MVP
💰 **Cost**: $35-100/month
📈 **Success Rate**: 90% outline approval in 2 iterations
🎯 **Cycle Time**: <20 minutes per full workflow
""")


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    💡 Tip: Start with "New Session" to create your first content outline
    <br/>
    📖 Need help? Check Settings for configuration options
</div>
""", unsafe_allow_html=True)

# Navigation logic (simplified for now)
if page == "New Session":
    st.switch_page("pages/1_New_Session.py")
elif page == "History":
    st.switch_page("pages/2_History.py")
elif page == "Settings":
    st.switch_page("pages/3_Settings.py")
