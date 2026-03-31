# test_groq.py
import os
from groq_helper import generate_advice

# Test statement
text = "I feel anxious and stressed today"

try:
    advice = generate_advice(text)
    print("Input Statement:", text)
    print("Generated Mental Health Advice:\n", advice)
except Exception as e:
    print("Error:", e)