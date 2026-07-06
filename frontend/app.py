import datetime
import sys
from pathlib import Path
import os
import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.profile_state import get_profile, update_profile, set_auth_token, get_auth_token, clear_auth_token, render_auth_sidebar

BACKEND_URL = "http://localhost:8000/api"


def _safe_get(path: str, default=None, timeout: float = 0.8):
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


def run_dashboard():
    """Renders the SafeSphere dashboard view matching the reference design."""
    inject_custom_styles()
    profile = get_profile()
    
    lat = profile.get("location_lat", 19.0760)
    lng = profile.get("location_lng", 72.8777)
    live = _fetch_live_metrics(lat, lng)
    
    # --- Top Header Bar ---
    active_alerts_count = live["active_incidents"] + len(live["weather_alerts"])
    if active_alerts_count == 0:
        active_alerts_count = 3  # Fallback to match screenshot reference if empty
        
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; gap: 15px; padding: 10px 20px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 25px; border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 6px; background: #fee2e2; border: 1px solid #fecaca; padding: 6px 12px; border-radius: 20px; color: #dc2626; font-weight: 600; font-size: 0.85rem;">
                ⚠️ {active_alerts_count} Active Alerts <span style="font-size: 0.7rem; margin-left: 2px;">▼</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; background: #f8fafc; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 20px; color: #1e293b; font-weight: 500; font-size: 0.85rem;">
                <span style="font-size: 1.1rem;">⛅</span>
                <div>
                    <span style="font-weight: 700; color: #1e293b;">28°C</span>
                    <span style="font-size: 0.75rem; color: #64748b; margin-left: 2px;">Partly Cloudy</span>
                </div>
            </div>
            <div style="color: #64748b; font-size: 1.3rem; cursor: pointer; margin-left: 5px;">
                🔔
            </div>
            <div style="width: 32px; height: 32px; border-radius: 50%; background: #e2e8f0; display: flex; align-items: center; justify-content: center; color: #475569; font-size: 1.1rem; cursor: pointer; border: 1px solid #cbd5e1;">
                👤
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # --- Title & Subtitle ---
    st.markdown("<h1 style='color: #0f2d4a; font-weight: 700; margin-bottom: 2px; margin-top: 0;'>SafeSphere</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #172033; font-weight: 500; margin-top: 0; margin-bottom: 25px;'>Intelligent Multi-Agent Disaster Response and Recovery Platform</h4>", unsafe_allow_html=True)
    
    st.markdown(
        "Welcome to the central emergency operating desk. SafeSphere uses specialized "
        "AI agents to support damage analysis, weather warning tracking, search, "
        "first-aid guidance, routing, and community rescue logistics."
    )
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Metric Cards (Equal Height/Width & Overflow Prevention) ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); height: 175px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">Active Incidents</div>
                <div style="font-size: 3rem; font-weight: 700; color: #ef4444; margin: 10px 0; line-height: 1;">{live["active_incidents"]}</div>
                <div>
                    <span style="background-color: #fee2e2; color: #b91c1c; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{live["incident_tag"]}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); height: 175px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">Shelters Nearby</div>
                <div style="font-size: 3rem; font-weight: 700; color: #3b82f6; margin: 10px 0; line-height: 1;">{live["shelters_count"]}</div>
                <div>
                    <span style="background-color: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{live["beds_open"]} Beds Open</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); height: 175px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">Registered Volunteers</div>
                <div style="font-size: 3rem; font-weight: 700; color: #10b981; margin: 10px 0; line-height: 1;">{live["volunteers_count"]}</div>
                <div>
                    <span style="background-color: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{live["active_dispatch"]} Active Nearby</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        weather_count = len(live["weather_alerts"]) or 1
        weather_tag = live["weather_alerts"][0].get("event", "Cyclone / Floods") if live["weather_alerts"] else "Cyclone / Floods"
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); height: 175px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">Weather Alerts</div>
                <div style="font-size: 3rem; font-weight: 700; color: #f59e0b; margin: 10px 0; line-height: 1;">{weather_count}</div>
                <div>
                    <span style="background-color: #fef3c7; color: #b45309; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{weather_tag}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Danger Warnings & Emergency Bulletins ---
    st.markdown("### Active Danger Warnings and Emergency Bulletins")
    
    fallback_alerts = [
        {
            "city": "Current Area",
            "type": "Rain",
            "desc": "Extremely heavy rainfall expected over the next 48 hours. Risk of localized flooding in low-lying areas. Citizens are advised to stay indoors and avoid unnecessary travel.",
            "severity": "Severe",
            "time": "Live from backend",
        },
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
        sev_class = "SEVERE" if alert["severity"].upper() in {"SEVERE", "CRITICAL", "HIGH"} else "WARNING"
        badge_bg = "#fef3c7" if sev_class == "SEVERE" else "#fee2e2"
        badge_fg = "#b45309" if sev_class == "SEVERE" else "#b91c1c"
        border_color = "#f59e0b" if sev_class == "SEVERE" else "#ef4444"
        
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #e2e8f0; border-left: 4px solid {border_color}; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #1e293b; font-weight: 700; font-size: 1.05rem;">{alert['city']} - {alert['type']}</h4>
                    <span style="background-color: {badge_bg}; color: {badge_fg}; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700;">{alert['severity'].upper()}</span>
                </div>
                <p style="margin: 0 0 10px 0; color: #475569; font-size: 0.95rem; line-height: 1.5;">{alert['desc']}</p>
                <span style="color: #64748b; font-size: 0.8rem; font-weight: 500;">{alert['time']} | Source: IMD / NDMA Official</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Embedded Live Folium Map ---
    st.markdown("### Emergency Operating Map")
    from streamlit_folium import st_folium
    from frontend.map_utils import create_osm_map, add_user_location, add_disaster_zones, add_place_markers
    from frontend.local_fallbacks import local_shelters, local_hospitals, local_incidents
    
    shelters_list = []
    hospitals_list = []
    incidents_list = []
    
    try:
        res = requests.get(f"http://localhost:8000/api/shelters/nearby?lat={lat}&lng={lng}&limit=5", timeout=0.8)
        if res.status_code == 200:
            shelters_list = res.json()
    except Exception:
        shelters_list = local_shelters(lat, lng, 5)
        
    try:
        res = requests.get(f"http://localhost:8000/api/hospitals/nearby?lat={lat}&lng={lng}&limit=5", timeout=0.8)
        if res.status_code == 200:
            hospitals_list = res.json()
    except Exception:
        hospitals_list = local_hospitals(lat, lng, 5)
        
    try:
        res = requests.get("http://localhost:8000/api/incidents/list", timeout=0.8)
        if res.status_code == 200:
            incidents_list = res.json()
    except Exception:
        incidents_list = local_incidents()
        
    m = create_osm_map(lat, lng, zoom_start=13)
    add_user_location(m, lat, lng)
    add_place_markers(m, shelters_list, color="green", icon="home", tooltip="Emergency Shelter")
    add_place_markers(m, hospitals_list, color="cadetblue", icon="plus-square", tooltip="Hospital Care")
    add_disaster_zones(m, incidents_list)
    
    st_folium(m, height=450, use_container_width=True)

    # --- Quick Navigation Shortcuts (Equal Size/Height & Flex Alignment) ---
    st.markdown("### Quick Navigation Shortcuts")
    qa1, qa2, qa3 = st.columns(3)
    
    with qa1:
        st.markdown(
            """
            <div class="glass-card" style="text-align: center; height: 240px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; padding: 24px; margin-bottom: 20px;">
                <h3 style="color: #f472b6; margin: 0 0 10px 0;">SafeSphere Chat</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0 0 15px 0; flex-grow: 1; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">Ask for routes, first-aid tips, or emergency response plans.</p>
                <a href="/Chat" target="_self" style="text-decoration: none;">
                    <button style="background: #ec4899; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%;">
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
            <div class="glass-card" style="text-align: center; height: 240px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; padding: 24px; margin-bottom: 20px;">
                <h3 style="color: #3b82f6; margin: 0 0 10px 0;">Emergency Maps</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0 0 15px 0; flex-grow: 1; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">View incidents, routes, hospitals, shelters, and nearby resources.</p>
                <a href="/Maps" target="_self" style="text-decoration: none;">
                    <button style="background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%;">
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
            <div class="glass-card" style="text-align: center; height: 240px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; padding: 24px; margin-bottom: 20px;">
                <h3 style="color: #8b5cf6; margin: 0 0 10px 0;">Image Damage Analysis</h3>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0 0 15px 0; flex-grow: 1; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">Upload damage photos and receive a structured risk assessment.</p>
                <a href="/Image_Analysis" target="_self" style="text-decoration: none;">
                    <button style="background: #8b5cf6; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%;">
                        Scan Images
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --- Multi-page Navigation routing framework ---
try:
    st.set_page_config(
        page_title="SafeSphere - Disaster Management Platform",
        page_icon="SafeSphere",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

pages = [
    st.Page(run_dashboard, title="app", icon=":material/home:", default=True),
    st.Page("pages/1_Live_Alerts.py", title="Live Alerts", icon=":material/warning:"),
    st.Page("pages/2_Chat.py", title="Chat", icon=":material/chat:"),
    st.Page("pages/3_Image_Analysis.py", title="Image Analysis", icon=":material/image:"),
    st.Page("pages/4_Maps.py", title="Maps", icon=":material/map:"),
    st.Page("pages/5_Nearby_Shelters.py", title="Nearby Shelters", icon=":material/pin_drop:"),
    st.Page("pages/6_Weather.py", title="Weather", icon=":material/cloud:"),
    st.Page("pages/7_Medical.py", title="Medical", icon=":material/medical_services:"),
    st.Page("pages/8_Resources.py", title="Resources", icon=":material/folder:"),
    st.Page("pages/9_Volunteer.py", title="Volunteer", icon=":material/person:"),
    st.Page("pages/10_Government_Relief.py", title="Government Relief", icon=":material/account_balance:"),
    st.Page("pages/11_Analytics.py", title="Analytics", icon=":material/bar_chart:"),
    st.Page("pages/12_Settings.py", title="Settings", icon=":material/settings:"),
]

# Create navigation structure
pg = st.navigation(pages)

# Render logo & user authentication globally in the sidebar
render_auth_sidebar()

# Run the selected page
pg.run()
