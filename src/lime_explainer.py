#lime_explainer.py
import pickle
from lime.lime_text import LimeTextExplainer

model = pickle.load(open("../models/mental_health_model.pkl","rb"))

explainer = LimeTextExplainer()

def explain(text):

    def predictor(texts):
        return model.decision_function(texts)

    explanation = explainer.explain_instance(
        text,
        predictor,
        num_features=10
    )

    return explanation.as_list()
