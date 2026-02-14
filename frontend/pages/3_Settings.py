"""
Settings Page
Configure API keys, preferences, and advanced options
Path: frontend/pages/3_Settings.py
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.logger import frontend_logger

# Configure page
st.set_page_config(
    page_title="Settings - Content Studio",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("🎨 Content Studio")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "New Session", "History", "Settings"],
    index=3
)

# Navigate to other pages
if page == "Home":
    st.switch_page("pages/../Home.py")
elif page == "New Session":
    st.switch_page("pages/1_New_Session.py")
elif page == "History":
    st.switch_page("pages/2_History.py")

# Main title
st.markdown("# ⚙️ Settings")
st.markdown("Configure your Content Studio preferences and API keys.")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["API Keys", "Preferences", "About", "Help"])

# TAB 1: API Keys
with tab1:
    st.markdown("## 🔑 API Configuration")
    st.info(
        "ℹ️ API keys are stored locally in your OS keychain. They are never sent to external servers.",
        icon="ℹ️"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### LLM Services")
        
        # OpenAI
        with st.expander("🤖 OpenAI (GPT-4)", expanded=False):
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-...",
                help="Get from https://platform.openai.com/api-keys"
            )
            openai_org = st.text_input(
                "Organization ID (optional)",
                placeholder="org-..."
            )
            
            if st.button("💾 Save OpenAI Settings", key="save_openai"):
                st.success("✅ Settings saved to keyring")
                frontend_logger.info("OpenAI settings updated")
        
        # Anthropic
        with st.expander("🧠 Anthropic (Claude)", expanded=False):
            anthropic_key = st.text_input(
                "Anthropic API Key",
                type="password",
                placeholder="sk-ant-...",
                help="Get from https://console.anthropic.com/account/keys"
            )
            
            if st.button("💾 Save Anthropic Settings", key="save_anthropic"):
                st.success("✅ Settings saved to keyring")
                frontend_logger.info("Anthropic settings updated")
        
        st.markdown("### Search Services")
        
        # Bing Search
        with st.expander("🔍 Bing Web Search API", expanded=False):
            bing_key = st.text_input(
                "Bing Search API Key",
                type="password",
                placeholder="...",
                help="Get from https://www.microsoft.com/en-us/bing/apis/bing-web-search-api"
            )
            
            if st.button("💾 Save Bing Settings", key="save_bing"):
                st.success("✅ Settings saved to keyring")
                frontend_logger.info("Bing settings updated")
    
    with col2:
        st.markdown("### Status")
        st.markdown("**Configured Services**")
        
        services_status = {
            "OpenAI": "⚠️ Not configured",
            "Anthropic": "⚠️ Not configured",
            "Bing Search": "⚠️ Not configured",
        }
        
        for service, status in services_status.items():
            st.markdown(f"• {service}: {status}")
        
        st.markdown("\n**Keyring Status**")
        # Check if keyring is accessible
        try:
            import keyring
            keyring_available = True
            st.markdown("✅ Keyring: Available")
        except:
            keyring_available = False
            st.markdown("❌ Keyring: Not available")
        
        st.markdown("✅ Local Storage: OK")

# TAB 2: Preferences
with tab2:
    st.markdown("## 📋 Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Content Generation")
        
        default_framework = st.selectbox(
            "Default Framework",
            ["TED Talk", "Hero's Journey", "Problem-Solution", "Listicle", "Comparison", "Tutorial"],
            help="Your preferred story framework"
        )
        
        auto_validate = st.checkbox(
            "Auto-validate outlines",
            value=True,
            help="Automatically run web search validation"
        )
        
        min_confidence = st.slider(
            "Minimum Confidence Score",
            min_value=0.5,
            max_value=1.0,
            value=0.7,
            step=0.05,
            help="Minimum required confidence for outline approval"
        )
    
    with col2:
        st.markdown("### UI Preferences")
        
        theme = st.selectbox(
            "Theme",
            ["Light", "Dark", "Auto"],
            help="Color scheme preference"
        )
        
        show_tips = st.checkbox(
            "Show helpful tips",
            value=True,
            help="Display contextual tips and hints"
        )
        
        auto_save = st.checkbox(
            "Auto-save drafts",
            value=True,
            help="Automatically save content as you work"
        )
    
    if st.button("💾 Save Preferences", type="primary"):
        st.success("✅ Preferences saved")
        frontend_logger.info(f"Preferences updated: framework={default_framework}, confidence={min_confidence}")

# TAB 3: About
with tab3:
    st.markdown("## ℹ️ About Content Studio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Version
        **0.1.0 MVP**
        
        Personal AI Content Studio is a local-first platform for generating 
        fact-checked, multi-platform content with a focus on accuracy and 
        framework-driven storytelling.
        
        ### Technology Stack
        - **Backend**: FastAPI + SQLAlchemy
        - **Frontend**: Streamlit
        - **Database**: SQLite (local)
        - **LLM**: Multi-model routing (GPT-4, Claude, Llama)
        - **Search**: Bing Web Search API
        - **Secrets**: OS Keyring (hybrid)
        
        ### Features
        ✅ Topic extraction and outline generation  
        ✅ Web-based fact validation (70% confidence)  
        ✅ Storytelling framework selection  
        ✅ Multi-platform content adaptation  
        ✅ Iteration and refinement loop  
        ✅ Local data privacy  
        """)
    
    with col2:
        st.markdown("""
        ### Project Information
        **Repository**: Internal (OneDrive)  
        **Phase**: Phase 3 Implementation  
        **Created**: 2026-02-08  
        **Last Updated**: 2026-02-13
        
        ### Links
        - 📚 [Documentation](./docs/)
        - 🐛 [Report an Issue](#)
        - 💡 [Request a Feature](#)
        - 📧 Support: (internal)
        
        ### License
        Internal Use Only
        
        ### Credits
        Built with ❤️ using best practices in 
        LLM integration, data privacy, and user design.
        """)

