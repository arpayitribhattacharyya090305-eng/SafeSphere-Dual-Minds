import streamlit as st
import requests
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles
from frontend.local_fallbacks import local_government_schemes
from frontend.profile_state import render_auth_sidebar

BACKEND_URL = "http://localhost:8000/api"

st.set_page_config(page_title="SafeSphere Relief Schemes", layout="wide", initial_sidebar_state="expanded")
inject_custom_styles()
render_auth_sidebar()

st.markdown("<h1 class='gradient-header'>Government Relief & Compensation Schemes</h1>", unsafe_allow_html=True)
st.markdown("Access NDMA relief, ex-gratia compensations, and housing subsidies with eligibility guidelines and required documents.")

st.sidebar.markdown("### Filter Category")
category = st.sidebar.selectbox("Select Category", ["All", "Compensation", "Medical Aid", "Housing", "Relief Fund"])

schemes = []
is_live = False
try:
    params = {}
    if category != "All":
        params["category"] = category
    res = requests.get(f"{BACKEND_URL}/government/schemes", params=params, timeout=1)
    if res.status_code == 200:
        schemes = res.json()
        is_live = True
    else:
        schemes = local_government_schemes(category)
except requests.RequestException:
    schemes = local_government_schemes(category)

if not is_live:
    st.info("Showing local relief scheme records while the backend API is unavailable.")

if not schemes:
    st.info("No active government schemes found matching this category.")
else:
    for s in schemes:
        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 5px solid #a855f7;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #a855f7;"> {s['title']}</h3>
                    <span class="indicator-tag indicator-high">{s['category']}</span>
                </div>
                <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5;"><b>Description:</b> {s['description']}</p>
                <p style="color: #facc15; font-size: 0.92rem;"> <b>Benefit Amount:</b> {s['benefit_amount']}</p>
                <p style="color: #cbd5e1; font-size: 0.9rem;"> <b>Eligibility Criteria:</b> {s['eligibility_criteria']}</p>
                <p style="color: #94a3b8; font-size: 0.88rem;"> <b>Helpline Support:</b> {s['contact_helpline']}</p>
                <br>
                <div style="background: rgba(255, 255, 255, 0.03); border-radius: 8px; padding: 12px; border: 1px dashed rgba(255,255,255,0.1);">
                    <span style="font-weight: 600; color: #f8fafc; font-size: 0.85rem;"> REQUIRED DOCUMENTS TO CLAIM:</span>
                    <ul style="margin: 8px 0 0 0; padding-left: 20px; font-size: 0.85rem; color: #cbd5e1;">
            """,
            unsafe_allow_html=True
        )
        for doc in s.get("documents_required", []):
            st.markdown(f"<li style='color:#cbd5e1; font-size:0.85rem;'>{doc}</li>", unsafe_allow_html=True)
        st.markdown(
            """
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
