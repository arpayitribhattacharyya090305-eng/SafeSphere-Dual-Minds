import streamlit as st
import requests
from streamlit_folium import st_folium
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.auth_helper import AuthHelper
from frontend.map_utils import (
    add_disaster_zones,
    add_heatmap,
    add_place_markers,
    add_route,
    add_user_location,
    create_osm_map,
)

st.set_page_config(page_title="RescueAI Live Maps", layout="wide")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Emergency Live Maps</h1>", unsafe_allow_html=True)
st.markdown("Visualize active hazards, safety shelters, hospitals, and OSRM evacuation routes on OpenStreetMap.")

# Default Coordinates
user_lat = 19.0760
user_lng = 72.8777
user_loc = "Mumbai"

if AuthHelper.is_logged_in():
    p = st.session_state["user_profile"]
    user_lat = p.get("location_lat") or 19.0760
    user_lng = p.get("location_lng") or 72.8777
    user_loc = p.get("location_address") or "Mumbai"

# Sidebar controls
st.sidebar.markdown("### Map Settings")
show_shelters = st.sidebar.checkbox("Show Emergency Shelters", value=True)
show_hospitals = st.sidebar.checkbox("Show Hospitals", value=True)
show_incidents = st.sidebar.checkbox("Show Active Incidents", value=True)
route_dest = st.sidebar.selectbox("Evacuation Routing Target", ["None", "Closest Shelter"])

col_map, col_details = st.columns([3, 1])

# Fetch data from APIs
shelters = []
hospitals = []
incidents = []
route_info = None

try:
    if show_shelters:
        res = requests.get(f"http://localhost:8000/api/shelters/nearby?lat={user_lat}&lng={user_lng}&limit=10", timeout=5)
        if res.status_code == 200:
            shelters = res.json()

    if show_hospitals:
        res = requests.get(f"http://localhost:8000/api/hospitals/nearby?lat={user_lat}&lng={user_lng}&limit=10", timeout=5)
        if res.status_code == 200:
            hospitals = res.json()

    if show_incidents:
        res = requests.get("http://localhost:8000/api/incidents/list", timeout=5)
        if res.status_code == 200:
            incidents = res.json()
            
    # Calculate routing
    if route_dest == "Closest Shelter" and shelters:
        closest = shelters[0]
        # Query Chat API to generate routing steps and polyline
        payload = {
            "user_query": f"Draw route and navigate to shelter: {closest['name']}",
            "user_location": user_loc,
            "user_lat": user_lat,
            "user_lng": user_lng
        }
        res = requests.post("http://localhost:8000/api/chat/execute", json=payload, headers=AuthHelper.get_headers(), timeout=10)
        if res.status_code == 200:
            route_info = res.json().get("navigation_info")

except Exception as e:
    st.warning(f"Unable to read location feeds from backend API ({e})")

# Generate OpenStreetMap Folium map
m = create_osm_map(user_lat, user_lng, zoom_start=13)
add_user_location(m, user_lat, user_lng)

if show_shelters:
    add_place_markers(m, shelters, color="green", icon="home", tooltip="Emergency Shelter")

if show_hospitals:
    add_place_markers(m, hospitals, color="cadetblue", icon="plus-square", tooltip="Hospital Care")

if show_incidents:
    add_disaster_zones(m, incidents)
    add_heatmap(m, [[i["location_lat"], i["location_lng"]] for i in incidents])

if route_info and "polyline_coords" in route_info:
    add_route(m, route_info["polyline_coords"], color="#0f766e", tooltip="OSRM evacuation route")

# Render Map on Streamlit Page
with col_map:
    st_folium(m, height=600, width=900)

with col_details:
    st.markdown("### Navigation Instructions")
    if route_info:
        st.markdown(f"**Destination:** `{route_info['destination_name']}`")
        st.markdown(f"**Distance:** `{route_info['distance_km']} km`")
        st.markdown(f"**Time:** `{route_info['duration_min']} mins`")
        st.markdown("---")
        st.markdown("**OSRM Route Steps:**")
        for step in route_info["steps"]:
            st.markdown(f"- {step}")
    else:
        st.info("Select 'Closest Shelter' on the sidebar configuration panel to map and load direct evacuation routes.")
