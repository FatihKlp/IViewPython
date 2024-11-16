import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from utils.s3_handler import download_video_by_id
from video_processing.transcriber import transcribe_video
from video_processing.face_analyzer import analyze_faces
from config import BACKEND_URL

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}}, supports_credentials=True)

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
        # Video indirme
        video_path = download_video_by_id(video_id)
        if not video_path:
            print(f"Failed to download video with ID: {video_id}")
            return jsonify({"error": "Video not found"}), 404

        print(f"Video downloaded successfully: {video_path}")

        # 1. Transcription İşlemi
        transcription_path = transcribe_video(video_path, video_id)
        if not transcription_path:
            print("Failed to transcribe video")
            return jsonify({"error": "Failed to transcribe video"}), 500

        print(f"Transcription saved at: {transcription_path}")

        with open(transcription_path, "r", encoding="utf-8") as file:
            transcription_data = json.load(file)

        full_transcription = transcription_data.get("full_transcription", "")

        # 2. Face Analysis İşlemi
        face_analysis_path = analyze_faces(video_path, video_id)
        if not face_analysis_path:
            print("Failed to analyze faces")
            return jsonify({"error": "Failed to analyze faces"}), 500

        print(f"Face analysis saved at: {face_analysis_path}")

        with open(face_analysis_path, "r", encoding="utf-8") as file:
            face_analysis_data = json.load(file)

        # 3. Backend'e Gönderim
        payload = {
            "transcription": full_transcription,
            "face_analysis": {
                "age": face_analysis_data.get("average_age"),
                "gender": face_analysis_data.get("dominant_gender"),
                "race": face_analysis_data.get("dominant_race"),
                "emotion": face_analysis_data.get("dominant_emotion")
            }
        }

        response = requests.put(
            f"{BACKEND_URL}/api/candidates/{candidate_id}/result",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Backend response: {response.status_code}, {response.json()}")  # Debug için eklendi
        response.raise_for_status()

        print(f"Data successfully sent to backend for candidate {candidate_id}")
        return jsonify({"message": "Processing completed and sent to backend"})

    except requests.exceptions.RequestException as e:
        print(f"Failed to send data to backend: {e}")
        return jsonify({"error": "Failed to send data to backend", "details": str(e)}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Temporary file deleted: {video_path}")

if __name__ == '__main__':
    app.run(debug=True)