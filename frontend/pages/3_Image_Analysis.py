import streamlit as st
import requests
import base64
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.local_fallbacks import add_local_incident
from frontend.profile_state import get_profile, render_auth_sidebar

try:
    st.set_page_config(page_title="SafeSphere Vision Assessment", layout="wide", initial_sidebar_state="expanded")
except Exception:
    pass
inject_custom_styles()
# render_auth_sidebar()  # Handled globally in app.py

st.markdown("<h1 class='gradient-header'>Vision Damage Assessment</h1>", unsafe_allow_html=True)
st.markdown("Upload a photo of the emergency scene. Gemini Vision AI will analyze structural safety, flood levels, road blockages, and recommend immediate actions.")

profile = get_profile()
user_lat = profile.get("location_lat") or 19.0760
user_lng = profile.get("location_lng") or 72.8777
user_loc = profile.get("location_address") or "Mumbai"

uploaded_file = st.file_uploader("Choose a disaster image (Flood, Fire, Building Collapse, Road Blockage)...", type=["jpg", "jpeg", "png"])


def _local_vision_assessment(file_name: str) -> dict:
    name = file_name.lower()
    if "fire" in name:
        disaster_type = "Fire"
        road_condition = "Possible smoke or access restriction. Verify safe entry before approaching."
    elif "collapse" in name or "building" in name:
        disaster_type = "Collapse"
        road_condition = "Access may be blocked by debris. Keep distance from unstable structures."
    elif "flood" in name or "rain" in name:
        disaster_type = "Flood"
        road_condition = "Waterlogging or submerged road sections may be present."
    else:
        disaster_type = "Other"
        road_condition = "Scene needs manual verification by responders."

    return {
        "disaster_type": disaster_type,
        "severity": "Medium",
        "confidence_score": 0.55,
        "people_visible": False,
        "risk_level": "Needs manual verification",
        "road_condition": road_condition,
        "structural_damage": "Offline mode cannot inspect image details. Treat the scene as potentially unsafe until verified.",
        "immediate_actions": [
            "Keep people away from the affected area.",
            "Share the exact location with emergency responders.",
            "Do not touch damaged electrical lines, unstable walls, or contaminated floodwater.",
            "Use backend AI analysis when available for detailed visual assessment.",
        ],
    }

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Emergency Image", use_container_width=True)
    
    # Analyze button
    if st.button("Trigger Vision AI Assessment", width="stretch"):
        with st.spinner("Analyzing image features and running damage risk calculations..."):
            try:
                # 1. Read bytes and convert to base64
                file_bytes = uploaded_file.read()
                b64_image = base64.b64encode(file_bytes).decode("utf-8")
                
                # 2. Build payload triggering LangGraph execute
                # We target the Vision node directly by asking a vision-specific prompt
                payload = {
                    "user_query": "Analyze image damage in details: disaster type, severity, people visible, road condition, structural damage, risk level, immediate actions.",
                    "user_location": user_loc,
                    "user_lat": user_lat,
                    "user_lng": user_lng,
                    "user_language": "English",
                    "image_data_b64": b64_image,
                    "image_name": uploaded_file.name
                }
                
                res = requests.post("http://localhost:8000/api/chat/execute", json=payload, timeout=3)
                
                if res.status_code == 200:
                    data = res.json()
                    va = data["vision_assessment"]
                    is_live = True
                else:
                    va = _local_vision_assessment(uploaded_file.name)
                    is_live = False
            except requests.RequestException:
                va = _local_vision_assessment(uploaded_file.name)
                is_live = False

            if va:
                st.session_state["last_vision_assessment"] = va
                st.session_state["last_vision_is_live"] = is_live
                st.session_state["last_vision_location"] = user_loc
                st.session_state["last_vision_lat"] = user_lat
                st.session_state["last_vision_lng"] = user_lng
            else:
                st.warning("No assessment could be generated for this image.")

    va = st.session_state.get("last_vision_assessment")
    is_live = st.session_state.get("last_vision_is_live", False)
    if va:
        if is_live:
            st.success("Vision Analysis Complete!")
        else:
            st.info("Backend vision analysis is unavailable, so a local safety assessment is shown.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Assessment Scorecard")
            sev = va.get("severity", "Medium")
            sev_class = "indicator-critical" if sev == "Critical" else ("indicator-high" if sev == "High" else ("indicator-medium" if sev == "Medium" else "indicator-low"))

            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="details-row">
                        <span class="details-label">Disaster Type</span>
                        <span class="details-value">{va.get('disaster_type')}</span>
                    </div>
                    <div class="details-row">
                        <span class="details-label">Severity Level</span>
                        <span class="indicator-tag {sev_class}" style="margin: 0;">{sev}</span>
                    </div>
                    <div class="details-row">
                        <span class="details-label">Vision Confidence</span>
                        <span class="details-value">{int(va.get('confidence_score', 0.9) * 100)}%</span>
                    </div>
                    <div class="details-row">
                        <span class="details-label">Visible People Trapped</span>
                        <span class="details-value">{'YES ' if va.get('people_visible') else 'None visible'}</span>
                    </div>
                    <div class="details-row">
                        <span class="details-label">Risk Level</span>
                        <span class="details-value" style="color: #fca5a5;">{va.get('risk_level')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown("### Scene Details")
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="margin-bottom: 12px;">
                        <span style="color: #9fb0c3; font-weight: 500; font-size: 0.85rem;">ROAD CONDITION:</span><br>
                        <span style="color: #f8fafc; font-weight: 600;"> {va.get('road_condition')}</span>
                    </div>
                    <div style="margin-bottom: 12px;">
                        <span style="color: #9fb0c3; font-weight: 500; font-size: 0.85rem;">STRUCTURAL INTEGRITY:</span><br>
                        <span style="color: #f8fafc; font-weight: 600;"> {va.get('structural_damage')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("### Immediate Recommended Actions")
        actions_html = "<div class='glass-card' style='border-left: 5px solid #f87171;'>"
        for act in va.get("immediate_actions", []):
            actions_html += f"<p style='margin: 8px 0; color: #cbd7e3; font-weight: 500;'> {act}</p>"
        actions_html += "</div>"
        st.markdown(actions_html, unsafe_allow_html=True)

        st.markdown("### File Incident from Image")
        if st.button("Log as Active Incident"):
            report_payload = {
                "title": f"Image Reported {va['disaster_type']} - Proximity: {st.session_state.get('last_vision_location', user_loc)}",
                "description": f"Image assessment detected {va['disaster_type']} with {va['severity']} severity. structural condition: {va['structural_damage']}. road status: {va['road_condition']}.",
                "location_lat": st.session_state.get("last_vision_lat", user_lat),
                "location_lng": st.session_state.get("last_vision_lng", user_lng),
                "address": st.session_state.get("last_vision_location", user_loc),
                "disaster_type": va["disaster_type"],
                "severity": va["severity"],
                "assessment_details": va
            }
            try:
                res_report = requests.post("http://localhost:8000/api/incidents/report", json=report_payload, timeout=2)
                if res_report.status_code == 200:
                    st.success("Incident registered in main feed.")
                elif add_local_incident(report_payload):
                    st.success("Incident saved locally.")
                else:
                    st.warning("Incident could not be saved locally.")
            except requests.RequestException:
                if add_local_incident(report_payload):
                    st.success("Backend is offline, so the incident was saved locally.")
                else:
                    st.warning("Backend is offline and the local incident could not be saved.")
