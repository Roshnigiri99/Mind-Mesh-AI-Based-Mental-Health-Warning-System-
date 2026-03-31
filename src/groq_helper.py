import os
from openai import OpenAI

# read the key
api_key = os.environ["GROQ_API_KEY"]

# create Groq client
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

def generate_advice(statement):

    prompt = f"""
    A user said: {statement}

    Provide helpful mental health coping advice.
    """

    response = client.responses.create(
        model="openai/gpt-oss-20b",
        input=prompt
    )

    return response.output_text