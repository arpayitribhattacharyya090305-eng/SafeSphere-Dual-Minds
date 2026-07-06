import streamlit as st
import requests
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.local_fallbacks import add_local_volunteer, local_volunteers
from frontend.profile_state import get_profile

st.set_page_config(page_title="SafeSphere Volunteers", layout="wide", initial_sidebar_state="expanded")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Volunteer Matching & Dispatch</h1>", unsafe_allow_html=True)
st.markdown("Register as an emergency volunteer, see active dispatch lists, and match civilian squads with immediate help requests.")

col_reg, col_match = st.columns([1, 2])

profile = get_profile()
user_lat = profile.get("location_lat") or 19.0760
user_lng = profile.get("location_lng") or 72.8777
user_name = profile.get("full_name") or ""
user_email = profile.get("email") or ""

with col_reg:
    st.markdown("### Register as a Volunteer")
    with st.form("volunteer_form", clear_on_submit=True):
        name = st.text_input("Full Name", value=user_name)
        phone = st.text_input("Phone Number", placeholder="e.g. +91 99999 88888")
        email = st.text_input("Email Address", value=user_email)
        skills = st.text_area("Skill Sets (comma separated)", placeholder="e.g. first-aid, rescue, cooking, translation, driving")
        
        col_lat, col_lng = st.columns(2)
        lat = col_lat.number_input("Latitude", value=user_lat, format="%.5f")
        lng = col_lng.number_input("Longitude", value=user_lng, format="%.5f")
        
        submit_btn = st.form_submit_button("Register for Dispatch", width="stretch")
        
    if submit_btn and name and phone:
        payload = {
            "name": name,
            "skill_set": skills,
            "phone": phone,
            "email": email,
            "location_lat": lat,
            "location_lng": lng
        }
        try:
            res = requests.post("http://localhost:8000/api/volunteers/register", json=payload, timeout=2)
            if res.status_code == 200:
                st.success("You are now registered as an active volunteer! Ready for dispatch operations.")
            else:
                if add_local_volunteer(payload):
                    st.success("Volunteer saved locally for dispatch matching.")
                else:
                    st.warning("The volunteer record could not be saved. Check the required fields and try again.")
        except requests.RequestException:
            if add_local_volunteer(payload):
                st.success("Backend is offline, so the volunteer was saved locally.")
            else:
                st.warning("Backend is offline and the volunteer could not be saved locally.")

with col_match:
    st.markdown("### Dispatch: Find and Match Volunteers")
    
    col_s_lat, col_s_lng = st.columns(2)
    s_lat = col_s_lat.number_input("Search Latitude Target", value=user_lat, format="%.5f", key="s_lat")
    s_lng = col_s_lng.number_input("Search Longitude Target", value=user_lng, format="%.5f", key="s_lng")
    
    skill_filter = st.text_input("Filter by required skill (e.g. first-aid, rescue, cooking):", placeholder="All available")
    
    if st.button("Search Matching Volunteers", width="stretch"):
        volunteers = []
        is_live = False
        try:
            skill_param = f"&required_skills={skill_filter}" if skill_filter else ""
            url = f"http://localhost:8000/api/volunteers/match?lat={s_lat}&lng={s_lng}{skill_param}&limit=6"
            res = requests.get(url, timeout=1)
            
            if res.status_code == 200:
                volunteers = res.json()
                is_live = True
            else:
                volunteers = local_volunteers(s_lat, s_lng, skill_filter, 6)
        except requests.RequestException:
            volunteers = local_volunteers(s_lat, s_lng, skill_filter, 6)

        if not is_live:
            st.info("Showing local volunteer records while the backend API is unavailable.")

        if not volunteers:
            st.info("No active volunteers found with these skills near the target location.")
        else:
            for v in volunteers:
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; color: #86efac;"> {v['name']}</h3>
                            <span class="indicator-tag indicator-low">{v['distance_km']} km away</span>
                        </div>
                        <p style="color: #cbd7e3; margin: 8px 0; font-size: 0.92rem;"> Skills: <b>{v['skill_set']}</b></p>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 0.88rem; color: #cbd7e3;">
                            <span> Call: <b>{v['phone']}</b></span>
                            <span> Email: {v['email'] or 'N/A'}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
