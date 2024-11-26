from textblob import TextBlob

def analyze_emotion(transcription: str) -> dict:
    """
    Transkripsiyondan duygu analizi yapar.

    Args:
        transcription (str): Adayın transkripsiyonu.

    Returns:
        dict: Pozitif, nötr ve negatif duygu oranları.
    """
    blob = TextBlob(transcription)
    polarity = blob.sentiment.polarity  # -1 ile 1 arasında

    if polarity > 0.1:
        return {"positive": 1, "neutral": 0, "negative": 0}
    elif polarity < -0.1:
        return {"positive": 0, "neutral": 0, "negative": 1}
    else:
        return {"positive": 0, "neutral": 1, "negative": 0}
