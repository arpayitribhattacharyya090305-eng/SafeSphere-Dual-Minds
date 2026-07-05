import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import SessionLocal
from backend.app.models.database_models import User
from frontend.auth_helper import AuthHelper
from frontend.custom_style import inject_custom_styles

st.set_page_config(page_title="RescueAI Settings", layout="wide")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Profile and Emergency Settings</h1>", unsafe_allow_html=True)
st.markdown(
    "Customize your emergency profile, declare critical health conditions, "
    "and maintain family and emergency contact details."
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


if not AuthHelper.is_logged_in():
    st.warning("Please log in or sign up from the home page sidebar to configure your emergency profile settings.")
else:
    user_profile = st.session_state["user_profile"]

    st.markdown("### Personal Emergency Profile")

    with st.form("settings_form"):
        full_name = st.text_input("Full Name", value=user_profile.get("full_name", ""))

        st.markdown("#### Health and First-Aid Details")
        medical_conditions = st.text_area(
            "Medical Conditions / Allergies / Asthmatic Status:",
            value=user_profile.get("medical_conditions", ""),
        )

        st.markdown("#### Primary Rescue Geolocation")
        address = st.text_input(
            "Primary Street Address",
            value=user_profile.get("location_address", ""),
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

        save_btn = st.form_submit_button("Save Profile Settings", use_container_width=True)

    if save_btn:
        db = SessionLocal()
        try:
            db_user = db.query(User).filter(User.id == user_profile["id"]).first()
            if db_user:
                db_user.full_name = full_name
                db_user.preferred_language = "English"
                db_user.medical_conditions = medical_conditions
                db_user.location_address = address
                db_user.location_lat = lat
                db_user.location_lng = lng
                db_user.family_members = _parse_family_members(family_input)
                db_user.emergency_contacts = _parse_contacts(contacts_input)

                db.commit()
                st.success("Profile details updated successfully.")
                AuthHelper.fetch_profile()
                st.rerun()
            else:
                st.error("User matching ID was not found in the database.")
        except Exception as exc:
            db.rollback()
            st.error(f"Error saving settings: {exc}")
        finally:
            db.close()
