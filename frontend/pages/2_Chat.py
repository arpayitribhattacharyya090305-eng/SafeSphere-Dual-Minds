import base64
import io
import sys
from pathlib import Path

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.auth_helper import AuthHelper
from frontend.custom_style import inject_custom_styles

st.set_page_config(page_title="RescueAI Chat - Multi-Agent Desk", layout="wide")
inject_custom_styles()

st.markdown("<h1 class='gradient-header'>Multi-Agent Disaster Desk</h1>", unsafe_allow_html=True)
st.markdown(
    "Coordinate with RescueAI agents for weather, shelter, navigation, medical, "
    "resource, communication, and relief planning."
)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "last_logs" not in st.session_state:
    st.session_state["last_logs"] = []

user_lat = 19.0760
user_lng = 72.8777
user_loc = "Mumbai"

if AuthHelper.is_logged_in():
    profile = st.session_state["user_profile"]
    user_lat = profile.get("location_lat") or 19.0760
    user_lng = profile.get("location_lng") or 72.8777
    user_loc = profile.get("location_address") or "Mumbai"


def play_tts(text: str) -> None:
    """Generate English audio for the latest response."""
    try:
        from gtts import gTTS

        read_text = text[:350] + "..." if len(text) > 350 else text
        tts = gTTS(text=read_text, lang="en")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64_audio = base64.b64encode(fp.read()).decode("utf-8")
        st.markdown(
            f"""
            <audio autoplay controls style="width: 100%; margin-top: 10px;">
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
            """,
            unsafe_allow_html=True,
        )
    except Exception as exc:
        st.warning(f"Voice generation unavailable: {exc}")


chat_col, log_col = st.columns([2, 1])

with log_col:
    st.markdown("### Agent Execution Flow")
    st.markdown("Monitor how the coordinator delegates tasks to specialized responders.")

    if st.session_state["last_logs"]:
        for log in st.session_state["last_logs"]:
            status = log.get("status", "Running")
            status_color = "#34d399" if status == "Success" else "#fb923c"
            findings = log.get("findings", "Processing...")
            st.markdown(
                f"""
                <div class="agent-log-bubble">
                    <span style="font-weight: 600; color: #f8fafc;">{log.get('agent', 'Agent')}</span><br>
                    <span style="font-size: 0.8rem; color: #94a3b8;">{log.get('timestamp', '')} - {log.get('action', '')}</span><br>
                    <span style="font-size: 0.85rem; color: {status_color};">{findings}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Ask a question to see agent execution logs.")

with chat_col:
    st.markdown("#### Voice Input")
    st.components.v1.html(
        """
        <div style="background: rgba(20, 24, 46, 0.7); padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); margin-bottom: 15px;">
            <button id="mic-btn" style="background: #b91c1c; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%;">
                Click to Speak
            </button>
            <p id="status" style="color: #9fb0c3; font-size: 0.85rem; margin-top: 8px; text-align: center; font-weight: 500;">Microphone status: Idle</p>
            <textarea id="output" placeholder="Your spoken text will appear here. Copy and paste it into the prompt box below." style="width: 100%; height: 50px; background: #0f172a; color: #e5edf5; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 8px; box-sizing: border-box; resize: none; margin-top: 5px; font-size: 0.9rem;"></textarea>
        </div>
        <script>
            const btn = document.getElementById('mic-btn');
            const status = document.getElementById('status');
            const output = document.getElementById('output');
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

            if (!SpeechRecognition) {
                status.innerText = "Browser speech recognition is not supported.";
                btn.disabled = true;
            } else {
                const rec = new SpeechRecognition();
                rec.continuous = false;
                rec.interimResults = false;
                rec.lang = 'en-IN';

                btn.onclick = () => {
                    try {
                        rec.start();
                        status.innerText = "Listening. Speak now.";
                        btn.style.background = "#15803d";
                    } catch(e) {
                        status.innerText = "Error: " + e.message;
                    }
                };

                rec.onresult = (event) => {
                    output.value = event.results[0][0].transcript;
                    status.innerText = "Speech captured. Copy and paste it below.";
                    btn.style.background = "#b91c1c";
                };

                rec.onerror = (event) => {
                    status.innerText = "Microphone error: " + event.error;
                    btn.style.background = "#b91c1c";
                };

                rec.onend = () => {
                    btn.style.background = "#b91c1c";
                };
            }
        </script>
        """,
        height=160,
    )

    for message in st.session_state["chat_history"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**Agent System:**\n{message['content']}")
            st.markdown("---")

    with st.form("chat_form", clear_on_submit=True):
        user_query = st.text_input(
            "Enter your request / emergency alert:",
            placeholder="Example: Help, my area is flooding. I need the nearest shelter route and asthma care.",
        )
        submit_btn = st.form_submit_button("Send Action Request", use_container_width=True)

    if submit_btn and user_query:
        st.session_state["chat_history"].append({"role": "user", "content": user_query})

        with st.spinner("Invoking RescueAI agents..."):
            try:
                payload = {
                    "user_query": user_query,
                    "user_location": user_loc,
                    "user_lat": user_lat,
                    "user_lng": user_lng,
                    "user_language": "English",
                }
                response = requests.post(
                    "http://localhost:8000/api/chat/execute",
                    json=payload,
                    headers=AuthHelper.get_headers(),
                    timeout=15,
                )
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("final_response", "No response returned.")
                    medical_advice = data.get("medical_advice")
                    if medical_advice and medical_advice not in response_text:
                        response_text += f"\n\n### Medical Advice\n{medical_advice}"

                    st.session_state["chat_history"].append(
                        {"role": "assistant", "content": response_text}
                    )
                    st.session_state["last_logs"] = data.get("agent_logs", [])
                    st.rerun()
                else:
                    st.error("Error executing the agent flow on the backend.")
            except Exception as exc:
                st.error(f"Failed to reach the FastAPI backend: {exc}")

    if st.session_state["chat_history"] and st.session_state["chat_history"][-1]["role"] == "assistant":
        if st.button("Read Latest Response Aloud", key="play_tts_btn"):
            play_tts(st.session_state["chat_history"][-1]["content"])
