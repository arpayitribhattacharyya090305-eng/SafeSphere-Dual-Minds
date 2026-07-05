import streamlit as st
import requests
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.custom_style import inject_custom_styles

BACKEND_URL = "http://localhost:8000/api"

st.set_page_config(page_title="RescueAI Medical Advisor", layout="wide")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Medical First Aid Advisor (RAG)</h1>", unsafe_allow_html=True)
st.markdown("Search critical medical and trauma guidelines sourced from WHO, Indian NDMA, and Red Cross safety manuals.")

# Search bar
search_query = st.text_input(
    "Search first aid guidelines (e.g. how to perform CPR, snakebite treatment, burn care):",
    key="med_search_input"
)

# Quick tags
st.markdown("**Quick Shortcuts:**")
tag_cols = st.columns(6)
tags = ["CPR Guidelines", "Snake Bite Care", "Burn First Aid", "Fracture Splints", "Ingestion Poisoning", "Panic Relief"]

selected_tag = None
for i, tag in enumerate(tags):
    with tag_cols[i]:
        if st.button(tag, use_container_width=True, key=f"tag_{i}"):
            selected_tag = tag

# Override query if tag clicked
effective_query = selected_tag or search_query

if effective_query:
    st.markdown(f"### Search results for *'{effective_query}'*")

    with st.spinner("Retrieving matched safety sheets from guidelines database..."):
        try:
            res = requests.post(
                f"{BACKEND_URL}/medical/query",
                json={"query": effective_query, "limit": 2},
                timeout=8
            )
            if res.status_code == 200:
                results = res.json()
            else:
                st.error(f"Backend returned HTTP {res.status_code}. Is the backend running?")
                results = []
        except Exception as e:
            st.error(f"Cannot connect to backend API ({e}). Ensure the backend is running on port 8000.")
            results = []

        if not results:
            st.info("No explicit guidelines found. Try searching for terms like 'cpr', 'burn', 'snake', or 'fracture'.")
        else:
            for doc in results:
                st.markdown(
                    f"""
                    <div class="glass-card" style="border-left: 5px solid #6366f1;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h3 style="margin: 0; color: #a855f7;"> {doc['title']}</h3>
                            <span class="indicator-tag indicator-medium">{doc['category']} Guideline</span>
                        </div>
                        <p style="white-space: pre-line; color: #cbd5e1; line-height: 1.6; font-size: 0.95rem;">{doc['content']}</p>
                        <br>
                        <small style="color: #64748b; font-weight: 500;">Verified Reference: National Disaster Management Authority / Red Cross standard manuals</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
else:
    st.info("Enter a health emergency query above or click a quick shortcut button to load verified step-by-step first-aid actions.")
