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
.stApp {
    background-color: #E6E6FA;
}
html, body, [class*="css"]  {
    color: #1f2937 !important;
}
.main-header {
    background: #009999;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    color: white;
    font-size: 45px;
    font-weight: bold;
    margin-bottom: 15px;
}
section[data-testid="stSidebar"] {
    background: grey;
    color: white;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
div[role="radiogroup"] > label {
    font-size: 30px !important;
    font-weight: 900;
    padding: 10px;
    border-radius: 10px;
}
div[role="radiogroup"] > label:hover {
    background-color: #00CC00;
}
.stButton>button {
    background: black;
    color: white;
    border-radius: 10px;
    height: 50px;
    width: 100%;
    font-size: 30px;
    font-weight: bold;
    border: none;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #ff6600;
    color: white;
}
textarea {
    border-radius: 20px !important;
    border: 1px solid #ccc !important;
    font-size: 18px !important;
}
label[for^="textarea"] {
    font-size: 28px !important;
    color: #006666 !important;
    font-weight: bold;
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
st.sidebar.image(LOGO_PATH, width=140)
st.sidebar.markdown("## 🧠 MIND MESH")
menu = st.sidebar.radio("Navigation", ["Analyze", "About", "Resources"])

# ----------------------------
# HEADER
# ----------------------------
st.markdown("""
<div class="main-header">
🧠 MIND MESH: AI-Based Mental Health Warning System
</div>
""", unsafe_allow_html=True)

# ----------------------------
# ANALYZE PAGE
# ----------------------------
if menu == "Analyze":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📝 Enter Your Thoughts </h3>", unsafe_allow_html=True)
    text = st.text_area("", height=300)
    analyze_btn = st.button("🔍 Analyze Mental State")
    st.markdown('</div>', unsafe_allow_html=True)

    if analyze_btn:
        if text.strip() == "":
            st.warning("Please enter a statement")
        else:
            with st.spinner("Analyzing your mental state..."):
                prediction = model.predict([text])[0]

                # Prediction section (compact horizontal layout)
                st.markdown('<div class="card">', unsafe_allow_html=True)
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

                st.markdown('</div>', unsafe_allow_html=True)

                # AI Advice section stacked below
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("🤖 AI Advice")
                try:
                    advice = generate_advice(text)
                    st.info(advice)
                except:
                    st.error("AI advice unavailable")
                st.markdown('</div>', unsafe_allow_html=True)

    # Dataset preview
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Dataset Preview")
    st.dataframe(df.head())
    st.markdown('</div>', unsafe_allow_html=True)

    # Distribution chart
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Mental Health Distribution")
    st.bar_chart(df["status"].value_counts())
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# ABOUT PAGE
# ----------------------------
elif menu == "About":
    st.title("📖 About Mind Mesh")
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=120)
        st.markdown("### 🤖 AI-Powered System\nUses ML to analyze mental health patterns.")
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2913/2913465.png", width=120)
        st.markdown("### 💡 Smart Insights\nProvides intelligent suggestions.")
    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/3209/3209265.png", width=120)
        st.markdown("### 🌍 Awareness\nPromotes early detection.")
    with col4:
        st.image("https://cdn-icons-png.flaticon.com/512/2966/2966483.png", width=120)
        st.markdown("### ⚠️ Disclaimer\nNot a replacement for professional advice.")

# ----------------------------
# RESOURCES PAGE
# ----------------------------
elif menu == "Resources":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📚 Mental Health Resources")

    # ---------------- APPS ----------------
    st.subheader("📱 Applications")
    with st.expander("View Apps"):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
🔹 **[Calm](https://www.calm.com)**  
Provides guided meditations, sleep stories, and breathing exercises to help reduce anxiety and improve sleep quality.
""")

            st.markdown("""
🔹 **[Wysa](https://www.wysa.com)**  
An AI-powered chatbot that uses evidence-based techniques like CBT and mindfulness to support users in managing stress, anxiety, and depression.
""")

            st.markdown("""
🔹 **[Sanvello](https://www.sanvello.com)**  
Provides daily tools to manage stress, anxiety, and depression using CBT, mindfulness, and mood tracking.
""")
            st.markdown("""
🔹 **[Cope Notes](https://copenotes.com/)**  
Sends daily text messages with positive thoughts, exercises, and journaling prompts to help combat depression and anxiety. Content is reviewed by mental health professionals.
""")

        with col2:
            st.markdown("""
🔹 **[Headspace](https://www.headspace.com)**  
A meditation and mindfulness app offering guided sessions, sleep aids, and stress-reduction techniques.
""")

            st.markdown("""
🔹 **[Youper](https://www.youper.ai)**  
An AI-powered emotional health assistant that guides you through conversations and activities.
""")

    # ---------------- ARTICLES ----------------
    st.subheader("📄 Articles")
    with st.expander("View Articles"):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
🔹 **[A Programmer’s Guide to Stress](https://medium.com)**  
By Daragh Byrne
""")

            st.markdown("""
🔹 **[Burnout Recovery Guide](https://medium.com)**  
Practical strategies for managing burnout.
""")

        with col2:
            st.markdown("""
🔹 **[Developer Depression](https://medium.com)**  
By Lauren Maffeo
""")

            st.markdown("""
🔹 **[It's Okay To Not Be Okay](https://dev.to/fogs/its-okay-to-not-be-okay)**  
By Andrew Montagne
""")

    # ---------------- BOOKS ----------------
    st.subheader("📚 Books")
    with st.expander("View Books"):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
🔹 **[Peopleware: Productive Projects and Teams](https://www.amazon.com/Peopleware-Productive-Projects-Teams-3rd/dp/0321934113)**  
By Tom DeMarco and Timothy Lister. Focuses on human factors in software development.
""")

            st.markdown("""
🔹 **[Slack: Getting Past Burnout, Busywork, and the Myth of Total Efficiency](https://www.amazon.com/Slack-Getting-Burnout-Busywork-Efficiency/dp/0767907698)**  
Highlights the importance of balance and avoiding overwork.
""")

        with col2:
            st.markdown("""
🔹 **[It Doesn’t Have to Be Crazy at Work](https://www.amazon.com/Doesnt-Have-Be-Crazy-Work/dp/0062874780)**  
Promotes a calm and sustainable work culture.
""")

    # ---------------- PODCASTS ----------------
    st.subheader("🎧 Podcasts")
    with st.expander("View Podcasts"):
        st.markdown("""
🔹 Mental Health in Tech  
🔹 Soft Skills Engineering  
""")

    # ---------------- ORGANIZATIONS ----------------
    st.subheader("🏢 Organizations")
    with st.expander("View Organizations"):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
🔹 **[IfMe](https://www.if-me.org/)**  
Community encouraging people to share mental health experiences.
""")

            st.markdown("""
🔹 **[OSMI](https://osmihelp.org/)**  
Non-profit supporting mental wellness awareness.
""")

        with col2:
            st.markdown("""
🔹 **[MHPrompt](https://mhprompt.org/)**  
Promotes conversations about mental health in tech.
""")

            st.markdown("""
🔹 **[SelfCare.Tech](https://selfcare.tech/)**  
Collection of self-care resources for developers.
""")

    st.markdown('</div>', unsafe_allow_html=True)
