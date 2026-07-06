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


def set_auth_token(token: str) -> None:
    st.session_state["auth_token"] = token


def get_auth_token() -> str | None:
    return st.session_state.get("auth_token")


def clear_auth_token() -> None:
    if "auth_token" in st.session_state:
        del st.session_state["auth_token"]
