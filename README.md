## 📖 Introduction
This project is an AI-powered mental health analysis system designed to understand and interpret user statements. It uses Machine Learning and Natural Language Processing (NLP) to classify mental health conditions and provide meaningful support.
The system predicts the mental health category of user input, performs sentiment analysis, explains predictions, generates AI-based advice, and includes data analysis (EDA) along with a resource section for mental well-being.

## 🎯 Purpose of the Project
The goal of this project is to assist in the early identification of mental health conditions based on text input. It demonstrates how AI, ML, and data analysis can be combined to build a helpful and user-friendly application.

## ⚙️ How the System Works
1. User enters a statement  
2. ML model predicts mental health category (Depression, Anxiety, Stress, Normal, etc.)  
3. Sentiment analysis determines emotional tone  
4. LIME explains predictions  
5. AI generates personalized advice  
6. Resources section provides additional support  

## 🚀 Features
- 🧠 Mental health prediction using ML model  
- 📊 Sentiment analysis using VADER  
- 🔍 Model explainability using LIME  
- 🤖 AI-generated mental health advice  
- 📈 Interactive Streamlit dashboard  
- 💻 Command Line Interface (CLI) support  
- 📊 Exploratory Data Analysis (EDA) with visual insights  
- 📚 Resource section with apps, articles, and calming techniques  
- ⚠️ Early warning system  

## 🛠️ Technologies Used

- Python  
- Streamlit  
- Scikit-learn  
- Pandas  
- VADER Sentiment Analyzer  
- LIME  
- Groq API  

## 📂 Project Structure
MIND MESH/
│
├── data/ # Dataset and assets
├── models/ # Trained ML model
├── src/ # Core logic (ML, sentiment, AI, EDA)
├── ui/ # Streamlit dashboard
├── cli/ # Command line interface
├── mentalhealth.ipynb/ # EDA 
└── README.md

## ⚙️ Setup Instructions

To run this project on your system, follow these steps:
* First, install all required dependencies:
```
  pip install -r requirements.txt
```
* Next, set your Groq API key as an environment variable:
 For Windows PowerShell:
```
$env:GROQ_API_KEY="your_api_key_here"
```
## 🧪 Training the Model

To train the machine learning model, navigate to the `src` folder and run:
```
cd src
python train_model.py
```
This will train the model and save it inside the `models` folder.

## ▶️ Running the Application

To launch the Streamlit dashboard, go to the `ui` folder and run:
```
cd ui
python -m streamlit run streamlit_dashboard.py
```
Once the server starts, open your browser and visit: http://localhost:8501

## 🤖 Testing AI Advice (Optional)
To test the AI-based advice generation separately:
```
cd src
python test_groq.py
```
## 💻 Command Line Interface (CLI)

Run the model directly from terminal:
```
cd cli
python predict_mental_health.py "I feel very stressed and anxious"
```
**Example Output**
Predicted Mental Health Condition: Anxiety
Suggested Coping Mechanism: Try deep breathing, meditation, or journaling.

## 📚 Resources Section
The application includes a dedicated **Resources section** to support mental well-being.

It provides:

- 📱 Apps
- 📄 Articles on stress and burnout  
- 📚 Books on mental wellness  
- 🎧 Podcasts  
- 🏢 Mental health organizations  

These resources offer techniques to **calm the mind, reduce anxiety, and improve overall well-being**.

## 🤖 Test AI Advice (Optional)
```
cd src
python test_groq.py
```
## 📊 Dataset

Dataset sourced from Kaggle with labeled mental health statements such as Depression, Anxiety, Stress, and Normal.
Dataset used : https://www.kaggle.com/datasets/suchintikasarkar/sentiment-analysis-for-mental-health

## 📈 Model Performance
- Accuracy: ~76%  
- Performs well on common categories  
- Can be improved for less frequent classes  

## ⚠️ Disclaimer

This project is for educational purposes only and is not a substitute for professional medical advice. Please consult a healthcare professional if needed.

## 🔮 Future Scope

- Use advanced NLP models like BERT  
- Add multilingual support  
- Deploy as a web application   
- Add real-time monitoring  
