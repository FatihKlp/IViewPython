import cv2
import os
import numpy as np
import json
from deepface import DeepFace
from collections import Counter

def extract_frames(video_path, output_folder="frames", interval_seconds=20):
    """
    Video'dan frame çıkartır.
    """
    os.makedirs(output_folder, exist_ok=True)
    vidcap = cv2.VideoCapture(video_path)
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    frame_interval = fps * interval_seconds

    frame_paths = []
    success, image = vidcap.read()
    frame_count = 0

    while success:
        if frame_count % frame_interval == 0:
            frame_path = os.path.join(output_folder, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_path, image)
            frame_paths.append(frame_path)
        success, image = vidcap.read()
        frame_count += 1

    vidcap.release()
    return frame_paths

def analyze_faces(video_path, video_id, interval_seconds=10):
    """
    Frame'leri analiz eder, tek bir kişi için ortalama sonuç döner ve JSON formatında kaydeder.
    """
    try:
        # Klasör oluştur
        analysis_folder = f"face_analysis/{video_id}"
        os.makedirs(analysis_folder, exist_ok=True)

        # Frame'leri çıkart
        frames_folder = os.path.join(analysis_folder, "frames")
        frames = extract_frames(video_path, output_folder=frames_folder, interval_seconds=interval_seconds)

        # Frame analiz sonuçları
        aggregated_results = {
            "age": [],
            "gender": [],
            "emotion": []
        }

        for frame in frames:
            if not os.path.exists(frame) or os.path.getsize(frame) == 0:
                print(f"Skipping invalid frame: {frame}")
                continue
            try:
                # DeepFace analiz
                analysis = DeepFace.analyze(img_path=frame, actions=['age', 'gender', 'emotion'])
                
                # Eğer analiz bir liste dönerse sadece ilk sonucu al
                if isinstance(analysis, list):
                    analysis = analysis[0]

                # Analiz sonuçlarını toplulaştır
                aggregated_results["age"].append(analysis["age"])
                aggregated_results["gender"].append(analysis["dominant_gender"])
                aggregated_results["emotion"].append(analysis["dominant_emotion"])

            except Exception as e:
                print(f"Error analyzing frame {frame}: {e}")

        # Sonuçları birleştir
        final_result = {
            "average_age": np.mean(aggregated_results["age"]) if aggregated_results["age"] else None,
            "dominant_gender": Counter(aggregated_results["gender"]).most_common(1)[0][0] if aggregated_results["gender"] else None,
            "dominant_emotion": Counter(aggregated_results["emotion"]).most_common(1)[0][0] if aggregated_results["emotion"] else None
        }

        # Kaydedilen dosya
        face_analysis_path = os.path.join(analysis_folder, "face_analysis.json")
        with open(face_analysis_path, "w", encoding="utf-8") as file:
            json.dump(final_result, file, ensure_ascii=False, indent=4)

        print(f"Face analysis saved to {face_analysis_path}")
        
        # Cleanup frame images
        for frame in frames:
            os.remove(frame)

        return face_analysis_path

    except Exception as e:
        print(f"Error in face analysis: {e}")
        return None
    finally:
        import gc
        gc.collect()  # Gereksiz belleği temizler