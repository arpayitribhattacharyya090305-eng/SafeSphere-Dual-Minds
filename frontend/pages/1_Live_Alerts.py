import streamlit as st
import requests
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.auth_helper import AuthHelper

st.set_page_config(page_title="RescueAI Live Alerts", layout="wide")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Live Incident Alerts & Reports</h1>", unsafe_allow_html=True)
st.markdown("Monitor ongoing disasters reported by citizens and validated by Vision AI nodes.")

col_list, col_report = st.columns([2, 1])

# Fetch profile details if logged in
user_lat = 19.0760
user_lng = 72.8777
user_addr = "Mumbai"
if AuthHelper.is_logged_in():
    p = st.session_state["user_profile"]
    user_lat = p.get("location_lat") or 19.0760
    user_lng = p.get("location_lng") or 72.8777
    user_addr = p.get("location_address") or "Mumbai"

with col_report:
    st.markdown("### Report a New Hazard")
    with st.form("incident_form", clear_on_submit=True):
        title = st.text_input("Incident Title", placeholder="e.g. Broken electric wire in flood water")
        desc = st.text_area("Detailed Description", placeholder="Identify hazards, trapped individuals, and damage status...")
        disaster_type = st.selectbox("Disaster Type", ["Flood", "Fire", "Collapse", "Landslide", "Blockage", "Other"])
        severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
        addr = st.text_input("Incident Location Area", value=user_addr)
        
        col_lat, col_lng = st.columns(2)
        lat = col_lat.number_input("Latitude", value=user_lat, format="%.5f")
        lng = col_lng.number_input("Longitude", value=user_lng, format="%.5f")
        
        submit_btn = st.form_submit_button("Report Emergency", use_container_width=True)
        
    if submit_btn and title:
        try:
            headers = AuthHelper.get_headers()
            payload = {
                "title": title,
                "description": desc,
                "location_lat": lat,
                "location_lng": lng,
                "address": addr,
                "disaster_type": disaster_type,
                "severity": severity
            }
            res = requests.post("http://localhost:8000/api/incidents/report", json=payload, headers=headers, timeout=5)
            if res.status_code == 200:
                st.success("Emergency report logged in central command center! Dispatching verification teams.")
                st.rerun()
            else:
                st.error("Failed to post incident: " + res.json().get("detail", "Error"))
        except Exception as e:
            st.error(f"Cannot connect to API backend ({e})")

with col_list:
    st.markdown("### Active Incidents Feed")
    try:
        res = requests.get("http://localhost:8000/api/incidents/list", timeout=5)
        if res.status_code == 200:
            incidents = res.json()
            if not incidents:
                st.info("No active hazards reported in this region. The area is currently secure.")
            else:
                for inc in incidents:
                    sev = inc["severity"]
                    sev_class = "indicator-critical" if sev == "Critical" else ("indicator-high" if sev == "High" else ("indicator-medium" if sev == "Medium" else "indicator-low"))
                    
                    st.markdown(
                        f"""
                        <div class="glass-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin: 0; color: #f8fafc;"> {inc['title']}</h4>
                                <span class="indicator-tag {sev_class}">{sev}</span>
                            </div>
                            <p style="margin: 10px 0; color: #cbd7e3; font-size: 0.92rem;">{inc['description'] or 'No description provided.'}</p>
                            <div style="display: flex; gap: 20px; font-size: 0.8rem; color: #9fb0c3; font-weight: 500;">
                                <span> Area: {inc['address'] or 'N/A'}</span>
                                <span> Coords: {inc['location_lat']:.4f}, {inc['location_lng']:.4f}</span>
                                <span> Status: <b>{inc['status']}</b></span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.error("Failed to load incidents from backend.")
    except Exception as e:
        st.error(f"Failed to connect to API backend ({e})")