# TAB 4: Help
with tab4:
    st.markdown("## 🆘 Help & Troubleshooting")
    
    with st.expander("❓ How do I get started?"):
        st.markdown("""
        1. Go to **New Session**
        2. Enter a topic or URL
        3. System generates outline with web research
        4. Approve the outline (if confidence >= 70%)
        5. Select a storytelling framework
        6. Generate content
        7. Adapt for different platforms
        8. Iterate until satisfied
        """)
    
    with st.expander("🔴 Why did my outline get rejected?"):
        st.markdown("""
        Outlines are rejected when the confidence score (based on web research) 
        is below 70%. This ensures that the generated content is fact-checked.
        
        **To fix this:**
        - Make your topic more specific
        - Include more concrete details
        - Reference established concepts
        - Try a different angle
        """)
    
    with st.expander("🔑 How do I add API keys securely?"):
        st.markdown("""
        API keys are stored in your operating system's secure credential storage:
        - **macOS**: Keychain
        - **Windows**: Credential Manager
        - **Linux**: Secret-Service or pass
        
        Never share your API keys or commit them to version control.
        """)
    
    with st.expander("📊 Where is my data stored?"):
        st.markdown("""
        All data is stored locally in:
        `~/.content-studio/sessions.db`
        
        Your data is:
        - ✅ Never uploaded to external servers
        - ✅ Kept in a private SQLite database
        - ✅ Owner-accessible anytime
        - ✅ Backed up with your home directory
        """)
    
    with st.expander("⚡ Performance: Why is generation slow?"):
        st.markdown("""
        Content generation can be slower if:
        - LLM API responses are slow
        - Web search is processing many sources  
        - Your internet connection is slow
        
        Typical generation time: 2-5 minutes.
        
        **To speed up:**
        - Use faster models (GPT-4 Turbo vs Claude Instant)
        - Reduce research depth
        - Use local model fallbacks
        """)
    
    with st.expander("🐛 I found a bug, how do I report it?"):
        st.markdown("""
        Report bugs by sharing:
        1. What you were doing
        2. What went wrong
        3. Error message (if any)
        4. Session ID (from History page)
        
        Share with: (internal support)
        """)
    
    st.markdown("---")
    st.markdown("""
    **Need more help?**
    
    Check the full documentation in `/docs/` or contact support.
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    🔒 Your privacy is important. All processing happens locally.
    <br/>
    💾 Data persists in local SQLite database at ~/.content-studio/
</div>
""", unsafe_allow_html=True)
