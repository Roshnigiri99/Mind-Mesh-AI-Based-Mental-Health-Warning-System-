import pandas as pd
import pickle
import string

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# -------------------------------
# Load and preprocess dataset
# -------------------------------
print("Loading dataset...")
df = pd.read_csv("../data/mental_health.csv")

# Drop missing values
df = df.dropna()

# Preprocessing: lowercase + remove punctuation
def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

df["statement"] = df["statement"].apply(clean_text)

# Features and labels
X = df["statement"]
y = df["status"]

# -------------------------------
# Train-test split
# -------------------------------
print("Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y  # preserves class distribution
)

# -------------------------------
# Build pipeline with balanced SVM
# -------------------------------
print("Training model...")
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer( max_features=7000,ngram_range=(1,2),stop_words="english")),
    ("classifier", LinearSVC(class_weight='balanced'))  # important for imbalance
])


pipeline.fit(X_train, y_train)

# -------------------------------
# Evaluate model
# -------------------------------
predictions = pipeline.predict(X_test)
print("Model Evaluation")
print(classification_report(y_test, predictions))

# -------------------------------
# Save trained pipeline
# -------------------------------
with open("../models/mental_health_model.pkl", "wb") as f:
    pickle.dump(pipeline, f)

print("Model saved successfully")
