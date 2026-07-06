import streamlit as st
import requests

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


def rerun() -> None:
    """Safe wrapper for Streamlit rerun, supporting older and newer APIs."""
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def render_auth_sidebar() -> None:
    """Renders user authentication controls and status in the sidebar."""
    BACKEND_URL = "http://localhost:8000/api"
    
    auth_token = get_auth_token()
    st.sidebar.markdown("---")
    
    if auth_token:
        profile = get_profile()
        st.sidebar.markdown(f"**Signed in as:** {profile.get('full_name') or profile.get('email') or 'Citizen'}")
        if st.sidebar.button("Logout", key="sidebar_logout_btn"):
            try:
                requests.post(f"{BACKEND_URL}/auth/logout", headers={"Authorization": f"Bearer {auth_token}"}, timeout=5)
            except Exception:
                pass
            clear_auth_token()
            update_profile({})
            rerun()
    else:
        with st.sidebar.expander("Account"):
            st.write("Log in or create an account to enable personalized features.")
            tab = st.radio("Action", ["Login", "Sign up"], key="sidebar_auth_action")
            if tab == "Login":
                le = st.text_input("Email", key="sidebar_login_email")
                lp = st.text_input("Password", type="password", key="sidebar_login_password")
                if st.button("Login", key="sidebar_login_button"):
                    if not le or not lp:
                        st.error("Please enter both email and password.")
                    else:
                        try:
                            r = requests.post(f"{BACKEND_URL}/auth/login", json={"email": le, "password": lp}, timeout=5)
                            if r.status_code == 200:
                                token = r.json().get("access_token")
                                set_auth_token(token)
                                me = requests.get(f"{BACKEND_URL}/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=5)
                                if me.status_code == 200:
                                    u = me.json()
                                    update_profile({
                                        "full_name": u.get("full_name"),
                                        "email": u.get("email"),
                                        "location_address": u.get("location_address") or "Mumbai",
                                        "location_lat": u.get("location_lat") or 19.0760,
                                        "location_lng": u.get("location_lng") or 72.8777,
                                        "medical_conditions": u.get("medical_conditions") or "",
                                        "family_members": u.get("family_members") or [],
                                        "emergency_contacts": u.get("emergency_contacts") or [],
                                    })
                                st.success("Logged in successfully.")
                                rerun()
                            else:
                                detail = r.json().get("detail", "Login failed")
                                st.error(detail)
                        except Exception as exc:
                            st.error(f"Login request failed: {exc}")
            else:
                se = st.text_input("Email", key="sidebar_signup_email")
                sn = st.text_input("Full name", key="sidebar_signup_name")
                sp = st.text_input("Password", type="password", key="sidebar_signup_password")
                if st.button("Sign up", key="sidebar_signup_button"):
                    if not se or not sn or not sp:
                        st.error("All fields are required for sign up.")
                    else:
                        try:
                            r = requests.post(f"{BACKEND_URL}/auth/signup", json={"email": se, "password": sp, "full_name": sn}, timeout=5)
                            if r.status_code == 200:
                                st.success("Account created successfully! Please select 'Login' to log in.")
                            else:
                                detail = r.json().get("detail", "Sign up failed")
                                st.error(detail)
                        except Exception as exc:
                            st.error(f"Signup request failed: {exc}")
