import streamlit as st
import pandas as pd
import pickle
import sys
import os
import textwrap
import json
import base64

# ----------------------------
# PATH SETUP
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(BASE_DIR, "src")
MODEL_PATH = os.path.join(BASE_DIR, "models", "mental_health_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "mental_health.csv")
LOGO_PATH = os.path.join(BASE_DIR, "data", "logo.png")
REMEMBER_FILE = os.path.join(BASE_DIR, ".remembered_users.json")

def save_remembered_user(identifier, password):
    data = {}
    if os.path.exists(REMEMBER_FILE):
        try:
            with open(REMEMBER_FILE, "r") as f:
                data = json.load(f)
        except:
            pass
    # Encrypt password using base64 for local storage
    encoded_pw = base64.b64encode(password.encode("utf-8")).decode("utf-8")
    data[identifier] = encoded_pw
    with open(REMEMBER_FILE, "w") as f:
        json.dump(data, f)

def get_remembered_password(identifier):
    if os.path.exists(REMEMBER_FILE):
        try:
            with open(REMEMBER_FILE, "r") as f:
                data = json.load(f)
            if identifier in data:
                return base64.b64decode(data[identifier].encode("utf-8")).decode("utf-8")
        except:
            pass
    return None

def clear_remembered_user(identifier):
    if os.path.exists(REMEMBER_FILE):
        try:
            with open(REMEMBER_FILE, "r") as f:
                data = json.load(f)
            if identifier in data:
                del data[identifier]
                with open(REMEMBER_FILE, "w") as f:
                    json.dump(data, f)
        except:
            pass

sys.path.append(SRC_PATH)
from groq_helper import generate_advice
from sentiment_analysis import analyze_sentiment
from auth import (
    register_user, login_user, update_streak, save_mood, update_therapy_usage,
    get_user, reset_password, update_user_activity, increment_therapy_session,
    get_dashboard_data
)
from therapy_components import show_therapy, gamification_banner, show_exercises_page

# ----------------------------
# WELCOME POPUP  (session-once)
# ----------------------------
@st.dialog("Welcome to Mind Mesh 👋")
def _show_welcome_popup():
    st.markdown("""
    <div style='text-align:center;padding:6px 0 18px'>
        <div style='font-size:52px;margin-bottom:10px'>🧠</div>
        <p style='color:#475569;font-size:16px;line-height:1.8;'>
            You can use <b style='color:#0ea5e9'>Mind Mesh</b> completely <b>without logging in</b>.<br>
            Create an account only if you want to save your<br>
            <b>mood history</b>, <b>self-care streaks</b> and <b>therapy progress</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Continue without login", use_container_width=True,
                     key="popup_guest_btn", type="secondary"):
            st.session_state.popup_shown = True
            st.rerun()
    with col2:
        if st.button("👤 Go to Account", use_container_width=True,
                     key="popup_account_btn", type="primary"):
            st.session_state.popup_shown = True
            st.session_state.current_page = "Account"
            st.rerun()



# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Mind Mesh", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "session_exercises_done" not in st.session_state:
    st.session_state.session_exercises_done = 0
if "guest_streak" not in st.session_state:
    st.session_state.guest_streak = 0
if "guest_last_activity_date" not in st.session_state:
    st.session_state.guest_last_activity_date = None
if "guest_therapy_date" not in st.session_state:
    st.session_state.guest_therapy_date = None
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "Login"
if "popup_shown" not in st.session_state:
    st.session_state.popup_shown = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Analyze"

# Show popup once per session (must be after set_page_config)
if not st.session_state.popup_shown:
    _show_welcome_popup()

# ----------------------------
# UI CSS
# ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Poppins:wght@500;600;700&family=Montserrat:wght@700;800;900&display=swap');

/* Base Theme */
.stApp {
    background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
    font-family: 'Inter', sans-serif;
}
html, body, [class*="css"]  {
    color: #1e293b !important;
}

header[data-testid="stHeader"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
    border-bottom: 2px solid #38bdf8 !important;
    height: 70px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    z-index: 99999 !important;
    position: fixed !important;
    left: 0 !important;
    width: 100vw !important;
    max-width: 100vw !important;
}

header[data-testid="stHeader"]::after {
    content: " MIND MESH: AI-Based Mental Health Warning System";
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 28px;
    font-family: 'Montserrat', sans-serif;
    font-weight: 800;
    letter-spacing: 1px;
    white-space: nowrap;
    pointer-events: none;
}


[data-testid="collapsedControl"], 
.stApp header button, 
section[data-testid="stSidebar"] button {
    background-color: #0ea5e9 !important; /* Bright vivid blue */
    border-radius: 8px !important;
    padding: 5px !important;
    opacity: 1 !important; /* Override streamlit's default fading */
    visibility: visible !important;
    display: inline-flex !important;
    z-index: 999999 !important;
}

[data-testid="collapsedControl"]:hover, 
.stApp header button:hover, 
section[data-testid="stSidebar"] button:hover {
    background-color: #0284c7 !important;
    transform: scale(1.05);
}

[data-testid="collapsedControl"] svg, 
.stApp header button svg, 
section[data-testid="stSidebar"] button svg {
    stroke: white !important;
    fill: white !important;
    width: 24px !important;
    height: 24px !important;
}


.stApp .main .block-container {
    padding-top: 100px !important;
}


section[data-testid="stSidebar"] {
    margin-top: 70px !important; 
    height: calc(100vh - 70px) !important;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important; 
    border-right: none !important;
    box-shadow: 2px 0 15px rgba(0,0,0,0.1);
}
section[data-testid="stSidebar"] h2 {
    font-weight: 900 !important;
    font-size: 26px !important;
    color: #38bdf8 !important;
    text-align: center;
}
section[data-testid="stSidebar"] * {
    color: rgba(255, 255, 255, 0.9) !important;
}

/* Navigation Radio Buttons */
div[role="radiogroup"] {
    gap: 12px;
}
div[role="radiogroup"] > label {
    font-size: 18px !important;
    font-weight: 700;
    padding: 15px 20px;
    border-radius: 12px;
    transition: all 0.3s ease;
    cursor: pointer;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    margin-bottom: 5px;
}
div[role="radiogroup"] > label:hover {
    background: linear-gradient(135deg, #14b8a6 0%, #0ea5e9 100%) !important;
    color: white !important;
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
    border-color: transparent !important;
}
div[role="radiogroup"] > label:hover * {
    color: white !important;
}

/* Cards */
.card {
    background: rgba(255, 255, 255, 0.85);
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.8);
    margin-bottom: 25px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.08);
}


.resource-card {
    background: linear-gradient(135deg, #ffffff 0%, #fdf4ff 100%); 
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    margin-bottom: 20px;
    border-left: 6px solid #8b5cf6;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    height: 100%;
    position: relative;
    overflow: hidden;
}
.resource-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(14, 165, 233, 0.1));
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 0;
}
.resource-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 30px rgba(139, 92, 246, 0.2);
    border-left: 6px solid #0ea5e9;
}
.resource-card:hover::after {
    opacity: 1;
}
.resource-card h4, .resource-card p, .resource-card a {
    position: relative;
    z-index: 1;
}
.resource-card h4 {
    margin-top: 0 !important;
    color: #7c3aed !important;
    font-weight: 800 !important;
    font-size: 22px !important;
    margin-bottom: 12px !important;
    font-family: 'Montserrat', sans-serif;
}
.resource-card p {
    color: #334155 !important;
    margin-bottom: 20px !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
}
.resource-btn {
    display: inline-block;
    padding: 12px 24px;
    background: #8b5cf6;
    color: white !important;
    text-decoration: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 15px;
    transition: all 0.3s;
    box-shadow: 0 4px 10px rgba(139, 92, 246, 0.3);
}
.resource-btn:hover {
    background: #0ea5e9;
    box-shadow: 0 6px 15px rgba(14, 165, 233, 0.4);
    transform: translateY(-2px);
}


.grid-card {
    background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
    padding: 35px;
    border-radius: 20px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
    text-align: center;
    margin-bottom: 20px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    border: 1px solid rgba(14, 165, 233, 0.1);
}
.grid-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 35px rgba(14, 165, 233, 0.15);
    border-color: rgba(14, 165, 233, 0.3);
}
.grid-card img {
    margin-bottom: 20px;
    transition: transform 0.3s ease;
}
.grid-card:hover img {
    transform: scale(1.1);
}
.grid-card h3 {
    font-size: 24px !important;
    color: #0ea5e9 !important;
    margin-bottom: 15px !important;
    font-family: 'Montserrat', sans-serif;
    font-weight: 800 !important;
}
.grid-card p {
    color: #475569 !important;
    font-size: 17px !important;
    line-height: 1.5;
}


.stTabs [data-baseweb="tab-list"] {
    gap: 15px;
    background-color: transparent;
}
.stTabs [data-baseweb="tab"] {
    height: auto;
    white-space: pre-wrap;
    font-family: 'Montserrat', sans-serif !important;
    background-color: #ede9fe !important;
    border-radius: 15px !important;
    padding: 15px 30px !important;
    font-weight: 800 !important;
    font-size: 20px !important; /* BIGGER FONT */
    color: #5b21b6 !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    border: 2px solid #ddd6fe !important;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stTabs [data-baseweb="tab"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    background-color: #ddd6fe !important;
    color: #4c1d95 !important;
    border-color: #c4b5fd !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: 0 10px 20px rgba(139, 92, 246, 0.4) !important;
    border-bottom: none !important;
    transform: scale(1.05);
}
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}


.stButton>button {
    background: linear-gradient(135deg, #14b8a6 0%, #0ea5e9 100%);
    color: white !important;
    border-radius: 12px;
    height: 55px;
    width: 100%;
    font-size: 20px;
    font-weight: 700;
    border: none;
    box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #0d9488 0%, #0284c7 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4);
}
.stButton>button:active {
    transform: translateY(1px);
}

/* Text Area */
.stTextArea textarea {
    border-radius: 15px !important;
    border: 2px solid #e2e8f0 !important;
    font-size: 18px !important;
    padding: 15px !important;
    transition: all 0.3s ease;
    background: #f8fafc !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}
.stTextArea textarea:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.2) !important;
    background: white !important;
}


.stTextArea label {
    font-size: 22px !important;
    color: #1e293b !important;
    font-weight: 800 !important;
    margin-bottom: 10px !important;
}

.stAlert {
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}


@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}


h1, h2, h3, h4 {
    color: #1e293b !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

if st.session_state.dark_mode:
    st.markdown("""
    <style>
   
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
    }
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span, .stTextArea label {
        color: #f8fafc !important;
    }
    .card, .resource-card, .grid-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3) !important;
    }
    .resource-card h4 {
        color: #a78bfa !important;
    }
    .grid-card h3 {
        color: #38bdf8 !important;
    }
    .resource-card p, .grid-card p {
        color: #cbd5e1 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #334155 !important;
        color: #cbd5e1 !important;
        border-color: #475569 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #475569 !important;
        color: white !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
        color: white !important;
    }
    .stTextArea textarea {
        background: #1e293b !important;
        color: #f8fafc !important;
        border-color: #475569 !important;
    }
    .stTextArea textarea:focus {
        background: #0f172a !important;
    }
    div[style*="color: #64748b"] {
        color: #94a3b8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------
# LOAD MODEL
# ----------------------------
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except:
    st.error("Model file not found ")
    st.stop()

# ----------------------------
# LOAD DATA
# ----------------------------
try:
    df = pd.read_csv(DATA_PATH)
except:
    st.error("Dataset file not found ")
    st.stop()

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.image(LOGO_PATH, width=120)
st.sidebar.markdown("<h2 style='text-align: center;'>🧠 MIND MESH</h2>", unsafe_allow_html=True)

st.sidebar.toggle(
    "🌙 Dark Mode", 
    key="dark_mode",
    help="Toggle between light and dark mode"
)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Minimal logged-in pill (no form in sidebar)
if st.session_state.logged_in:
    st.sidebar.markdown(
        f"<div style='background:rgba(14,165,233,0.15);border:1px solid rgba(14,165,233,0.3);"
        f"border-radius:12px;padding:9px 14px;text-align:center;margin-bottom:4px;'>"
        f"<span style='font-size:13px;color:#38bdf8;font-weight:700'>"
        f"👤 {st.session_state.username}</span><br>"
        f"<span style='font-size:12px;color:#7dd3fc'>🔥 {st.session_state.streak}-day streak</span>"
        f"</div>",
        unsafe_allow_html=True
    )
    if st.sidebar.button("🚪 Logout", use_container_width=True, key="sb_logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username  = None
        st.session_state.streak    = 0
        st.rerun()


st.sidebar.markdown("<br>", unsafe_allow_html=True)

_NAV_PAGES = ["Analyze", "Exercises", "Resources", "About"]

def _on_nav_change():
    st.session_state.current_page = st.session_state.main_nav_radio

# Sync the radio key with current_page if applicable
if st.session_state.current_page in _NAV_PAGES:
    st.session_state.main_nav_radio = st.session_state.current_page

st.sidebar.radio(
    "Navigation", _NAV_PAGES,
    label_visibility="collapsed",
    key="main_nav_radio",
    on_change=_on_nav_change
)

# Account option separated by a divider
st.sidebar.markdown(
    "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.15);margin:14px 4px'>",
    unsafe_allow_html=True
)
if st.sidebar.button("👤  Account", use_container_width=True, key="sidebar_account_nav_btn"):
    st.session_state.current_page = "Account"
    st.rerun()

menu = st.session_state.current_page


# ANALYZE PAGE
# ----------------------------
if menu == "Analyze":

    st.markdown("<p style='font-size: 18px; font-weight: 600; color: #0ea5e9; margin-bottom: 5px;'>You can choose how you want to proceed — select a mood, share your thoughts, or use both for a more personalized analysis. 🌟</p>", unsafe_allow_html=True)
    st.markdown("<h3>🎭 How are you feeling right now? Choose the option that best describes your current mood.</h3>", unsafe_allow_html=True)
    mood_options = ["Select your mood...", "Normal 😐", "Happy 😊", "Sad 😢", "Stressed 😫", "Depressed 😔"]
    selected_mood = st.selectbox("", mood_options, label_visibility="collapsed")
    
    needs_questionnaire = selected_mood in ["Sad 😢", "Stressed 😫", "Depressed 😔"]
    questionnaire_responses = []

    if needs_questionnaire:
        st.markdown("---")
        st.markdown("<h3 style='color: #0ea5e9;'>📋 Let's understand your situation better</h3>", unsafe_allow_html=True)
        st.info("Please answer the following questions to help us evaluate your state.")
        
        questions = [
            "Do you have trouble sleeping?",
            "Do you often feel sad or low?",
            "Do you feel tired without reason?",
            "Do you lose interest in activities?",
            "Do you feel hopeless about future?",
            "Do you find it hard to concentrate?",
            "Do you feel lonely even with people?",
            "Do you feel worthless sometimes?",
            "Do you overthink small problems?",
            "Do you feel anxious or restless often?"
        ]
        options_map = {"Never": 0, "Sometimes": 1, "Often": 2, "Always": 3}
        
        for i, q in enumerate(questions):
            st.markdown(f"**{i+1}. {q}**")
            response = st.radio("", options=list(options_map.keys()), horizontal=True, key=f"q_{i}", label_visibility="collapsed")
            questionnaire_responses.append(options_map[response])
        st.markdown("---")

    st.markdown("<h3 style='margin-top: 20px;'>📝 Share more about how you’re feeling.</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 18px; font-weight: 600; font-style: italic; color: #8b5cf6; margin-bottom: 10px;'>This is a safe, non-judgmental space to express your thoughts freely. 🕊️✨</p>", unsafe_allow_html=True)
    text = st.text_area("", height=200, placeholder="Write here...")

    # Privacy consent — only for logged-in users
    if st.session_state.logged_in:
        st.markdown(
            "<p style='font-size:13px;color:#94a3b8;margin-top:4px;'>"
            "🔒 <b>Privacy:</b> Your mental health text is <b>never stored</b> unless you explicitly consent below."
            "</p>",
            unsafe_allow_html=True
        )
        privacy_consent = st.checkbox(
            "I consent to my text being stored securely to improve my personal experience.",
            key="privacy_consent"
        )
    else:
        privacy_consent = False

    analyze_btn = st.button("🔍 Analyze")

    # Clear cached analysis if user changes input
    if st.session_state.get("analyze_last_mood") != selected_mood or st.session_state.get("analyze_last_text") != text:
        for key in ["analyze_prediction", "analyze_advice", "analyze_percentage", "analyze_needs_questionnaire", "analyze_questionnaire_score", "analyze_show_results"]:
            if key in st.session_state:
                del st.session_state[key]

    if analyze_btn:
        has_mood = selected_mood != "Select your mood..."
        has_text = text.strip() != ""
        
        if not has_mood and not has_text:
            st.warning("Please select your mood or share your thoughts to proceed.")
        else:
            with st.spinner("Analyzing..."):
                st.session_state.analyze_last_mood = selected_mood
                st.session_state.analyze_last_text = text
                st.session_state.analyze_therapy_running = False  # Prevent results block from hiding if timer was abandoned

                
                if needs_questionnaire:
                    total_score = sum(questionnaire_responses)
                    percentage = (total_score / 30.0) * 100
                    st.session_state.analyze_percentage = percentage
                    st.session_state.analyze_needs_questionnaire = True
                else:
                    st.session_state.analyze_needs_questionnaire = False
                
                prediction = None

                mood_map = {
                    "Normal 😐": "Normal",
                    "Happy 😊": "Normal",
                    "Sad 😢": "Depression",
                    "Stressed 😫": "Stress",
                    "Depressed 😔": "Depression"
                }

                if has_text:
                    cleaned_text = text.lower().strip()
                    sentiment = analyze_sentiment(cleaned_text)
                    prediction = model.predict([cleaned_text])[0]

                    # -------------------------------------------------------
                    # POST-PROCESSING LAYER  (model is never retrained)
                    # -------------------------------------------------------
                    MILD_KEYWORDS = [
                        "sad", "tired", "low", "upset",
                        "not feeling good", "lonely today",
                        "a bit down", "feeling off", "dull",
                        "not great", "meh", "gloomy"
                    ]
                    STRONG_DEPRESSION_KEYWORDS = [
                        "hopeless", "empty", "worthless", "no purpose",
                        "give up", "nothing matters", "no point",
                        "don't want to live", "end it", "can't go on",
                        "no reason to", "feel dead inside", "suicidal"
                    ]

                    has_mild      = any(kw in cleaned_text for kw in MILD_KEYWORDS)
                    has_strong    = any(kw in cleaned_text for kw in STRONG_DEPRESSION_KEYWORDS)

                    if sentiment == "Positive":
                        prediction = "Normal"
                    elif has_strong:
                        prediction = "Depression"
                    elif has_mild and prediction == "Depression" and sentiment != "Negative":
                        prediction = "Stress"
                    elif has_mild and prediction == "Depression":
                        prediction = "Stress"
                    elif sentiment == "Negative" and prediction == "Normal":
                        prediction = "Stress"
                    # -------------------------------------------------------

                elif has_mood:
                    prediction = mood_map.get(selected_mood, "Normal")

                st.session_state.analyze_prediction = prediction

                try:
                    prompt_text = text
                    if has_mood and has_text:
                        prompt_text = f"The user is feeling {selected_mood.split(' ')[0]} and shared: '{text}'"
                    elif has_mood and not has_text:
                        prompt_text = f"The user is feeling {selected_mood.split(' ')[0]} today. Please give them some supportive advice."

                    # ── Fetch saved mood history for personalisation ────────
                    user_mood_history = None
                    if st.session_state.logged_in:
                        user_doc = get_user(st.session_state.username)
                        if user_doc:
                            history = user_doc.get("mood_history", [])
                            if history:
                                user_mood_history = history
                                st.session_state.analyze_used_history = True
                            else:
                                st.session_state.analyze_used_history = False
                        else:
                            st.session_state.analyze_used_history = False
                    else:
                        st.session_state.analyze_used_history = False

                    st.session_state.analyze_advice = generate_advice(
                        prompt_text, mood_history=user_mood_history
                    )
                except:
                    st.session_state.analyze_advice = "AI advice unavailable"
                    st.session_state.analyze_used_history = False

                # ── Save mood only if user consented ───────────────
                if prediction and privacy_consent and st.session_state.logged_in:
                    save_mood(
                        st.session_state.username,
                        selected_mood if has_mood else "Not selected",
                        prediction,
                        st.session_state.analyze_percentage if needs_questionnaire else None,
                        thought_text=text if has_text else ""
                    )

                # ── Update self-care streak once per day for mood analysis ──
                if prediction:
                    if st.session_state.logged_in:
                        st.session_state.streak = update_user_activity(st.session_state.username)
                    else:
                        from datetime import date
                        today = str(date.today())
                        if st.session_state.guest_last_activity_date != today:
                            st.session_state.guest_streak += 1
                            st.session_state.guest_last_activity_date = today

                st.session_state.analyze_show_results = True
            
            st.rerun()  # Force a clean rerun to prevent ghosting elements from the spinner's DOM shift

    if st.session_state.get("analyze_show_results", False):
        # ── Guard: if breathing timer is ticking, only re-render the therapy widget ──
        therapy_running = st.session_state.get("analyze_therapy_running", False)
        prediction = st.session_state.get("analyze_prediction")

        if True:  # Prevent layout shift by always showing the results block
            # Full results block (only renders when timer is NOT ticking)
            if st.session_state.get("analyze_needs_questionnaire", False):
                percentage = st.session_state.analyze_percentage
                st.subheader("📊 Questionnaire Result")
                if percentage <= 30:
                    st.success(f"**Score: {percentage:.1f}% - ✔ Low Risk**\n\nUser is mentally stable. No major concern.")
                elif percentage <= 60:
                    st.warning(f"**Score: {percentage:.1f}% - ⚠️ Moderate Risk**\n\nMild stress or emotional disturbance. Suggested relaxation and self-care.")
                else:
                    st.error(f"**Score: {percentage:.1f}% - 🚨 High Risk**\n\nPossible depression symptoms. Suggest talking to someone or seeking help.")

            if prediction:
                st.subheader("🧠 Emotional State Prediction")
                st.success(prediction)

                if prediction == "Depression":
                    st.warning("⚠️ You might be feeling low. Consider talking to someone you trust.")
                elif prediction == "Anxiety":
                    st.warning("⚠️ You might be feeling anxious.")
                elif prediction == "Stress":
                    st.warning("⚠️ You might be feeling stressed.")
                else:
                    st.success("😊 You seem emotionally stable.")

                # ── AI Advice — always visible immediately after prediction ──
                st.markdown("---")
                used_history = st.session_state.get("analyze_used_history", False)
                if used_history:
                    st.markdown(
                        "<span style='font-size:22px;font-weight:800;'>🤖 AI Advice</span> "
                        "<span style='background:#10b981;color:white;font-size:12px;font-weight:700;"
                        "padding:3px 10px;border-radius:20px;vertical-align:middle;'>✨ Personalised to your history</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.subheader("🤖 AI Advice")
                if st.session_state.get("analyze_advice") == "AI advice unavailable":
                    st.error("AI advice unavailable")
                else:
                    st.info(st.session_state.get("analyze_advice", ""))

        # ── Personalized Therapy Session — only for sad/negative moods ──────
        if prediction in ("Depression", "Stress", "Anxiety"):
            # ── Exercise completion callback ──────────────────────────
            def on_exercise_complete():
                from datetime import date
                today = str(date.today())
                if st.session_state.logged_in:
                    result = increment_therapy_session(st.session_state.username, prediction)
                    st.session_state.streak = result.get("streak", st.session_state.streak)
                    st.session_state.session_exercises_done = result.get("therapy_sessions_today", st.session_state.session_exercises_done)
                else:
                    if st.session_state.guest_therapy_date != today:
                        st.session_state.session_exercises_done = 0
                        st.session_state.guest_therapy_date = today
                    st.session_state.session_exercises_done += 1
                    if st.session_state.guest_last_activity_date != today:
                        st.session_state.guest_streak += 1
                        st.session_state.guest_last_activity_date = today

            if True:  # Keep banner visible to prevent layout shift
                gamification_banner(
                    logged_in=st.session_state.logged_in,
                    streak=st.session_state.streak if st.session_state.logged_in else st.session_state.guest_streak,
                    session_count=st.session_state.session_exercises_done
                )
                # ── Therapy heading — rendered ONCE here, not inside show_therapy ──
                st.markdown("---")
                st.subheader("🧘 Personalized Therapy Session")

            # ── Interactive Therapy Session ───────────────────────────
            show_therapy(prediction, on_complete_callback=on_exercise_complete)

            # ── Motivational footer (only when timer is not running) ──
            if True:  # Keep footer visible to prevent layout shift
                st.markdown("---")
                st.markdown("""
                <div style='
                    background: linear-gradient(135deg, #eef7ff, #f5f0ff);
                    border-radius: 20px;
                    padding: 28px 32px;
                    border-left: 6px solid #8b5cf6;
                    box-shadow: 0 8px 25px rgba(139,92,246,0.12);
                    margin-top: 24px;
                '>
                    <p style='font-size:20px;font-weight:900;color:#1e293b;margin:0 0 10px;'>
                        💪 Feeling low, sad, or stressed? You are not alone.
                    </p>
                    <p style='font-size:16px;font-style:italic;color:#64748b;border-top:0;padding-top:0;margin:0 0 16px;'>
                        🌟 <em>"You don't have to control your thoughts. You just have to stop letting them control you."</em><br>
                        <span style='font-size:14px;color:#94a3b8;'>— Dan Millman</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                # Clickable navigation buttons
                st.markdown("<p style='font-size:16px;font-weight:700;color:#475569;margin:14px 0 6px;'>👇 Explore more support:</p>", unsafe_allow_html=True)
                nav_col1, nav_col2 = st.columns(2)
                with nav_col1:
                    if st.button("🌿 Go to Exercises", key="footer_goto_exercises", use_container_width=True):
                        st.session_state.current_page = "Exercises"
                        st.rerun()
                with nav_col2:
                    if st.button("📚 Go to Resources", key="footer_goto_resources", use_container_width=True):
                        st.session_state.current_page = "Resources"
                        st.rerun()





# ----------------------------
# EXERCISES PAGE
# ----------------------------
elif menu == "Exercises":

    def on_general_exercise_complete():
        from datetime import date
        today = str(date.today())
        if st.session_state.logged_in:
            result = increment_therapy_session(st.session_state.username, "Exercises Page")
            st.session_state.streak = result.get("streak", st.session_state.streak)
            st.session_state.session_exercises_done = result.get("therapy_sessions_today", st.session_state.session_exercises_done)
        else:
            if st.session_state.guest_therapy_date != today:
                st.session_state.session_exercises_done = 0
                st.session_state.guest_therapy_date = today
            st.session_state.session_exercises_done += 1
            if st.session_state.guest_last_activity_date != today:
                st.session_state.guest_streak += 1
                st.session_state.guest_last_activity_date = today

    show_exercises_page(on_complete_callback=on_general_exercise_complete)


# ----------------------------
# ABOUT PAGE
# ----------------------------
elif menu == "About":
    st.markdown("<h1 style='text-align: center; color: #0ea5e9 !important;'>📖 About Mind Mesh</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #64748b; margin-bottom: 30px;'>A proactive approach to mental well-being using advanced Machine Learning.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="grid-card">
            <img src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png" width="80">
            <h3>🤖 AI-Powered System</h3>
            <p>Uses Machine Learning to analyze mental health patterns and detect early warning signs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="grid-card">
            <img src="https://cdn-icons-png.flaticon.com/512/3209/3209265.png" width="80">
            <h3>🌍 Awareness</h3>
            <p>Promotes mental health awareness and encourages proactive well-being management.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="grid-card">
            <img src="https://cdn-icons-png.flaticon.com/512/2913/2913465.png" width="80">
            <h3>💡 Smart Insights</h3>
            <p>Provides intelligent, context-aware suggestions to help you navigate your feelings.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="grid-card">
            <img src="https://cdn-icons-png.flaticon.com/512/2966/2966483.png" width="80">
            <h3>⚠️ Disclaimer</h3>
            <p>This is an AI tool and not a replacement for professional medical or psychological advice.</p>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------
# RESOURCES PAGE
# ----------------------------
elif menu == "Resources":

    st.markdown("<h1 style='text-align: center; color: #0ea5e9 !important; margin-bottom: 30px;'>📚 Mental Health Resources</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📱 Apps", "📄 Articles", "📚 Books", "🎧 Podcasts", "🏢 Organizations"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="resource-card">
                <h4>Calm</h4>
                <p>Provides guided meditations, sleep stories, and breathing exercises to help reduce anxiety and improve sleep quality.</p>
                <a href="https://www.calm.com" target="_blank" class="resource-btn">Visit Website</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>Wysa</h4>
                <p>An AI-powered chatbot that uses evidence-based techniques like CBT and mindfulness to support users in managing stress.</p>
                <a href="https://www.wysa.com" target="_blank" class="resource-btn">Visit Website</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>Sanvello</h4>
                <p>Provides daily tools to manage stress, anxiety, and depression using CBT, mindfulness, and mood tracking.</p>
                <a href="https://www.sanvello.com" target="_blank" class="resource-btn">Visit Website</a>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="resource-card">
                <h4>Headspace</h4>
                <p>A meditation and mindfulness app offering guided sessions, sleep aids, and stress-reduction techniques.</p>
                <a href="https://www.headspace.com" target="_blank" class="resource-btn">Visit Website</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>Youper</h4>
                <p>An AI-powered emotional health assistant that guides you through conversations and activities.</p>
                <a href="https://www.youper.ai" target="_blank" class="resource-btn">Visit Website</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>Cope Notes</h4>
                <p>Sends daily text messages with positive thoughts, exercises, and journaling prompts to help combat depression.</p>
                <a href="https://copenotes.com/" target="_blank" class="resource-btn">Visit Website</a>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="resource-card">
                <h4>A Programmer’s Guide to Stress</h4>
                <p>By Daragh Byrne. An excellent guide tailored for software developers dealing with workplace stress.</p>
                <a href="https://medium.com" target="_blank" class="resource-btn">Read Article</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>Burnout Recovery Guide</h4>
                <p>Practical strategies for managing burnout and restoring your energy and passion.</p>
                <a href="https://medium.com" target="_blank" class="resource-btn">Read Article</a>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="resource-card">
                <h4>Developer Depression</h4>
                <p>By Lauren Maffeo. Discussing the unspoken challenges of mental health in the tech industry.</p>
                <a href="https://medium.com" target="_blank" class="resource-btn">Read Article</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>It's Okay To Not Be Okay</h4>
                <p>By Andrew Montagne. A reminder that struggling is human and seeking help is a strength.</p>
                <a href="https://dev.to/fogs/its-okay-to-not-be-okay" target="_blank" class="resource-btn">Read Article</a>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="resource-card">
                <h4>Peopleware</h4>
                <p>By Tom DeMarco & Timothy Lister. Focuses on the human factors in software development.</p>
                <a href="https://www.amazon.com/Peopleware-Productive-Projects-Teams-3rd/dp/0321934113" target="_blank" class="resource-btn">View Book</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>Slack</h4>
                <p>Getting Past Burnout, Busywork, and the Myth of Total Efficiency. Highlights the importance of balance.</p>
                <a href="https://www.amazon.com/Slack-Getting-Burnout-Busywork-Efficiency/dp/0767907698" target="_blank" class="resource-btn">View Book</a>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="resource-card">
                <h4>It Doesn’t Have to Be Crazy at Work</h4>
                <p>By Jason Fried & DHH. Promotes a calm, sustainable, and healthy work culture.</p>
                <a href="https://www.amazon.com/Doesnt-Have-Be-Crazy-Work/dp/0062874780" target="_blank" class="resource-btn">View Book</a>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="resource-card">
                <h4>Destigmatizing Mental Health</h4>
                <p>Scott Hanselman interviews Dr. Jennifer Akullian about breaking the stigma in the tech industry.</p>
                <a href="https://hanselminutes.com/728/destigmatizing-mental-health-in-the-tech-industry-with-jen-akullian-phd" target="_blank" class="resource-btn">Listen Now</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>GET REAL: Podcast</h4>
                <p>Honest and intrepid discussions about mental health and disability from frontline workers and advocates.</p>
                <a href="https://www.ermha.org/get-real-podcast/" target="_blank" class="resource-btn">Listen Now</a>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="resource-card">
                <h4>In Recovery</h4>
                <p>Weekly discussions answering questions about addiction, treatment, mental health, and recovery.</p>
                <a href="https://lemonadamedia.com/show/inrecovery/" target="_blank" class="resource-btn">Listen Now</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>Stress and mental health</h4>
                <p>Get together with different people and experts to chat about managing mental health challenges.</p>
                <a href="https://www.mentalhealth.org.uk/podcasts/stress-and-mental-health" target="_blank" class="resource-btn">Listen Now</a>
            </div>
            """, unsafe_allow_html=True)

    with tab5:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="resource-card">
                <h4>IfMe</h4>
                <p>A community encouraging people to share mental health experiences openly and safely.</p>
                <a href="https://www.if-me.org/" target="_blank" class="resource-btn">Visit Site</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>OSMI</h4>
                <p>Open Sourcing Mental Illness: A non-profit supporting mental wellness awareness in tech.</p>
                <a href="https://osmihelp.org/" target="_blank" class="resource-btn">Visit Site</a>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="resource-card">
                <h4>MHPrompt</h4>
                <p>Promotes conversations about mental health specifically within the technology industry.</p>
                <a href="https://mhprompt.org/" target="_blank" class="resource-btn">Visit Site</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="resource-card">
                <h4>SelfCare.Tech</h4>
                <p>A comprehensive collection of self-care resources specifically curated for developers.</p>
                <a href="https://selfcare.tech/" target="_blank" class="resource-btn">Visit Site</a>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------
# ACCOUNT PAGE
# ----------------------------
elif menu == "Account":

    def detect_id_type(identifier):
        identifier = identifier.strip()
        if "@" in identifier:
            return "email"
        if identifier.isdigit() and len(identifier) >= 10:
            return "phone"
        return "unknown"

    import base64
    import os
    # Fix: Get absolute path to the data folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bg_img_path = os.path.join(base_dir, "data", "login_bg.png")
    bg_b64 = ""
    if os.path.exists(bg_img_path):
        with open(bg_img_path, "rb") as f:
            bg_b64 = base64.b64encode(f.read()).decode()

    # This CSS is only for Account page. It removes the blank top space and
    # avoids raw HTML blocks, so nothing like <div class=...> appears on screen.
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Inter:wght@400;600&display=swap');

    [data-testid="block-container"] {{
        max-width: 1160px !important;
        padding-top: 80px !important;
        padding-bottom: 20px !important;
        font-family: 'Inter', sans-serif;
    }}

    /* Split layout styling */
    [data-testid="stHorizontalBlock"] {{
        gap: 50px !important;
    }}

    /* No CSS-based background selectors here - backgrounds are inline on the HTML divs */

    /* Force left panel heading colors */
    .left-panel-heading {{ color: #ffffff !important; }}
    .left-panel-heading .wellness-word {{ color: #67e8f9 !important; }}

    .signin-title {{
        font-family: 'Outfit', sans-serif;
        color: #0f172a !important;
        font-size: 38px !important;
        font-weight: 800 !important;
        margin-bottom: 6px !important;
    }}





    .signin-subtitle {{
        color: #64748b !important;
        font-size: 14px !important;
        margin-bottom: 25px !important;
    }}

    .auth-tab .stRadio > div[role="radiogroup"] {{
        background: #f1f5f9;
        padding: 4px;
        border-radius: 12px;
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 4px !important;
        margin-bottom: 20px !important;
    }}

    .auth-tab .stRadio label {{
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px !important;
        text-align: center !important;
    }}

    .auth-tab .stRadio label[data-checked="true"] {{
        background: #ffffff !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }}

    .auth-form .stTextInput input {{
        height: 50px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background: #f8fafc !important;
    }}

    .auth-form .stButton>button {{
        height: 50px !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        font-family: 'Outfit', sans-serif;
    }}

    .auth-form .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        color: white !important;
    }}

    .auth-form .stButton>button[kind="tertiary"] {{
        background: transparent !important;
        color: #0ea5e9 !important;
        box-shadow: none !important;
        border: none !important;
        height: 28px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        padding: 0 !important;
        margin-top: 6px !important;
    }}

    .auth-form .stButton>button[kind="tertiary"]:hover {{
        color: #0284c7 !important;
        text-decoration: underline !important;
        transform: none !important;
    }}

    .or-line-clean {{
        display: flex;
        align-items: center;
        gap: 12px;
        color: #94a3b8;
        font-size: 13px;
        margin: 15px 0;
    }}

    .or-line-clean::before, .or-line-clean::after {{
        content: ""; flex: 1; height: 1px; background: #f1f5f9;
    }}
    </style>
    """, unsafe_allow_html=True)




    if st.session_state.logged_in:
        # ── LOGGED-IN DASHBOARD ───────────────────────────────────
        st.markdown("<h1 style='color:#0ea5e9 !important;margin-bottom:6px'>👤 Your Account</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#64748b;font-size:16px'>Signed in as <b>{st.session_state.username}</b></p>", unsafe_allow_html=True)
        st.markdown("<hr style='border:none;border-top:1px solid rgba(14,165,233,.15);margin:22px 0;'>", unsafe_allow_html=True)

        dashboard_data = get_dashboard_data(st.session_state.username)
        st.session_state.streak = dashboard_data.get("streak", st.session_state.streak)
        st.session_state.session_exercises_done = dashboard_data.get("therapy_sessions_today", st.session_state.session_exercises_done)

        c1, c2 = st.columns(2)
        streak = st.session_state.streak
        streak_word = "Day" if streak == 1 else "Days"
        session_count = st.session_state.session_exercises_done
        for col, icon, label, val, sub in [
            (c1, "🔥", "Self-Care Streak", f"{streak} {streak_word} Streak", "You showed up today 💙"),
            (c2, "✨", "Therapy Sessions Today", f"{session_count} completed today", "Completed therapy sessions are counted here"),
        ]:
            with col:
                st.markdown(f"""
                <div class='grid-card' style='padding:26px 20px; min-height:170px'>
                    <div style='font-size:38px'>{icon}</div>
                    <h3 style='font-size:20px !important;margin:8px 0 4px'>{label}</h3>
                    <p style='font-size:24px !important;font-weight:900;color:#0ea5e9'>{val}</p>
                    <p style='font-size:14px !important;color:#64748b'>{sub}</p>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        _, mid, _ = st.columns([2, 1, 2])
        with mid:
            if st.button("🚪 Logout", key="acct_logout_btn", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.streak = 0
                st.session_state.current_page = "Analyze"
                st.rerun()

        # ── Mood History (from DB, uses saved consent data) ──────────────
        user_doc = get_user(st.session_state.username)
        mood_history = (user_doc or {}).get("mood_history", [])
        if mood_history:
            st.markdown("<hr style='border:none;border-top:1px solid rgba(14,165,233,.15);margin:28px 0;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#0ea5e9 !important;'>📅 Your Mood History</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:#64748b;font-size:14px;'>Entries are only saved when you give consent on the Analyze page.</p>", unsafe_allow_html=True)
            # Show last 10 entries in reverse order
            for entry in reversed(mood_history[-10:]):
                pred_color = {
                    "Depression": "#ef4444",
                    "Stress": "#f59e0b",
                    "Anxiety": "#8b5cf6",
                    "Normal": "#10b981",
                }.get(entry.get("prediction", ""), "#64748b")
                thought_snippet = entry.get("thought_text", "")
                thought_html = f"<br><span style='font-size:13px;color:#64748b;font-style:italic;'>\"{thought_snippet[:120]}{'...' if len(thought_snippet) > 120 else ''}\"</span>" if thought_snippet else ""
                score_html = f" &nbsp;·&nbsp; Score: {entry.get('questionnaire_score', 0):.0f}%" if entry.get("questionnaire_score") else ""
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.85);border-left:4px solid {pred_color};border-radius:12px;
                            padding:14px 18px;margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,0.05);'>
                    <span style='font-weight:800;color:{pred_color};font-size:16px;'>{entry.get('prediction','?')}</span>
                    &nbsp;·&nbsp; <span style='color:#94a3b8;font-size:14px;'>{entry.get('mood_label','')}</span>{score_html}
                    &nbsp;·&nbsp; <span style='color:#cbd5e1;font-size:13px;'>{entry.get('date','')}</span>
                    {thought_html}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<hr style='border:none;border-top:1px solid rgba(14,165,233,.15);margin:28px 0;'>", unsafe_allow_html=True)
            st.info("📝 No saved mood history yet. Enable consent on the Analyze page to start tracking your emotional journey.")

    else:
        # ── GUEST: CLEAN SIGN-IN / SIGN-UP PAGE ─────────────────────
        left_col, right_col = st.columns([1, 1], gap="large")


        with left_col:
            left_bg_style = (
                f"background-image: linear-gradient(rgba(15,23,42,0.62), rgba(15,23,42,0.62)), url(data:image/png;base64,{bg_b64});"
                if bg_b64 else
                "background: linear-gradient(135deg, #0f172a, #1e293b, #0ea5e9);"
            )
            st.markdown(f"""
<div style="
    {left_bg_style}
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-color: #0f172a;
    padding: 50px 40px;
    border-radius: 24px;
    min-height: 580px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.1);
    font-family: 'Inter', sans-serif;
">
    <h1 class="left-panel-heading" style="font-family:'Outfit',sans-serif; font-weight:900; font-size:42px; line-height:1.15; margin-bottom:18px;">
        Your personal<br>
        <span class="wellness-word">mental wellness</span><br>
        companion
    </h1>
    <p style="color:rgba(255,255,255,0.85); font-size:16px; line-height:1.7; margin-bottom:36px;">
        Understand your emotions, build healthy habits, and take small steps toward a calmer mind.
    </p>
    <div style="color:#ffffff; font-size:16px; font-weight:700; padding:10px 0; display:flex; align-items:center; gap:10px; margin-bottom:10px;">😊 &nbsp;Mood Tracking</div>
    <div style="color:#ffffff; font-size:16px; font-weight:700; padding:10px 0; display:flex; align-items:center; gap:10px; margin-bottom:10px;">🪷 &nbsp;Guided Therapy</div>
    <div style="color:#ffffff; font-size:16px; font-weight:700; padding:10px 0; display:flex; align-items:center; gap:10px; margin-bottom:10px;">🔥 &nbsp;Self-care Streaks</div>
    <div style="color:#ffffff; font-size:16px; font-weight:700; padding:10px 0; display:flex; align-items:center; gap:10px; margin-bottom:10px;">✨ &nbsp;AI-Powered Support</div>
    <div style="margin-top:28px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.15); color:rgba(255,255,255,0.7); font-size:14px; font-weight:500;">
        🔒 &nbsp;<b style="color:rgba(255,255,255,0.9);">Your privacy is our priority.</b><br>
        Your private thoughts are secure and confidential.
    </div>
</div>
""", unsafe_allow_html=True)


        with right_col:
            st.markdown("<div class='account-right-marker'></div>", unsafe_allow_html=True)
            if "show_reset_password" not in st.session_state:
                st.session_state.show_reset_password = False

            if st.session_state.show_reset_password:
                # ── RESET PASSWORD VIEW ──────────────────────────────────
                st.markdown("<h1 class='signin-title'>Reset Password</h1>", unsafe_allow_html=True)
                st.markdown("<p class='signin-subtitle'>Enter your account identifier and a new password to reset it.</p>", unsafe_allow_html=True)

                identifier = st.text_input(
                    "Email or Phone Number",
                    placeholder="Email or phone number",
                    key="acct_reset_identifier"
                )
                new_password = st.text_input(
                    "New Password",
                    type="password",
                    placeholder="New password",
                    key="acct_reset_password"
                )
                confirm_pw = st.text_input(
                    "Confirm New Password",
                    type="password",
                    placeholder="Confirm new password",
                    key="acct_reset_confirm_pw"
                )

                if st.button("Reset Password", key="acct_reset_btn", use_container_width=True, type="primary"):
                    if identifier and new_password and confirm_pw:
                        if len(new_password) < 6:
                            st.error("Password must be at least 6 characters.")
                        elif new_password != confirm_pw:
                            st.error("Passwords do not match.")
                        else:
                            res = reset_password(identifier.strip(), new_password)
                            if res["success"]:
                                st.success("✅ Password reset successfully! You can now sign in.")
                            else:
                                st.error(res["error"])
                    else:
                        st.warning("Please fill in all fields.")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("⬅ Back to Login", key="acct_back_login_btn", use_container_width=True, type="secondary"):
                    st.session_state.show_reset_password = False
                    st.rerun()
            else:
                st.markdown("<div class='auth-form'>", unsafe_allow_html=True)
                st.markdown("<div class='auth-tab'>", unsafe_allow_html=True)
                acct_tab = st.radio(
                    "Choose account action",
                    ["Sign In", "Sign Up"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="acct_tab_sel"
                )
                st.markdown("</div>", unsafe_allow_html=True)

                if acct_tab == "Sign In":
                    st.markdown("<h1 class='signin-title'>Sign in</h1>", unsafe_allow_html=True)
                    st.markdown("<p class='signin-subtitle'>Login only if you want to save your progress.</p>", unsafe_allow_html=True)

                    identifier = st.text_input(
                        "Email or Phone Number",
                        placeholder="Email or phone number",
                        key="acct_login_identifier"
                    )
                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Password",
                        key="acct_login_password"
                    )

                    remember_me = st.checkbox("Remember me", key="acct_remember_me", value=True)

                    if st.button("Sign in", key="acct_login_btn", use_container_width=True, type="primary"):
                        if identifier:
                            login_pw = password
                            if not login_pw:
                                # Try to auto-login using remembered password
                                saved_pw = get_remembered_password(identifier.strip())
                                if saved_pw:
                                    login_pw = saved_pw

                            if login_pw:
                                res = login_user(identifier.strip(), login_pw)
                                if res["success"]:
                                    st.session_state.logged_in = True
                                    st.session_state.username = identifier.strip()
                                    st.session_state.streak = res["user"].get("streak", 0)
                                    # Save or clear remembered password
                                    if remember_me:
                                        save_remembered_user(identifier.strip(), login_pw)
                                    else:
                                        clear_remembered_user(identifier.strip())
                                    st.success("✅ Welcome back!")
                                    st.rerun()
                                else:
                                    st.error(res["error"])
                            else:
                                st.warning("Please enter your password.")
                        else:
                            st.warning("Please enter your email/phone.")

                    # Simple text-style forgot-password option below Sign in.
                    cols = st.columns([1, 1, 1])
                    with cols[1]:
                        if st.button("Forgot Password?", key="acct_forgot_btn", type="tertiary", use_container_width=True):
                            st.session_state.show_reset_password = True
                            st.rerun()

                    st.markdown("<div class='or-line-clean'>or</div>", unsafe_allow_html=True)

                    if st.button("Continue as Guest", key="acct_guest_cta_login", use_container_width=True, type="secondary"):
                        st.session_state.current_page = "Analyze"
                        st.rerun()

                    st.markdown("<p style='text-align:center;color:#64748b;font-size:13px;'>Don’t have an account? Select <b>Sign Up</b> above.</p>", unsafe_allow_html=True)

                elif acct_tab == "Sign Up":
                    st.markdown("<h1 class='signin-title'>Sign up</h1>", unsafe_allow_html=True)
                    st.markdown("<p class='signin-subtitle'>Create an optional account to save streaks, mood history and therapy progress.</p>", unsafe_allow_html=True)

                    identifier = st.text_input(
                        "Email or Phone Number",
                        placeholder="Email or phone number",
                        key="acct_signup_identifier"
                    )
                    password = st.text_input(
                        "Create Password",
                        type="password",
                        placeholder="Create password",
                        key="acct_signup_password"
                    )
                    confirm_pw = st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="Confirm password",
                        key="acct_signup_confirm_pw"
                    )

                    if st.button("Sign up", key="acct_signup_btn", use_container_width=True, type="primary"):
                        if identifier and password and confirm_pw:
                            id_type = detect_id_type(identifier)
                            if id_type == "unknown":
                                st.error("Please enter a valid email or phone number.")
                            elif len(password) < 6:
                                st.error("Password must be at least 6 characters.")
                            elif password != confirm_pw:
                                st.error("Passwords do not match.")
                            else:
                                res = register_user(identifier.strip(), password, id_type=id_type)
                                if res["success"]:
                                    st.success("🎉 Account created! Now select Sign In to login.")
                                else:
                                    st.error(res["error"])
                        else:
                            st.warning("Please fill in all fields.")

                    st.markdown("<div class='or-line-clean'>or</div>", unsafe_allow_html=True)
                    if st.button("Continue as Guest", key="acct_guest_cta_signup", use_container_width=True, type="secondary"):
                        st.session_state.current_page = "Analyze"
                        st.rerun()

                    st.markdown("<p style='text-align:center;color:#64748b;font-size:13px;'>Already have an account? Select <b>Sign In</b> above.</p>", unsafe_allow_html=True)


            st.markdown("""
            <div class="security-note-clean">
                <span style="color:#10b981;font-weight:900;">✔</span> Passwords are securely hashed.<br>
                Your private thoughts are not saved unless you give consent.
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

