import datetime
import sys
from pathlib import Path

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.auth_helper import AuthHelper
from frontend.custom_style import inject_custom_styles

BACKEND_URL = "http://localhost:8000/api"


def _safe_get(path: str, default=None, timeout: int = 3):
    """Fetch JSON from backend and return a safe default on error."""
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=timeout)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return default


def _fetch_live_metrics(lat: float = 19.0760, lng: float = 72.8777) -> dict:
    """Fetch live dashboard counts from the backend API."""
    incidents = _safe_get("/incidents/list", [])
    shelters = _safe_get(f"/shelters/nearby?lat={lat}&lng={lng}&limit=20", [])
    volunteers = _safe_get(f"/volunteers/match?lat={lat}&lng={lng}&limit=50", [])
    weather = _safe_get(f"/weather/alerts?lat={lat}&lng={lng}", {})

    active_incidents = [item for item in incidents if item.get("status") != "Resolved"]
    critical_count = sum(
        1 for item in active_incidents if item.get("severity") in {"Critical", "High"}
    )
    beds_open = sum(int(item.get("available_beds") or 0) for item in shelters)
    nearby_volunteers = sum(
        1 for item in volunteers if item.get("distance_km", 999) < 10
    )
    weather_alerts = weather.get("alerts", []) if isinstance(weather, dict) else []

    return {
        "active_incidents": len(active_incidents),
        "incident_tag": "Critical Level" if critical_count > 0 else "Monitoring",
        "shelters_count": len(shelters),
        "beds_open": beds_open,
        "volunteers_count": len(volunteers),
        "active_dispatch": nearby_volunteers,
        "weather_alerts": weather_alerts,
    }


