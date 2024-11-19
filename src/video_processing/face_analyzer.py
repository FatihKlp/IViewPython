import cv2
import numpy as np
from io import BytesIO
from deepface import DeepFace
from collections import Counter

def extract_frames(video_stream, interval_seconds=10):
    """
    Video'dan bellek içinde frame çıkarır.
    """
    vidcap = cv2.VideoCapture(video_stream)  # Bellekten video işleniyor
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    frame_interval = fps * interval_seconds
    frame_count = 0

    frames = []
    success, image = vidcap.read()

    while success:
        if frame_count % frame_interval == 0:
            frames.append(image)  # Frame bellekte saklanıyor
        success, image = vidcap.read()
        frame_count += 1

    vidcap.release()
    return frames

def analyze_faces(video_stream, interval_seconds=10):
    """
    Frame'leri analiz eder ve sonuçları JSON formatında döner.
    """
    try:
        # Frame'leri çıkar
        frames = extract_frames(video_stream, interval_seconds=interval_seconds)

        aggregated_results = {
            "age": [],
            "gender": [],
            "race": [],
            "emotion": []
        }

        for frame in frames:
            try:
                # DeepFace analiz
                analysis = DeepFace.analyze(img_path=frame, actions=['age', 'gender', 'race', 'emotion'])
                if isinstance(analysis, list):
                    analysis = analysis[0]

                aggregated_results["age"].append(analysis["age"])
                aggregated_results["gender"].append(analysis["dominant_gender"])
                aggregated_results["race"].append(analysis["dominant_race"])
                aggregated_results["emotion"].append(analysis["dominant_emotion"])
            except Exception as e:
                print(f"Error analyzing frame: {e}")

        # Toplu sonuçları döndür
        return {
            "average_age": np.mean(aggregated_results["age"]) if aggregated_results["age"] else None,
            "dominant_gender": Counter(aggregated_results["gender"]).most_common(1)[0][0] if aggregated_results["gender"] else None,
            "dominant_race": Counter(aggregated_results["race"]).most_common(1)[0][0] if aggregated_results["race"] else None,
            "dominant_emotion": Counter(aggregated_results["emotion"]).most_common(1)[0][0] if aggregated_results["emotion"] else None
        }
    except Exception as e:
        print(f"Error during face analysis: {e}")
        return None
