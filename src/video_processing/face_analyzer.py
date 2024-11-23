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
            "age": []
        }

        for frame in frames:
            if not os.path.exists(frame) or os.path.getsize(frame) == 0:
                print(f"Skipping invalid frame: {frame}")
                continue
            try:
                # DeepFace analiz
                analysis = DeepFace.analyze(
                    img_path=frame, actions=['age', 'gender'], enforce_detection=False
                )

                # Eğer analiz bir liste dönerse sadece ilk sonucu al
                if isinstance(analysis, list):
                    analysis = analysis[0]

                if analysis.get("age") is not None:
                    aggregated_results["age"].append(analysis["age"])

            except Exception as e:
                print(f"Error analyzing frame {frame}: {e}")

        # Eğer hiçbir yüz algılanmadıysa, uygun bir mesaj döndür
        if not aggregated_results["age"]:
            print("No faces detected in any frames.")
            return {
                "average_age": None
            }

        # Sonuçları birleştir
        final_result = {
        "average_age": np.mean(aggregated_results["age"]) if aggregated_results["age"] else None
        }

        # Kaydedilen dosya
        face_analysis_path = os.path.join(analysis_folder, "face_analysis.json")
        with open(face_analysis_path, "w", encoding="utf-8") as file:
            json.dump(final_result, file, ensure_ascii=False, indent=4)

        print(f"Face analysis saved to {face_analysis_path}")

        # Cleanup frame images
        for frame in frames:
            os.remove(frame)

        return final_result

    except Exception as e:
        print(f"Error in face analysis: {e}")
        return {
            "average_age": None
        }
    finally:
        import gc
        gc.collect()  # Gereksiz belleği temizler