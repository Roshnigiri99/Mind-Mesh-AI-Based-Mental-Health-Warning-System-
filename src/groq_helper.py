#groq_helper.py
import os
from openai import OpenAI

# read the key
api_key = os.environ["GROQ_API_KEY"]

# create Groq client
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

def generate_advice(statement, mood_history=None):
    """
    Generate personalised mental health advice.
    mood_history: optional list of past mood entry dicts from MongoDB
                  (keys: date, mood_label, prediction, thought_text)
    """

    # Build mood history context string if available
    history_context = ""
    if mood_history:
        recent = mood_history[-5:]  # use last 5 entries
        lines = []
        for entry in reversed(recent):  # newest first
            date = entry.get("date", "")
            pred = entry.get("prediction", "")
            mood = entry.get("mood_label", "")
            thought = entry.get("thought_text", "").strip()
            if thought:
                lines.append(
                    f"- {date}: felt {mood} (predicted: {pred}) — wrote: \"{thought[:120]}\""
                )
            else:
                lines.append(f"- {date}: felt {mood} (predicted: {pred})")
        if lines:
            history_context = (
                "\n\nThis user has previously shared their emotional history:\n"
                + "\n".join(lines)
                + "\n\nUse this pattern to give more personalised, empathetic advice "
                  "that acknowledges their ongoing journey."
            )

    prompt = f"""You are a compassionate and professional mental health support assistant.

A user said: {statement}{history_context}

Provide comprehensive, warm, and helpful mental health coping advice. 
Be empathetic, acknowledge their feelings, and give detailed guidance.
IMPORTANT: Do NOT provide step-by-step instructions for breathing exercises or grounding exercises (like 5-4-3-2-1). We will provide interactive widgets for these below your advice, so just give conversational advice without describing those specific exercises to avoid repetition.
Do not diagnose. Speak directly to the user as "you".
"""

    response = client.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt
    )

    return response.output_text
