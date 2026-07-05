import streamlit as st


DEFAULT_PROFILE = {
    "full_name": "",
    "email": "",
    "location_address": "Mumbai",
    "location_lat": 19.0760,
    "location_lng": 72.8777,
    "medical_conditions": "",
    "family_members": [],
    "emergency_contacts": [],
}


def get_profile() -> dict:
    if "emergency_profile" not in st.session_state:
        st.session_state["emergency_profile"] = DEFAULT_PROFILE.copy()
    return st.session_state["emergency_profile"]


def update_profile(profile: dict) -> None:
    st.session_state["emergency_profile"] = {**DEFAULT_PROFILE, **profile}
