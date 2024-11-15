import cv2
import os
import numpy as np
from deepface import DeepFace

def extract_frames(video_path, output_folder="frames", interval_seconds=10):
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

def analyze_faces(video_path):
    frames = extract_frames(video_path, interval_seconds=10)
    face_analysis_results = []

    for frame in frames:
        try:
            # DeepFace.analyze returns a list of dictionaries if analyzing multiple frames
            analysis = DeepFace.analyze(img_path=frame, actions=['age', 'gender', 'race', 'emotion'])

            # If the result is a list, process each entry in the list
            if isinstance(analysis, list):
                for item in analysis:
                    # `DeepFace.analyze` returns a dictionary per item, so we can sanitize the data
                    sanitized_analysis = {
                        key: (float(value) if isinstance(value, (np.float32, np.float64)) else
                              int(value) if isinstance(value, (np.int32, np.int64)) else value)
                        for key, value in item.items()
                    }
                    face_analysis_results.append({
                        "frame": frame,
                        "analysis": sanitized_analysis
                    })
            else:
                # Fallback in case analysis returns a single dictionary (unexpected)
                sanitized_analysis = {
                    key: (float(value) if isinstance(value, (np.float32, np.float64)) else
                          int(value) if isinstance(value, (np.int32, np.int64)) else value)
                    for key, value in analysis.items()
                }
                face_analysis_results.append({
                    "frame": frame,
                    "analysis": sanitized_analysis
                })
        except Exception as e:
            print(f"Error analyzing frame {frame}: {e}")

    # Clean up temporary frame files
    for frame in frames:
        os.remove(frame)

    return face_analysis_results
