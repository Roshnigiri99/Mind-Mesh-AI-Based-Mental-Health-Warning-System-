# 🧠 Mind Mesh: AI-Based Mental Health Warning System

## 📖 Introduction
Mind Mesh is an AI-powered mental health analysis system designed to understand and interpret user statements. It uses Machine Learning and Natural Language Processing (NLP) to classify mental health conditions and provide meaningful support.

The system predicts the mental health category of user input, performs sentiment analysis, explains predictions, generates AI-based advice, and includes therapy features and a resources section for mental well-being.

---

## 🎯 Purpose of the Project
The goal of this project is to assist in the early identification of mental health conditions based on text input. It demonstrates how AI, Machine Learning, and NLP can be combined to build a helpful and user-friendly application.

---

## ⚙️ How the System Works
1. User enters a statement or selects mood  
2. ML model predicts mental health category (Depression, Stress, Anxiety, Normal)  
3. Sentiment analysis determines emotional tone  
4. Rule-based correction improves prediction accuracy  
5. AI generates personalized advice using Groq API  
6. Therapy exercises and resources are suggested  

---

## 🚀 Features

- 🧠 Mental health prediction using ML model  
- 📊 Sentiment analysis using VADER  
- 🔍 Model explainability using LIME  
- 🤖 AI-generated mental health advice  
- 🧘 Interactive therapy exercises (breathing, grounding, thought release)  
- 🔐 User authentication with MongoDB and bcrypt  
- 📈 Mood history tracking (with user consent)  
- 🎮 Self-care streak and gamification  
- 📊 Interactive Streamlit dashboard  
- 💻 Command Line Interface (CLI) support  
- 📚 Resources section for mental well-being  
- ⚠️ Early warning system  

---

## 🛠️ Technologies Used

- Python  
- Streamlit  
- Scikit-learn  
- Pandas  
- NumPy  
- VADER Sentiment Analyzer  
- LIME  
- MongoDB  
- bcrypt  
- Groq API  

---

## 📂 Project Structure

```text
MIND MESH/
│
├── cli/
│   └── predict_mental_health.py
│
├── data/
│   ├── login_bg.png
│   ├── logo.png
│   └── mental_health.csv
│
├── models/
│   └── mental_health_model.pkl
│
├── src/
│   ├── auth.py
│   ├── groq_helper.py
│   ├── lime_explainer.py
│   ├── sentiment_analysis.py
│   ├── test_groq.py
│   ├── therapy_components.py
│   └── train_model.py
│
├── ui/
│   └── streamlit_dashboard.py
│
├── .env
├── .remembered_users.json
├── mentalhealth.ipynb
├── requirements.txt
└── README.md
⚙️ Setup Instructions
1. Install Dependencies
pip install -r requirements.txt
2. Create .env File

Create a .env file in the root folder:

MONGO_URI=your_mongodb_connection_string
GROQ_API_KEY=your_groq_api_key

⚠️ Important: Do NOT upload your .env file to GitHub.

3. Train the Model
cd src
python train_model.py
4. Run the Application
cd ui
streamlit run streamlit_dashboard.py

Open in browser:

http://localhost:8501
💻 Command Line Interface (CLI)
cd cli
python predict_mental_health.py "I feel very stressed and anxious"
🤖 Test AI Advice (Optional)
cd src
python test_groq.py
📚 Resources Section

The application includes a dedicated Resources section providing:

📱 Mental health apps
📄 Articles
📚 Books
🎧 Podcasts
🏢 Organizations

These help users manage stress and improve well-being.

📊 Dataset

Dataset sourced from Kaggle:
https://www.kaggle.com/datasets/suchintikasarkar/sentiment-analysis-for-mental-health

📈 Model Performance
Accuracy: ~94%
Performs well on common categories
Can be improved for rare classes
⚠️ Disclaimer

This project is for educational purposes only and is not a substitute for professional medical advice.

🔮 Future Scope
Use advanced NLP models like BERT
Add multilingual support
Deploy as a scalable web application
Add real-time monitoring
👩‍💻 Author

Roshni Giri
