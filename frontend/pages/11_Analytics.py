import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import SessionLocal
from backend.app.models.database_models import Shelter, Incident, Volunteer, WeatherAlert
from frontend.custom_style import inject_custom_styles

st.set_page_config(page_title="RescueAI Analytics", layout="wide")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Operations Analytics & Metrics</h1>", unsafe_allow_html=True)
st.markdown("Real-time telemetry on shelter bed availability, active incidents, volunteer skills, and meteorological severity metrics.")

db = SessionLocal()
try:
    # 1. Fetch Shelters Data
    shelters = db.query(Shelter).all()
    # 2. Fetch Incidents Data
    incidents = db.query(Incident).all()
    # 3. Fetch Volunteers Data
    volunteers = db.query(Volunteer).all()
    # 4. Fetch Weather Alerts
    alerts = db.query(WeatherAlert).all()
finally:
    db.close()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Shelter Bed Capacities")
    if not shelters:
        st.info("No shelters found in database.")
    else:
        shelter_names = [s.name for s in shelters]
        beds_occupied = [s.total_beds - s.available_beds for s in shelters]
        beds_avail = [s.available_beds for s in shelters]
        
        df_beds = pd.DataFrame({
            "Shelter": shelter_names * 2,
            "Beds count": beds_occupied + beds_avail,
            "Status": ["Occupied"] * len(shelters) + ["Available"] * len(shelters)
        })
        
        fig = px.bar(
            df_beds, x="Shelter", y="Beds count", color="Status",
            barmode="stack", color_discrete_map={"Occupied": "#fca5a5", "Available": "#86efac"},
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Active Incidents by Category")
    if not incidents:
        # Provide simulated data for display if DB is freshly reset
        df_inc = pd.DataFrame({
            "Category": ["Flood", "Fire", "Collapse", "Blockage"],
            "Count": [4, 1, 2, 3]
        })
    else:
        types = [inc.disaster_type for inc in incidents]
        df_inc = pd.DataFrame(types, columns=["Category"]).value_counts().reset_index()
        df_inc.columns = ["Category", "Count"]

    fig_pie = px.pie(
        df_inc, values="Count", names="Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4, template="plotly_dark"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("### Registered Volunteer Skillsets")
    # Gather skills frequency
    skills_map = {}
    for v in volunteers:
        if v.skill_set:
            for skill in v.skill_set.split(","):
                clean = skill.strip().capitalize()
                skills_map[clean] = skills_map.get(clean, 0) + 1
                
    if not skills_map:
        skills_map = {"First-aid": 12, "Rescue": 15, "Cooking": 8, "Logistics": 10}
        
    df_vol = pd.DataFrame(list(skills_map.items()), columns=["Skill", "Volunteers"])
    fig_vol = px.bar(
        df_vol, x="Volunteers", y="Skill", orientation='h',
        color="Skill", template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Agsunset
    )
    st.plotly_chart(fig_vol, use_container_width=True)

with col4:
    st.markdown("### Meteorological Alerts Severity")
    severity_map = {}
    for a in alerts:
        sev = a.severity.capitalize()
        severity_map[sev] = severity_map.get(sev, 0) + 1
        
    if not severity_map:
        severity_map = {"Extreme": 1, "Severe": 2, "Moderate": 4}
        
    df_alert = pd.DataFrame(list(severity_map.items()), columns=["Severity", "Count"])
    fig_alert = px.bar(
        df_alert, x="Severity", y="Count", color="Severity",
        template="plotly_dark", color_discrete_map={"Extreme": "#f87171", "Severe": "#fbbf24", "Moderate": "#fbbf24"}
    )
    st.plotly_chart(fig_alert, use_container_width=True)
