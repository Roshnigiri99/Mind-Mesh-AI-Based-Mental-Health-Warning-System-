import pandas as pd
import pickle
import string

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score, f1_score

# -------------------------------
# Paths
# -------------------------------
DATA_PATH = "../data/mental_health.csv"
MODEL_PATH = "../models/mental_health_model.pkl"

# -------------------------------
# Load dataset
# -------------------------------
print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

df = df.dropna()

# -------------------------------
# Clean text
# -------------------------------
def clean_text(text):
    text = str(text).lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = " ".join(text.split())
    return text

df["statement"] = df["statement"].apply(clean_text)

# -------------------------------
# Features and labels
# -------------------------------
X = df["statement"]
y = df["status"]

print("Dataset distribution:")
print(y.value_counts())

# -------------------------------
# Train-test split
# -------------------------------
print("Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# -------------------------------
# SVM Pipeline
# -------------------------------
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        stop_words="english",
        sublinear_tf=True
    )),
    ("classifier", LinearSVC(
        class_weight="balanced",
        dual="auto"
    ))
])

# -------------------------------
# Grid Search for SVM tuning
# -------------------------------
params = {
    "tfidf__max_features": [7000, 10000, 15000],
    "tfidf__ngram_range": [(1, 1), (1, 2)],
    "classifier__C": [0.1, 1.0, 10.0]
}

print("Training and tuning SVM model...")
grid = GridSearchCV(
    pipeline,
    params,
    cv=5,
    scoring="f1_weighted",
    n_jobs=-1
)

grid.fit(X_train, y_train)

best_model = grid.best_estimator_

# -------------------------------
# Evaluation
# -------------------------------
predictions = best_model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)
weighted_f1 = f1_score(y_test, predictions, average="weighted")

print("Best parameters:", grid.best_params_)
print("Accuracy:", round(accuracy, 4))
print("Weighted F1:", round(weighted_f1, 4))
print("\nClassification Report:")
print(classification_report(y_test, predictions))

# -------------------------------
# Save model only
# -------------------------------
with open(MODEL_PATH, "wb") as f:
    pickle.dump(best_model, f)

print("Model saved successfully at:", MODEL_PATH)
