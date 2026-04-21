from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import string

analyzer = SentimentIntensityAnalyzer()


def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.strip()


def analyze_sentiment(text):
    text = clean_text(text)

    score = analyzer.polarity_scores(text)["compound"]

    if score >= 0.05:
        return "Positive"

    elif score <= -0.05:
        return "Negative"

    else:
        return "Neutral"
