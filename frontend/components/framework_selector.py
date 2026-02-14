"""Framework selection component."""

from typing import List, Dict, Optional, Tuple
import streamlit as st


def render_framework_selector(
    frameworks: List[Dict],
    recommended_id: Optional[str] = None,
    key_prefix: str = "framework"
) -> Tuple[Optional[str], bool, List[str]]:
    """Render framework selection UI."""
    if not frameworks:
        st.warning("No frameworks available.")
        return None, True, []

    framework_labels = {fw["id"]: fw.get("name", fw["id"]) for fw in frameworks}
    default_id = recommended_id or frameworks[0]["id"]
    options = list(framework_labels.keys())

    selected = st.radio(
        "Choose a framework",
        options=options,
        index=options.index(default_id) if default_id in options else 0,
        format_func=lambda fw_id: framework_labels.get(fw_id, fw_id),
        key=f"{key_prefix}_selection"
    )

    visual_opt_in = st.checkbox(
        "Include visuals",
        value=True,
        key=f"{key_prefix}_visuals"
    )

    visual_preferences = []
    if visual_opt_in:
        visual_preferences = st.multiselect(
            "Preferred visual types (optional)",
            options=["flowchart", "timeline", "infographic", "architecture", "graph"],
            key=f"{key_prefix}_visual_types"
        )

    return selected, visual_opt_in, visual_preferences
