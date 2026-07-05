import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000/api"

class AuthHelper:
    @staticmethod
    def get_headers() -> dict:
        headers = {}
        if "auth_token" in st.session_state and st.session_state["auth_token"]:
            headers["Authorization"] = f"Bearer {st.session_state['auth_token']}"
        return headers

    @staticmethod
    def login(email: str, password: str) -> bool:
        try:
            url = f"{BACKEND_URL}/auth/login"
            res = requests.post(url, json={"email": email, "password": password}, timeout=5)
            if res.status_code == 200:
                data = res.json()
                st.session_state["auth_token"] = data["access_token"]
                return AuthHelper.fetch_profile()
            else:
                st.error(f"Login failed: {res.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            st.error(f"Could not connect to backend api ({e})")
            return False

    @staticmethod
    def signup(signup_data: dict) -> bool:
        try:
            url = f"{BACKEND_URL}/auth/signup"
            res = requests.post(url, json=signup_data, timeout=5)
            if res.status_code == 200:
                st.success("Account created successfully! Please log in.")
                return True
            else:
                st.error(f"Signup failed: {res.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            st.error(f"Could not connect to backend api ({e})")
            return False

    @staticmethod
    def fetch_profile() -> bool:
        if "auth_token" not in st.session_state or not st.session_state["auth_token"]:
            return False
        try:
            url = f"{BACKEND_URL}/auth/profile"
            headers = AuthHelper.get_headers()
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                st.session_state["user_profile"] = res.json()
                return True
            else:
                AuthHelper.logout()
                return False
        except Exception:
            # Silent fallback if offline / backend stopped
            return False

    @staticmethod
    def logout():
        st.session_state["auth_token"] = None
        st.session_state["user_profile"] = None
        if "user_profile" in st.session_state:
            del st.session_state["user_profile"]
        if "auth_token" in st.session_state:
            del st.session_state["auth_token"]

    @staticmethod
    def is_logged_in() -> bool:
        return "user_profile" in st.session_state and st.session_state["user_profile"] is not None
