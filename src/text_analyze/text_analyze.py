def analyze_transcription(transcription: str, context: dict) -> dict:
    """
    Transkripsiyonu analiz eder.

    Args:
        transcription (str): Adayın transkripsiyonu.
        context (dict): İş gereksinimleri ve sorular.

    Returns:
        dict: Analiz sonuçları.
    """
    from collections import Counter

    # Dinamik spaCy yüklemesi
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")  # Burada modelin yüklendiğinden emin olun
    except ImportError:
        return {"error": "spaCy is not installed."}
    except OSError:
        return {"error": "The spaCy model 'en_core_web_md' is not installed."}
    except SystemExit as e:
        return {"error": f"Unexpected SystemExit error: {str(e)}"}
    except Exception as e:
        print(f"Error occurred during analysis: {e}")
        return {"error": "Unexpected error occurred during analysis."}

    # Analiz işlemleri
    doc = nlp(transcription.lower())

    # Kelime analizleri
    word_count = len([token.text for token in doc if token.is_alpha])
    unique_words = len(set(token.text for token in doc if token.is_alpha))

    # Anahtar kelime analizi
    requirements = context.get("requirements", {})
    keyword_hits = {
        "technical": [kw for kw in requirements["keywords"]["technical"] if kw.lower() in transcription.lower()],
        "soft_skills": [kw for kw in requirements["keywords"]["softSkills"] if kw.lower() in transcription.lower()],
    }

    # Soru analizleri
    questions = context.get("questions", [])
    print(f"Processing questions: {questions}")

    question_similarity = []
    for question_data in questions:
        question_text = question_data.get("text", "")
        question_doc = nlp(question_text.lower())
        similarity = doc.similarity(question_doc)
        question_similarity.append({"question": question_text, "similarity": similarity})

    # Skor hesaplama
    total_score = (
        len(keyword_hits["technical"]) * 0.4
        + len(keyword_hits["soft_skills"]) * 0.3
        + (unique_words / max(word_count, 1)) * 0.3
    )

    from text_analyze.emotion_analyze import analyze_emotion
    # Duygu analizi ekle
    emotion_analysis = analyze_emotion(transcription)

    return {
        "word_count": word_count,
        "unique_words": unique_words,
        "keyword_hits": keyword_hits,
        "question_similarity": question_similarity,
        "total_score": round(total_score, 2),
        "emotion_analysis": emotion_analysis,
    }
