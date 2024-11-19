import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from utils.s3_handler import download_video_by_id
from video_processing.transcriber import transcribe_video
from video_processing.face_analyzer import analyze_faces
from config import BACKEND_URL, FRONTEND_URL

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [FRONTEND_URL]}}, supports_credentials=True)

@app.route('/process_video', methods=['POST'])
def process_video():
    video_id = request.json.get('video_id')
    candidate_id = request.json.get('candidate_id')

    if not video_id or not candidate_id:
        return jsonify({"error": "video_id and candidate_id are required"}), 400

    try:
        # Video indirme
        video_path = download_video_by_id(video_id)
        if not video_path:
            return jsonify({"error": "Video not found"}), 404

        # 1. Transcription İşlemi
        transcription_data = transcribe_video(video_path, video_id)
        if not transcription_data:
            return jsonify({"error": "Failed to transcribe video"}), 500

        full_transcription = transcription_data.get("full_transcription", "")

        # 2. Face Analysis İşlemi
        face_analysis_data = analyze_faces(video_path, video_id)
        if not face_analysis_data:
            return jsonify({"error": "Failed to analyze faces"}), 500

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
        response.raise_for_status()

        return jsonify({"message": "Processing completed and sent to backend"})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to send data to backend", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)