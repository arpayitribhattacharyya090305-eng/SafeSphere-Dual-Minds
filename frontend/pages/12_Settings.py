import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
from frontend.custom_style import inject_custom_styles
from frontend.profile_state import get_profile, update_profile, get_auth_token, render_auth_sidebar

try:
    st.set_page_config(page_title="SafeSphere Settings", layout="wide", initial_sidebar_state="expanded")
except Exception:
    pass
inject_custom_styles()
# render_auth_sidebar()  # Handled globally in app.py

st.markdown("<h1 class='gradient-header'>Emergency Settings</h1>", unsafe_allow_html=True)
st.markdown(
    "Set the location and emergency details used by the rescue tools in this session."
)


def _parse_family_members(raw_value: str) -> list[dict]:
    members = []
    if not raw_value.strip():
        return members
    for item in raw_value.split(","):
        parts = [part.strip() for part in item.split("-")]
        if len(parts) != 3:
            continue
        try:
            members.append(
                {
                    "name": parts[0],
                    "relationship": parts[1],
                    "age": int(parts[2]),
                }
            )
        except ValueError:
            continue
    return members


def _parse_contacts(raw_value: str) -> list[dict]:
    contacts = []
    if not raw_value.strip():
        return contacts
    for item in raw_value.split(","):
        parts = [part.strip() for part in item.split("-")]
        if len(parts) == 3:
            contacts.append(
                {
                    "name": parts[0],
                    "relationship": parts[1],
                    "phone": parts[2],
                }
            )
    return contacts


user_profile = get_profile()

st.markdown("### Local Emergency Profile")

with st.form("settings_form"):
    full_name = st.text_input("Full Name", value=user_profile.get("full_name", ""))
    email = st.text_input("Email Address", value=user_profile.get("email", ""))

    st.markdown("#### Health and First-Aid Details")
    medical_conditions = st.text_area(
        "Medical Conditions / Allergies / Asthmatic Status:",
        value=user_profile.get("medical_conditions", ""),
    )

    st.markdown("#### Primary Rescue Geolocation")
    address = st.text_input(
        "Primary Street Address",
        value=user_profile.get("location_address", "Mumbai"),
    )

    col_lat, col_lng = st.columns(2)
    lat = col_lat.number_input(
        "Home Latitude",
        value=user_profile.get("location_lat", 19.0760),
        format="%.5f",
    )
    lng = col_lng.number_input(
        "Home Longitude",
        value=user_profile.get("location_lng", 72.8777),
        format="%.5f",
    )

    st.markdown("#### Family Members")
    family_entries = [
        f"{member.get('name')}-{member.get('relationship')}-{member.get('age')}"
        for member in user_profile.get("family_members", [])
    ]
    family_input = st.text_area(
        "Family Members (Format: Name-Relationship-Age, separate with commas):",
        value=", ".join(family_entries),
        placeholder="Example: Kiran Patel-Spouse-38, Aarav Patel-Son-12",
    )

    st.markdown("#### Emergency Contacts")
    contact_entries = [
        f"{contact.get('name')}-{contact.get('relationship')}-{contact.get('phone')}"
        for contact in user_profile.get("emergency_contacts", [])
    ]
    contacts_input = st.text_area(
        "Emergency Contacts (Format: Name-Relationship-Phone, separate with commas):",
        value=", ".join(contact_entries),
        placeholder="Example: Sanjay Patel-Brother-+91 98765 43210",
    )

    save_btn = st.form_submit_button("Save Emergency Settings", width="stretch")

if save_btn:
    profile_data = {
        "full_name": full_name.strip(),
        "email": email.strip(),
        "medical_conditions": medical_conditions.strip(),
        "location_address": address.strip() or "Mumbai",
        "location_lat": lat,
        "location_lng": lng,
        "family_members": _parse_family_members(family_input),
        "emergency_contacts": _parse_contacts(contacts_input),
    }
    update_profile(profile_data)
    
    # Persist to database if logged in
    auth_token = get_auth_token()
    if auth_token:
        BACKEND_URL = "http://localhost:8000/api"
        try:
            r = requests.put(
                f"{BACKEND_URL}/auth/profile",
                json=profile_data,
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=5
            )
            if r.status_code == 200:
                st.success("Emergency settings saved and synced to database.")
            else:
                st.warning("Emergency settings saved locally, but database sync failed: " + r.json().get("detail", "Error"))
        except Exception as exc:
            st.warning(f"Emergency settings saved locally, but database sync failed: {exc}")
    else:
        st.success("Emergency settings saved for this session.")
