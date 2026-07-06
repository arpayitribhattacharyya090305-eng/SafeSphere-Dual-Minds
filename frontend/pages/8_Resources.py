import streamlit as st
import requests
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.local_fallbacks import local_resources
from frontend.profile_state import get_profile, render_auth_sidebar

try:
    st.set_page_config(page_title="SafeSphere Resources", layout="wide", initial_sidebar_state="expanded")
except Exception:
    pass
inject_custom_styles()
# render_auth_sidebar()  # Handled globally in app.py

st.markdown("<h1 class='gradient-header'>Emergency Inventory & Resource Hubs</h1>", unsafe_allow_html=True)
st.markdown("Locate and verify stock levels of drinking water, rations, medicines, generator fuel, and battery hubs.")

profile = get_profile()
user_lat = profile.get("location_lat") or 19.0760
user_lng = profile.get("location_lng") or 72.8777

st.sidebar.markdown("### Search Filter")
category = st.sidebar.selectbox("Filter Category", ["All", "Food", "Water", "Medicine", "Fuel", "Power"])
limit = st.sidebar.slider("Radius Hub Limits", min_value=1, max_value=10, value=5)

cat_param = f"&category={category}" if category != "All" else ""
url = f"http://localhost:8000/api/resources/nearby?lat={user_lat}&lng={user_lng}{cat_param}&limit={limit}"
try:
    res = requests.get(url, timeout=3)
    resources = res.json() if res.status_code == 200 else local_resources(user_lat, user_lng, category, limit)
    is_live = res.status_code == 200
except requests.RequestException:
    resources = local_resources(user_lat, user_lng, category, limit)
    is_live = False

if not is_live:
    st.info("Showing local resource hub records while the live API is unavailable.")

if not resources:
    st.info("No resource depots found matching this category in proximity.")
else:
    for r in resources:
        status_color = "#86efac" if r["status"] == "Available" else ("#fbbf24" if r["status"] == "Low" else "#f87171")
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #60a5fa;"> {r['name']}</h3>
                    <span class="indicator-tag" style="background-color: rgba(167, 139, 250, 0.1); color: {status_color}; border: 1px solid {status_color};">{r['status']}</span>
                </div>
                <p style="color: #cbd7e3; margin: 8px 0; font-size: 0.92rem;"> Depot: {r['address'] or 'N/A'}</p>
                <p style="color: #cbd7e3; margin: 4px 0; font-size: 0.88rem;"> Category: <b>{r['category']}</b> | Current Supply: <b>{r['quantity']} {r['unit']}</b></p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 0.85rem; color: #9fb0c3;">
                    <span> Dispatch Desk: {r['contact_number'] or 'N/A'}</span>
                    <span style="font-weight: 600; color: #f8fafc;"> Proximity: {r['distance_km']} km</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
