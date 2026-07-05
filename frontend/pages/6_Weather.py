import streamlit as st
import requests
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.local_fallbacks import local_weather
from frontend.profile_state import get_profile

st.set_page_config(page_title="RescueAI Weather alerts", layout="wide", initial_sidebar_state="expanded")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Live Weather Forecasts & Warnings</h1>", unsafe_allow_html=True)
st.markdown("Assess local weather warnings and evaluate meteorological impacts on rescue craft and evacuation logistics.")

profile = get_profile()
user_lat = profile.get("location_lat") or 19.0760
user_lng = profile.get("location_lng") or 72.8777

st.sidebar.markdown("### Location Coordinates")
lat_in = st.sidebar.number_input("Latitude", value=user_lat, format="%.5f")
lng_in = st.sidebar.number_input("Longitude", value=user_lng, format="%.5f")

try:
    res = requests.get(f"http://localhost:8000/api/weather/alerts?lat={lat_in}&lng={lng_in}", timeout=3)
    data = res.json() if res.status_code == 200 else local_weather(lat_in, lng_in)
except requests.RequestException:
    data = local_weather(lat_in, lng_in)

if not data.get("is_live") and any(data.get(key) is None for key in ("temp", "humidity", "wind_speed")):
    data = local_weather(lat_in, lng_in)

if not data.get("is_live"):
    st.info("Showing local weather condition estimates and warning bulletins while live weather is unavailable.")

# Grid layout for primary stats
col1, col2, col3, col4 = st.columns(4)
temp = data.get("temp") if data.get("temp") is not None else "--"
humidity = data.get("humidity") if data.get("humidity") is not None else "--"
wind_speed = data.get("wind_speed") if data.get("wind_speed") is not None else "--"
temp_unit = "C" if temp != "--" and temp is not None else ""
humidity_unit = "%" if humidity != "--" and humidity is not None else ""
wind_unit = " m/s" if wind_speed != "--" and wind_speed is not None else ""
with col1:
    st.markdown(f"<div class='glass-card' style='text-align: center;'><h5 style='margin:0;color:#9fb0c3;'>Temp</h5><h2 style='margin:10px 0 0 0;'>{temp}{temp_unit}</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='glass-card' style='text-align: center;'><h5 style='margin:0;color:#9fb0c3;'>Humidity</h5><h2 style='margin:10px 0 0 0;'>{humidity}{humidity_unit}</h2></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='glass-card' style='text-align: center;'><h5 style='margin:0;color:#9fb0c3;'>Wind Speed</h5><h2 style='margin:10px 0 0 0;'>{wind_speed}{wind_unit}</h2></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='glass-card' style='text-align: center;'><h5 style='margin:0;color:#9fb0c3;'>Description</h5><h2 style='margin:10px 0 0 0; font-size:1.4rem; padding-top:5px;'>{data.get('description', 'Unavailable')}</h2></div>", unsafe_allow_html=True)

st.markdown("### Active Warning Bulletins")
alerts = data.get("alerts", [])
if not alerts:
    st.success("No active extreme weather alerts (cyclones, monsoons, heatwaves) for these coordinates.")
else:
    for alert in alerts:
        sev_color = "#f87171" if alert["severity"].lower() in ["high", "critical", "extreme"] else "#fbbf24"
        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 5px solid {sev_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin:0; color:#f8fafc;"> {alert['event']}</h4>
                    <span class="indicator-tag" style="background-color: rgba(239, 68, 68, 0.1); color: {sev_color}; border: 1px solid {sev_color};">{alert['severity']}</span>
                </div>
                <p style="margin: 10px 0; color:#cbd7e3;">{alert['description']}</p>
                <small style="color:#8fa1b6;">Issued by: <b>{alert['sender']}</b></small>
            </div>
            """,
            unsafe_allow_html=True
        )
