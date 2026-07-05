import streamlit as st

def inject_custom_styles():
    """
    Injects custom CSS to style the Streamlit interface with a light,
    professional operations palette and readable dashboard components.
    """
    css = """
    <style>
    /* Import outfit typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    #MainMenu,
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stDeployButton"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Hide expand button when collapsed */
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Hide collapse button inside expanded sidebar */
    section[data-testid="stSidebar"] button[kind="headerNoPadding"] {
        display: none !important;
        visibility: hidden !important;
    }

    .block-container {
        padding-top: 2rem;
    }

    :root {
        --bg: #f7fafc;
        --sidebar: #ffffff;
        --surface: #ffffff;
        --surface-soft: #eef6fb;
        --border: #cbd8e6;
        --text: #172033;
        --muted: #516173;
        --primary: #0f766e;
        --primary-strong: #0d9488;
        --secondary: #2563eb;
        --success: #15803d;
        --warning: #b45309;
        --danger: #b91c1c;
        --danger-strong: #991b1b;
    }

    /* Main Container Styles */
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, var(--bg) 52%, #edf4f8 100%);
        color: var(--text);
    }

    /* Calm card design */
    .glass-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
        transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(15, 118, 110, 0.36);
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.1);
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
        background-color: #fee2e2;
        color: var(--danger);
        border: 1px solid #fecaca;
    }
    .indicator-high {
        background-color: #fef3c7;
        color: var(--warning);
        border: 1px solid #fde68a;
    }
    .indicator-medium {
        background-color: #dbeafe;
        color: var(--secondary);
        border: 1px solid #bfdbfe;
    }
    .indicator-low {
        background-color: #dcfce7;
        color: var(--success);
        border: 1px solid #bbf7d0;
    }

    /* Header styling */
    .gradient-header {
        background: linear-gradient(135deg, #123047 0%, var(--primary) 48%, var(--secondary) 100%);
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
        background: #ecfdf5;
        border-radius: 0 8px 8px 0;
        padding-top: 8px;
        padding-bottom: 8px;
    }

    /* Custom buttons styling */
    .stButton>button,
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, var(--primary-strong) 0%, #2563eb 100%);
        color: #f8fafc;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #0f766e 0%, #1d4ed8 100%);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(15, 118, 110, 0.18);
    }

    /* Custom sidebar adjustment */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar);
        border-right: 1px solid var(--border);
    }

    input, textarea, select {
        color: var(--text) !important;
        background-color: #ffffff !important;
        border-color: var(--border) !important;
    }

    [data-testid="stMetricValue"],
    h1, h2, h3, h4, h5, h6 {
        letter-spacing: 0;
        color: var(--text);
    }

    p, li, label, span, div, small, [data-testid="stMarkdownContainer"] {
        color: var(--text);
    }

    [data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] [role="button"] {
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] [aria-selected="true"],
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
        background-color: #e8f2ff !important;
        color: #123047 !important;
    }

    .glass-card h1,
    .glass-card h2,
    .glass-card h3,
    .glass-card h4,
    .glass-card h5,
    .glass-card p,
    .glass-card span,
    .glass-card small,
    .glass-card li,
    .details-value {
        color: var(--text) !important;
    }

    .details-label,
    .glass-card [style*="color: #94a3b8"],
    .glass-card [style*="color:#94a3b8"],
    .glass-card [style*="color: #9fb0c3"],
    .glass-card [style*="color:#9fb0c3"],
    .glass-card [style*="color: #8fa1b6"],
    .glass-card [style*="color:#8fa1b6"],
    .glass-card [style*="color: #64748b"],
    .glass-card [style*="color:#64748b"] {
        color: var(--muted) !important;
    }

    .glass-card [style*="color: #f8fafc"],
    .glass-card [style*="color:#f8fafc"],
    .glass-card [style*="color: #cbd5e1"],
    .glass-card [style*="color:#cbd5e1"],
    .glass-card [style*="color: #cbd7e3"],
    .glass-card [style*="color:#cbd7e3"],
    .glass-card [style*="color: #e5edf5"],
    .glass-card [style*="color:#e5edf5"] {
        color: var(--text) !important;
    }

    .glass-card [style*="background: rgba(255, 255, 255, 0.03)"],
    [style*="background: rgba(20, 24, 46, 0.7)"] {
        background: var(--surface-soft) !important;
        border-color: var(--border) !important;
    }

    [style*="background: #0f172a"] {
        background: #ffffff !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