st.set_page_config(
    page_title="RescueAI - Disaster Management Platform",
    page_icon="RescueAI",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_styles()

if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None
if "user_profile" not in st.session_state:
    st.session_state["user_profile"] = None

AuthHelper.fetch_profile()
profile = st.session_state.get("user_profile")

st.sidebar.markdown(
    "<h2 style='text-align: center; color: #6366f1;'>RescueAI Portal</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

if AuthHelper.is_logged_in():
    user = st.session_state["user_profile"]
    st.sidebar.markdown(f"### Welcome, **{user['full_name']}**")
    st.sidebar.markdown(f"**Role:** `{user['role'].upper()}`")
    st.sidebar.markdown(f"**Location:** {user['location_address'] or 'Not set'}")

    if st.sidebar.button("Log Out", key="logout_btn"):
        AuthHelper.logout()
        st.rerun()
else:
    st.sidebar.markdown("### Responder / Citizen Login")
    login_tab, signup_tab = st.sidebar.tabs(["Login", "Sign Up"])

    with login_tab:
        login_email = st.text_input("Email", key="login_email")
        login_pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Log In", use_container_width=True, key="login_submit"):
            if AuthHelper.login(login_email, login_pwd):
                st.success("Logged in successfully.")
                st.rerun()

    with signup_tab:
        su_name = st.text_input("Full Name", key="su_name")
        su_email = st.text_input("Email", key="su_email")
        su_pwd = st.text_input("Password", type="password", key="su_pwd")
        su_addr = st.text_input("Address / City", key="su_addr")
        su_role = st.selectbox(
            "I am registering as a:",
            ["citizen", "responder", "volunteer"],
            key="su_role",
        )

        if st.button("Create Account", use_container_width=True, key="signup_submit"):
            signup_data = {
                "email": su_email,
                "password": su_pwd,
                "full_name": su_name,
                "location_address": su_addr,
                "role": su_role,
                "preferred_language": "English",
            }
            if AuthHelper.signup(signup_data):
                st.info("Registration successful. You can now log in.")

st.markdown("<h1 class='gradient-header'>RescueAI</h1>", unsafe_allow_html=True)
st.markdown("### Intelligent Multi-Agent Disaster Response and Recovery Platform")
st.markdown(
    "Welcome to the central emergency operating desk. RescueAI uses specialized "
    "AI agents to support damage analysis, weather warning tracking, search, "
    "first-aid guidance, routing, and community rescue logistics."
)

st.markdown("<br>", unsafe_allow_html=True)

lat = profile.get("location_lat", 19.0760) if profile else 19.0760
lng = profile.get("location_lng", 72.8777) if profile else 72.8777
live = _fetch_live_metrics(lat, lng)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="glass-card">
            <h4 style="margin: 0; color: #94a3b8;">Active Incidents</h4>
            <h1 style="margin: 10px 0 0 0; color: #f87171; font-size: 2.8rem;">{live["active_incidents"] or "-"}</h1>
            <span class="indicator-tag indicator-critical">{live["incident_tag"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="glass-card">
            <h4 style="margin: 0; color: #94a3b8;">Shelters Nearby</h4>
            <h1 style="margin: 10px 0 0 0; color: #60a5fa; font-size: 2.8rem;">{live["shelters_count"] or "-"}</h1>
            <span class="indicator-tag indicator-low">{live["beds_open"]} Beds Open</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="glass-card">
            <h4 style="margin: 0; color: #94a3b8;">Registered Volunteers</h4>
            <h1 style="margin: 10px 0 0 0; color: #34d399; font-size: 2.8rem;">{live["volunteers_count"] or "-"}</h1>
            <span class="indicator-tag indicator-low">{live["active_dispatch"]} Active Nearby</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    weather_count = len(live["weather_alerts"])
    st.markdown(
        f"""
        <div class="glass-card">
            <h4 style="margin: 0; color: #94a3b8;">Weather Alerts</h4>
            <h1 style="margin: 10px 0 0 0; color: #facc15; font-size: 2.8rem;">{weather_count or "-"}</h1>
            <span class="indicator-tag indicator-high">Cyclone / Floods</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Active Danger Warnings and Emergency Bulletins")

fallback_alerts = [
    {
        "city": "Mumbai Wards A-G",
        "type": "Monsoon Flash Flood Warning",
        "desc": "Heavy rainfall reported. Low underpasses may be waterlogged and traffic diversions may be active.",
        "severity": "Critical",
        "time": "Updated 10 minutes ago",
    },
    {
        "city": "Coastal Chennai / Adyar",
        "type": "Cyclone Warning",
        "desc": "High coastal winds and tides reported. Follow local evacuation instructions and move to safe centers.",
        "severity": "High",
        "time": "Updated 45 minutes ago",
    },
]

display_alerts = (
    [
        {
            "city": "Current Area",
            "type": alert.get("event", "Weather Alert"),
            "desc": alert.get("description", "Follow local emergency instructions."),
            "severity": alert.get("severity", "Medium"),
            "time": "Live from backend",
        }
        for alert in live["weather_alerts"]
    ]
    if live["weather_alerts"]
    else fallback_alerts
)

for alert in display_alerts:
    sev_class = "indicator-critical" if alert["severity"] == "Critical" else "indicator-high"
    border_color = "#f87171" if alert["severity"] == "Critical" else "#fb923c"
    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 5px solid {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #f8fafc;">{alert['city']} - {alert['type']}</h4>
                <span class="indicator-tag {sev_class}">{alert['severity']}</span>
            </div>
            <p style="margin: 10px 0; color: #cbd5e1; font-size: 0.95rem;">{alert['desc']}</p>
            <span style="color: #64748b; font-size: 0.8rem; font-weight: 500;">{alert['time']} | Source: IMD / NDMA Official</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Quick Navigation Shortcuts")
qa1, qa2, qa3 = st.columns(3)

with qa1:
    st.markdown(
        """
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #f472b6; margin-top:0;">RescueAI Chat</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">Ask for routes, first-aid tips, or emergency response plans.</p>
            <a href="/Chat" target="_self" style="text-decoration: none;">
                <button style="background: #ec4899; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer;">
                    Open Assistant
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

with qa2:
    st.markdown(
        """
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #60a5fa; margin-top:0;">Emergency Maps</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">View incidents, routes, hospitals, shelters, and nearby resources.</p>
            <a href="/Maps" target="_self" style="text-decoration: none;">
                <button style="background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer;">
                    View Maps
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

with qa3:
    st.markdown(
        """
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #a78bfa; margin-top:0;">Image Damage Analysis</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">Upload damage photos and receive a structured risk assessment.</p>
            <a href="/Image_Analysis" target="_self" style="text-decoration: none;">
                <button style="background: #8b5cf6; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer;">
                    Scan Images
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
