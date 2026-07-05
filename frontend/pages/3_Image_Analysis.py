import streamlit as st
import requests
import base64
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.auth_helper import AuthHelper

st.set_page_config(page_title="RescueAI Vision Assessment", layout="wide")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Vision Damage Assessment</h1>", unsafe_allow_html=True)
st.markdown("Upload a photo of the emergency scene. Gemini Vision AI will analyze structural safety, flood levels, road blockages, and recommend immediate actions.")

# State variables
user_lat = 19.0760
user_lng = 72.8777
user_loc = "Mumbai"
if AuthHelper.is_logged_in():
    p = st.session_state["user_profile"]
    user_lat = p.get("location_lat") or 19.0760
    user_lng = p.get("location_lng") or 72.8777
    user_loc = p.get("location_address") or "Mumbai"

uploaded_file = st.file_uploader("Choose a disaster image (Flood, Fire, Building Collapse, Road Blockage)...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Emergency Image", use_container_width=True)
    
    # Analyze button
    if st.button("Trigger Vision AI Assessment", use_container_width=True):
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
                
                headers = AuthHelper.get_headers()
                res = requests.post("http://localhost:8000/api/chat/execute", json=payload, headers=headers, timeout=20)
                
                if res.status_code == 200:
                    data = res.json()
                    va = data["vision_assessment"]
                    
                    if va:
                        st.success("Vision Analysis Complete!")
                        
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
                        
                        # Save Incident option
                        st.markdown("### File Incident from Image")
                        if st.button("Log as Active Incident in Database"):
                            report_payload = {
                                "title": f"AI Verified {va['disaster_type']} - Proximity: {user_loc}",
                                "description": f"Vision AI detected {va['disaster_type']} with {va['severity']} severity. structural condition: {va['structural_damage']}. road status: {va['road_condition']}.",
                                "location_lat": user_lat,
                                "location_lng": user_lng,
                                "address": user_loc,
                                "disaster_type": va["disaster_type"],
                                "severity": va["severity"],
                                "assessment_details": va
                            }
                            res_report = requests.post("http://localhost:8000/api/incidents/report", json=report_payload, headers=headers, timeout=5)
                            if res_report.status_code == 200:
                                st.success("Incident registered in main feed! Responders have been notified.")
                            else:
                                st.error("Failed to register incident in database.")
                    else:
                        st.error("No assessment generated by the AI node.")
                else:
                    st.error("Error communicating with AI engine backend.")
            except Exception as e:
                st.error(f"Failed to run vision evaluation: {e}")
