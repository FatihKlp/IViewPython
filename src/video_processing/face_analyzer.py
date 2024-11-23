import cv2
import os
import numpy as np
from deepface import DeepFace
from collections import Counter

def extract_frames(video_path, output_folder="frames", interval_seconds=20):
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
    try:
        analysis_folder = f"face_analysis/{video_id}"
        os.makedirs(analysis_folder, exist_ok=True)

        frames_folder = os.path.join(analysis_folder, "frames")
        frames = extract_frames(video_path, output_folder=frames_folder, interval_seconds=interval_seconds)

        aggregated_results = {
            "age": [],
            "gender": []
        }

        for frame in frames:
            try:
                analysis = DeepFace.analyze(
                    img_path=frame, actions=['age', 'gender'], enforce_detection=False
                )
                if isinstance(analysis, list):
                    analysis = analysis[0]

                aggregated_results["age"].append(analysis.get("age", None))
                aggregated_results["gender"].append(analysis.get("dominant_gender", None))

            except Exception as e:
                print(f"Error analyzing frame {frame}: {e}")

        if not aggregated_results["age"]:
            print("No faces detected.")
            return {"average_age": None, "dominant_gender": None}

        return {
            "average_age": np.mean([x for x in aggregated_results["age"] if x]),
            "dominant_gender": Counter(aggregated_results["gender"]).most_common(1)[0][0] if aggregated_results["gender"] else None
        }

    except Exception as e:
        print(f"Error in face analysis: {e}")
        return {"average_age": None, "dominant_gender": None}
