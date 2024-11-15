import sys
import os
import numpy as np  # Add numpy import

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from flask import Flask, request, jsonify
from utils.s3_handler import download_video_by_id
from video_processing.transcriber import transcribe_video
from video_processing.face_analyzer import analyze_faces
from config import BACKEND_URL
from flask_cors import CORS

# Flask uygulamasını başlatma
app = Flask(__name__)

# CORS yapılandırması
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}}, supports_credentials=True)

# Tüm sonuçları tutacak global değişken
all_results = {}

@app.route('/process_video', methods=['POST'])
def process_video():
    video_id = request.json.get('video_id')
    candidate_id = request.json.get('candidate_id')

    if not video_id or not candidate_id:
        print("Error: Missing video_id or candidate_id")
        return jsonify({"error": "video_id and candidate_id are required"}), 400

    print(f"Received video_id: {video_id}")
    print(f"Received candidate_id: {candidate_id}")

    try:
        video_path = download_video_by_id(video_id)
        if not video_path:
            print(f"Failed to download video with ID: {video_id}")
            return jsonify({"error": "Video not found on backend"}), 404
        
        print(f"Video downloaded successfully: {video_path}")

        # Video metne çevirme işlemi
        transcription = transcribe_video(video_path)
        if transcription is None:
            print(f"Failed to transcribe video: {video_path}")
            return jsonify({"error": "Failed to transcribe video"}), 500
        
        print(f"Transcription result: {transcription}")

        # Yüz analizi işlemi
        face_analysis = analyze_faces(video_path)
        if not face_analysis:
            print(f"Failed to analyze faces in video: {video_path}")
            return jsonify({"error": "Failed to analyze faces in video"}), 500
        
        print(f"Face analysis result: {face_analysis}")

        # Sonuçları JSON olarak hazırla
        results = {
            "transcription": transcription,
            "face_analysis": face_analysis
        }
        
        # NumPy türlerini dönüştür
        results = sanitize_for_json(results)

        # Backend'e sonuçları gönder
        backend_url = f"{BACKEND_URL}/api/candidates/{candidate_id}/result"
        response = requests.put(backend_url, json=results)
        response.raise_for_status()

        print(f"Results successfully sent to backend: {backend_url}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}")
        return jsonify({"error": "Failed to send data to backend", "details": str(req_err)}), 500
    except Exception as e:
        print(f"Error processing video: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Temporary file deleted: {video_path}")

    return jsonify({"message": "Processing completed successfully", "results": results})

if __name__ == '__main__':
    app.run(debug=True)

def sanitize_for_json(data):
    """
    Converts NumPy types to native Python types recursively.
    """
    if isinstance(data, dict):
        return {key: sanitize_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(element) for element in data]
    elif isinstance(data, (np.float32, np.float64)):
        return float(data)
    elif isinstance(data, (np.int32, np.int64)):
        return int(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    else:
        return data
