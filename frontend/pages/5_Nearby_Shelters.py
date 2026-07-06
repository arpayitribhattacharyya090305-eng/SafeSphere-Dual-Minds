import streamlit as st
import requests
from pathlib import Path
import sys
from textwrap import dedent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.local_fallbacks import local_hospitals, local_shelters
from frontend.profile_state import get_profile

st.set_page_config(page_title="SafeSphere Shelters", layout="wide", initial_sidebar_state="expanded")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Nearby Emergency Shelters & Hospitals</h1>", unsafe_allow_html=True)
st.markdown("Locate safe relief camps, community centers, and operational hospitals near your location.")

profile = get_profile()
user_lat = profile.get("location_lat") or 19.0760
user_lng = profile.get("location_lng") or 72.8777

# Sidebar search customization
st.sidebar.markdown("### Location Coordinates")
lat_in = st.sidebar.number_input("Latitude", value=user_lat, format="%.5f")
lng_in = st.sidebar.number_input("Longitude", value=user_lng, format="%.5f")

shelter_tab, hospital_tab = st.tabs([" Emergency Shelters", " Hospitals & Clinics"])


def _api_get(url: str, fallback_fn):
    try:
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            return res.json(), True
    except requests.RequestException:
        pass
    return fallback_fn(), False


def _show_local_notice():
    st.info("Showing local emergency database results while the live API is unavailable.")

with shelter_tab:
    st.markdown("### Safe Relief Centers")
    shelters, is_live = _api_get(
        f"http://localhost:8000/api/shelters/nearby?lat={lat_in}&lng={lng_in}&limit=6",
        lambda: local_shelters(lat_in, lng_in, 6),
    )
    if not is_live:
        _show_local_notice()
    if not shelters:
        st.info("No shelters found in database matching these coordinates.")
    else:
        for s in shelters:
            occ_pct = (s["total_beds"] - s["available_beds"]) / s["total_beds"] if s["total_beds"] > 0 else 1.0

            st.markdown(
                dedent(f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; color: #38bdf8;">{s['name']}</h3>
                        <span class="indicator-tag indicator-low">{s['distance_km']} km away</span>
                    </div>
                    <p style="color: #cbd7e3; margin: 8px 0; font-size: 0.92rem;">{s['address']}</p>
                    <p style="color: #9fb0c3; margin: 4px 0; font-size: 0.88rem;">Contact: <b>{s['contact_number'] or 'N/A'}</b></p>
                    <p style="font-size: 0.85rem; color: #9fb0c3; margin: 12px 0 0;">
                        Occupancy Capacity ({s['total_beds'] - s['available_beds']}/{s['total_beds']} beds occupied):
                    </p>
                </div>
                """),
                unsafe_allow_html=True
            )
            st.progress(occ_pct)

            food_tag = "Food" if s["has_food"] else "No Food"
            water_tag = "Water" if s["has_water"] else "No Water"
            power_tag = "Power Backup" if s["has_power"] else "No Power"
            med_tag = "First-Aid" if s["has_medical"] else "No Medical"

            st.markdown(
                dedent(f"""
                <div style="display: flex; gap: 15px; margin-top: -10px; margin-bottom: 25px; font-size: 0.85rem; font-weight: 600;">
                    <span>{food_tag}</span>
                    <span>{water_tag}</span>
                    <span>{power_tag}</span>
                    <span>{med_tag}</span>
                </div>
                """),
                unsafe_allow_html=True
            )

with hospital_tab:
    st.markdown("### Operational Medical Care Centers")
    hospitals, is_live = _api_get(
        f"http://localhost:8000/api/hospitals/nearby?lat={lat_in}&lng={lng_in}&limit=6",
        lambda: local_hospitals(lat_in, lng_in, 6),
    )
    if not is_live:
        _show_local_notice()
    if not hospitals:
        st.info("No hospitals found in database matching these coordinates.")
    else:
        for h in hospitals:
            st.markdown(
                dedent(f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; color: #60a5fa;">{h['name']}</h3>
                        <span class="indicator-tag indicator-low">{h['distance_km']} km away</span>
                    </div>
                    <p style="color: #cbd7e3; margin: 8px 0; font-size: 0.92rem;">{h['address']}</p>
                    <p style="color: #9fb0c3; margin: 4px 0; font-size: 0.88rem;">Emergency Helpline: <b>{h['contact_number'] or '108'}</b></p>
                    <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 0.85rem; font-weight: 500; color: #cbd7e3;">
                        <span>Beds Available: <b>{h['available_beds']} / {h['total_beds']}</b></span>
                        <span>24/7 Trauma Services: <b>{'YES' if h['emergency_services'] else 'NO'}</b></span>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )
