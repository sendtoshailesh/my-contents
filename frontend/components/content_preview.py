"""Content preview component."""

from typing import Dict, Any
import streamlit as st

try:
    from streamlit_mermaid import st_mermaid
except Exception:  # pragma: no cover - optional dependency
    st_mermaid = None


def render_content_preview(content_draft: Dict[str, Any]):
    """Render a content draft with visuals and code snippets."""
    if not content_draft:
        st.info("No content draft available.")
        return

    st.markdown("## Draft")
    st.markdown(content_draft.get("body_text", ""))

    visual_plan = content_draft.get("visual_plan")
    if visual_plan and visual_plan.get("visuals"):
        st.markdown("## Visual Plan")
        for visual in visual_plan.get("visuals", []):
            st.markdown(f"**Visual {visual.get('visual_id')}**: {visual.get('description')}")
            code = visual.get("draft_code")
            if code and st_mermaid:
                st_mermaid(code)
            elif code:
                st.code(code, language="text")

    code_snippets = content_draft.get("code_snippets") or []
    if code_snippets:
        st.markdown("## Code Snippets")
        for snippet in code_snippets:
            st.code(snippet.get("code", ""), language=snippet.get("language", "text"))
            if snippet.get("explanation"):
                st.caption(snippet.get("explanation"))
