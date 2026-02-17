"""
History Page
View past sessions and continue interrupted work
Path: frontend/pages/2_History.py
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import requests
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.logger import frontend_logger

# Configure page
st.set_page_config(
    page_title="History - Content Studio",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("🎨 Content Studio")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "New Session", "History", "Settings"],
    index=2
)

# Navigate to other pages
if page == "Home":
    st.switch_page("pages/../Home.py")
elif page == "New Session":
    st.switch_page("pages/1_New_Session.py")
elif page == "Settings":
    st.switch_page("pages/3_Settings.py")

# Main title
st.markdown("# 📚 Session History")
st.markdown("View and continue your previous content sessions.")

# Backend API base URL
API_URL = "http://localhost:8000/api"

# Fetch sessions
def load_sessions():
    try:
        response = requests.get(f"{API_URL}/sessions", timeout=10)
        response.raise_for_status()
        data = response.json()
        sessions = data.get('sessions', [])
        total = data.get('total', 0)
        return sessions, total
    except requests.exceptions.ConnectionError:
        return [], 0
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error loading sessions: {str(e)}")
        frontend_logger.error(f"Error loading sessions: {e}")
        return [], 0

with st.spinner("⏳ Loading sessions..."):
    sessions, total = load_sessions()

# Display stats
if total > 0:
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 0.8])
    
    with col1:
        st.metric("Total Sessions", total)
    
    with col2:
        completed = len([s for s in sessions if s.get('status') == 'completed'])
        st.metric("Completed", completed)
    
    with col3:
        in_progress = len([s for s in sessions if s.get('status') in ['outline_review', 'framework_selection', 'generating_content', 'platform_review', 'iterating']])
        st.metric("In Progress", in_progress)
    
    with col4:
        abandoned = len([s for s in sessions if s.get('status') == 'abandoned'])
        st.metric("Abandoned", abandoned)
    
    with col5:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["All Sessions", "In Progress", "Completed"])
    
    # TAB 1: All Sessions
    with tab1:
        if sessions:
            # Create dataframe
            session_data = []
            for session in sessions:
                session_data.append({
                    "ID": session.get('id', '')[:12] + "...",
                    "Topic": session.get('topic', 'Untitled')[:50],
                    "Status": session.get('status', 'unknown'),
                    "Iterations": session.get('iteration_count', 0),
                    "Created": datetime.fromisoformat(session.get('created_at', '')).strftime('%m/%d %H:%M') if session.get('created_at') else 'N/A',
                    "Updated": datetime.fromisoformat(session.get('updated_at', '')).strftime('%m/%d %H:%M') if session.get('updated_at') else 'N/A',
                    "Full ID": session.get('id', '')
                })
            
            df = pd.DataFrame(session_data)
            
            # Display table
            st.dataframe(
                df[['Topic', 'Status', 'Iterations', 'Created', 'Updated']],
                use_container_width=True,
                hide_index=True
            )
            
            # Session details on click
            st.markdown("### Session Details")
            selected_topic = st.selectbox(
                "Select a session to view details:",
                options=df['Topic'].tolist(),
                key="session_select_all"
            )
            
            if selected_topic:
                session_row = df[df['Topic'] == selected_topic].iloc[0]
                session_id = session_row['Full ID']
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Topic**: {session_row['Topic']}")
                    st.markdown(f"**Status**: `{session_row['Status']}`")
                    st.markdown(f"**Iterations**: {session_row['Iterations']}")
                    st.markdown(f"**Created**: {session_row['Created']}")
                    st.markdown(f"**Updated**: {session_row['Updated']}")
                
                with col2:
                    col_resume, col_export, col_delete = st.columns(3)
                    
                    with col_resume:
                        if st.button("▶️ Resume", key=f"resume_{session_id}", type="primary", use_container_width=True):
                            st.session_state.continue_session_id = session_id
                            st.success(f"✅ Session {session_id[:8]}... loaded. Continuing...")
                            st.switch_page("pages/1_New_Session.py")
                    
                    with col_export:
                        if st.button("📥 Export", key=f"export_{session_id}", use_container_width=True):
                            try:
                                export_response = requests.post(
                                    f"{API_URL}/sessions/{session_id}/export",
                                    timeout=10
                                )
                                export_response.raise_for_status()
                                export_data = export_response.json()
                                
                                st.download_button(
                                    label="💾 Download JSON",
                                    data=export_data.get('json_content', '{}'),
                                    file_name=f"session_{session_id[:8]}.json",
                                    mime="application/json",
                                    key=f"download_{session_id}"
                                )
                            except Exception as e:
                                st.error(f"❌ Export failed: {str(e)}")
                                frontend_logger.error(f"Export error: {e}")
                    
                    with col_delete:
                        if st.button("🗑️ Delete", key=f"delete_{session_id}", use_container_width=True):
                            try:
                                delete_response = requests.delete(
                                    f"{API_URL}/sessions/{session_id}",
                                    timeout=10
                                )
                                delete_response.raise_for_status()
                                st.success(f"✅ Session deleted")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Delete failed: {str(e)}")
                                frontend_logger.error(f"Delete error: {e}")
        else:
            st.info("📭 No sessions found. Create a new session to get started!")
    
    # TAB 2: In Progress
    with tab2:
        in_progress_sessions = [s for s in sessions if s.get('status') in ['outline_review', 'framework_selection', 'generating_content', 'platform_review', 'iterating']]
        
        if in_progress_sessions:
            for session in in_progress_sessions:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{session.get('topic', 'Untitled')[:80]}**")
                        st.caption(f"Status: {session.get('status')} • Iterations: {session.get('iteration_count', 0)}")
                    
                    with col2:
                        st.caption(f"{datetime.fromisoformat(session.get('updated_at', '')).strftime('%m/%d %H:%M') if session.get('updated_at') else 'N/A'}")
                    
                    with col3:
                        if st.button("▶️ Continue", key=f"continue_progress_{session.get('id')}"):
                            st.info(f"🔄 Continuing session")
        else:
            st.info("✅ No sessions in progress")
    
    # TAB 3: Completed
    with tab3:
        completed_sessions = [s for s in sessions if s.get('status') == 'completed']
        
        if completed_sessions:
            for session in completed_sessions:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"✅ **{session.get('topic', 'Untitled')[:80]}**")
                        st.caption(f"Completed with {session.get('iteration_count', 0)} iterations")
                    
                    with col2:
                        if st.button("📋 View Details", key=f"view_completed_{session.get('id')}"):
                            st.info("📋 Details view not yet implemented")
        else:
            st.info("📭 No completed sessions yet. Complete a full workflow to see them here!")

else:
    st.info("""
    ### 👋 No sessions yet
    
    Get started by creating a new session:
    1. Click "New Session" from the sidebar
    2. Enter a topic
    3. Approve the generated outline
    4. Generate and iterate on content
    5. Review platform-specific versions
    6. Mark as complete when satisfied
    """)
    
    if st.button("➕ Create New Session", type="primary"):
        st.switch_page("pages/1_New_Session.py")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    💡 All sessions are saved locally in your home directory
    <br/>
    🔐 No data is uploaded to external servers
</div>
""", unsafe_allow_html=True)
