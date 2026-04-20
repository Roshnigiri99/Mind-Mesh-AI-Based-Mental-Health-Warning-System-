import streamlit as st
import pandas as pd
import pickle
import sys
import os

# ----------------------------
# PATH SETUP
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(BASE_DIR, "src")
MODEL_PATH = os.path.join(BASE_DIR, "models", "mental_health_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "mental_health.csv")
LOGO_PATH = os.path.join(BASE_DIR, "data", "logo.png")

sys.path.append(SRC_PATH)
from groq_helper import generate_advice

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Mind Mesh", layout="wide")

# ----------------------------
# 🔥 FULL UI CSS
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

/* 🚀 STYLE NATIVE HEADER AS TOP TITLE BAR */
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

/* Inject Title Text into the Native Header */
header[data-testid="stHeader"]::after {
    content: "🧠 MIND MESH: AI-Based Mental Health Warning System";
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

/* Ensure the native hamburger / expand button and close button are ALWAYS brightly visible */
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

/* Push Main Content Down */
.stApp .main .block-container {
    padding-top: 100px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    margin-top: 70px !important; /* Push below top bar */
    height: calc(100vh - 70px) !important;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important; /* Deep attractive color */
    border-right: none !important;
    box-shadow: 2px 0 15px rgba(0,0,0,0.1);
}
section[data-testid="stSidebar"] h2 {
    font-weight: 900 !important;
    font-size: 26px !important;
    color: #38bdf8 !important; /* Bright blue for dark bg */
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
    background: rgba(255, 255, 255, 0.05) !important; /* Dark theme matching */
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

/* Resource Card - More Attractive and Interactive */
.resource-card {
    background: linear-gradient(135deg, #ffffff 0%, #fdf4ff 100%); /* Soft pastel gradient */
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

/* Grid Card - More Attractive */
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

/* Tabs - Bigger and Different Font */
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

/* Button */
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

/* Labels */
.stTextArea label {
    font-size: 22px !important;
    color: #1e293b !important;
    font-weight: 800 !important;
    margin-bottom: 10px !important;
}

/* Success/Warning/Info Boxes */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

/* Animations */
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Headings in markdown */
h1, h2, h3, h4 {
    color: #1e293b !important;
    font-weight: 800 !important;
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
st.sidebar.markdown("<br>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigation", ["Analyze", "About", "Resources"], label_visibility="collapsed")

# The header title is now injected purely via CSS ::after on the native Streamlit header.

# ----------------------------
# ANALYZE PAGE
# ----------------------------
if menu == "Analyze":

    st.markdown("<h3>📝 Enter Your Thoughts </h3>", unsafe_allow_html=True)
    text = st.text_area("", height=300)
    analyze_btn = st.button("🔍 Analyze Mental State")

    if analyze_btn:
        if text.strip() == "":
            st.warning("Please enter a statement")
        else:
            with st.spinner("Analyzing your mental state..."):
                prediction = model.predict([text])[0]

                # Prediction section (compact horizontal layout)
                st.subheader("🧠 Prediction")

                col_pred1, col_pred2 = st.columns([1, 1])
                with col_pred1:
                    st.success(prediction)
                with col_pred2:
                    if hasattr(model, "decision_function"):
                        score = model.decision_function([text])
                        confidence = max(score[0])
                        st.metric("Confidence Score", round(confidence, 2))

                # Messages below prediction
                if prediction == "Depression":
                    st.warning("⚠️ You might be feeling low. Consider talking to someone you trust.")
                elif prediction == "Anxiety":
                    st.info("💡 Try breathing exercises.")
                elif prediction == "Stress":
                    st.info("🧘 Take a break and relax.")

                # AI Advice section stacked below
                st.subheader("🤖 AI Advice")
                try:
                    advice = generate_advice(text)
                    st.info(advice)
                except:
                    st.error("AI advice unavailable")

 

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

    # End of resources
