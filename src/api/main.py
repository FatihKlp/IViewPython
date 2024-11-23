import sys
import os
import json
import tensorflow as tf

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from utils.s3_handler import download_video_by_signed_url
from video_processing.transcriber import transcribe_video
from video_processing.face_analyzer import analyze_faces
from config import BACKEND_URL, FRONTEND_URL, PORT

# GPU kullanılabilirliğini kontrol et
print("Available GPUs:", tf.config.list_physical_devices('GPU'))

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [FRONTEND_URL]}}, supports_credentials=True)

def initialize_folder_structure(base_path="/tmp/.deepface"):
    required_dirs = ["weights"]
    for folder in required_dirs:
        full_path = os.path.join(base_path, folder)
        os.makedirs(full_path, exist_ok=True)

initialize_folder_structure()

@app.route('/process_video', methods=['POST'])
def process_video():
    signed_url = request.json.get('signed_url')
    candidate_id = request.json.get('candidate_id')

    if not signed_url or not candidate_id:
        print("Error: Missing signed_url or candidate_id")
        return jsonify({"error": "signed_url and candidate_id are required"}), 400

    print(f"Received signed_url: {signed_url}")
    print(f"Received candidate_id: {candidate_id}")

    transcription_path = None
    face_analysis_result = None

    try:
        # Video indirme
        video_id = signed_url.split('/')[-1].split('?')[0]
        video_path = download_video_by_signed_url(signed_url, video_id)
        if not video_path:
            print(f"Failed to download video from Signed URL: {signed_url}")
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
        face_analysis_result = analyze_faces(video_path, video_id)
        print(f"Face analysis result: {face_analysis_result}")

        # 3. Backend’e Gönderim
        payload = {
            "transcription": full_transcription,
            "face_analysis": face_analysis_result if face_analysis_result else {
                "average_age": None,
                "dominant_gender": None
            }
        }

        print(f"Payload being sent to backend: {json.dumps(payload, indent=4)}")

        response = requests.put(
            f"{BACKEND_URL}/api/candidates/{candidate_id}/result",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Backend response status code: {response.status_code}")
        print(f"Backend response content: {response.json()}")
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
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
            print(f"Temporary video file deleted: {video_path}")

        if transcription_path and os.path.exists(transcription_path):
            os.remove(transcription_path)
            print(f"Temporary transcription file deleted: {transcription_path}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, debug=True)
