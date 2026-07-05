import streamlit as st

def inject_custom_styles():
    """
    Injects custom CSS to style the Streamlit interface with a calm,
    professional operations palette and readable dashboard components.
    """
    css = """
    <style>
    /* Import outfit typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    :root {
        --bg: #0f172a;
        --sidebar: #111827;
        --surface: #172033;
        --surface-soft: #1e293b;
        --border: rgba(148, 163, 184, 0.18);
        --text: #e5edf5;
        --muted: #9fb0c3;
        --primary: #2dd4bf;
        --primary-strong: #14b8a6;
        --secondary: #60a5fa;
        --success: #86efac;
        --warning: #fbbf24;
        --danger: #fca5a5;
        --danger-strong: #fca5a5;
    }

    /* Main Container Styles */
    .stApp {
        background:
            radial-gradient(circle at 20% 0%, rgba(45, 212, 191, 0.08), transparent 28%),
            linear-gradient(180deg, #111827 0%, var(--bg) 55%, #0b1120 100%);
        color: var(--text);
    }

    /* Calm card design */
    .glass-card {
        background: rgba(23, 32, 51, 0.86);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 28px rgba(2, 6, 23, 0.22);
        transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(45, 212, 191, 0.34);
        box-shadow: 0 12px 30px rgba(45, 212, 191, 0.08);
        transform: translateY(-1px);
    }

    /* Indicator tags */
    .indicator-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-right: 8px;
    }
    .indicator-critical {
        background-color: rgba(248, 113, 113, 0.14);
        color: var(--danger);
        border: 1px solid rgba(248, 113, 113, 0.34);
    }
    .indicator-high {
        background-color: rgba(251, 191, 36, 0.14);
        color: var(--warning);
        border: 1px solid rgba(251, 191, 36, 0.34);
    }
    .indicator-medium {
        background-color: rgba(96, 165, 250, 0.14);
        color: var(--secondary);
        border: 1px solid rgba(96, 165, 250, 0.34);
    }
    .indicator-low {
        background-color: rgba(134, 239, 172, 0.14);
        color: var(--success);
        border: 1px solid rgba(134, 239, 172, 0.34);
    }

    /* Header styling */
    .gradient-header {
        background: linear-gradient(135deg, var(--text) 0%, var(--primary) 48%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: 0;
        margin-bottom: 24px;
    }

    /* Standardized flex details block */
    .details-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid var(--border);
    }
    .details-row:last-child {
        border-bottom: none;
    }
    .details-label {
        color: var(--muted);
        font-weight: 500;
    }
    .details-value {
        font-weight: 600;
        color: var(--text);
    }

    /* Speech bubble text */
    .agent-log-bubble {
        border-left: 3px solid var(--primary);
        padding-left: 12px;
        margin-bottom: 12px;
        background: rgba(45, 212, 191, 0.06);
        border-radius: 0 8px 8px 0;
        padding-top: 8px;
        padding-bottom: 8px;
    }

    /* Custom buttons styling */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary-strong) 0%, #2563eb 100%);
        color: #f8fafc;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0f766e 0%, #1d4ed8 100%);
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(45, 212, 191, 0.18);
    }

    /* Custom sidebar adjustment */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar);
        border-right: 1px solid var(--border);
    }

    input, textarea, select {
        color: var(--text) !important;
    }

    [data-testid="stMetricValue"],
    h1, h2, h3, h4, h5, h6 {
        letter-spacing: 0;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
