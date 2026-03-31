import pickle
import sys

with open("../models/mental_health_model.pkl", "rb") as f:
    model = pickle.load(f)

coping_mechanisms = {
    "Anxiety": "Try deep breathing, meditation, or journaling.",
    "Depression": "Engage in physical activities and talk to loved ones.",
    "Stress": "Practice mindfulness and take breaks.",
    "Neutral": "You're doing fine. Continue self-care."
}

def predict_mental_health(statement):

    prediction = model.predict([statement])[0]

    advice = coping_mechanisms.get(
        prediction,
        "Please consult a professional."
    )

    return prediction, advice


if __name__ == "__main__":

    if len(sys.argv) > 1:

        user_input = " ".join(sys.argv[1:])

        condition, advice = predict_mental_health(user_input)

        print("Predicted Mental Health Condition:", condition)
        print("Suggested Coping Mechanism:", advice)

    else:
        print("Usage: python predict_mental_health.py 'Your statement'")