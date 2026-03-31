import gradio as gr
import sys
sys.path.append("../cli")

from predict_mental_health import predict_mental_health

def analyze(text):

    condition, advice = predict_mental_health(text)

    return f"""
Mental Health Condition: {condition}

Advice:
{advice}
"""

interface = gr.Interface(
    fn=analyze,
    inputs="textbox",
    outputs="text",
    title="Mental Health Analysis Tool",
    description="Enter a statement to analyze mental health."
)

interface.launch()