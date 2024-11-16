import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.s3_handler import download_video_by_id
from video_processing.transcriber import transcribe_video
from config import BACKEND_URL

# Flask uygulamasını başlatma
app = Flask(__name__)

# CORS yapılandırması
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

        # Videodan ses çıkarıp metne çevirme işlemi
        transcription_path = transcribe_video(video_path, video_id)
        if not transcription_path:
            print("Failed to transcribe video")
            return jsonify({"error": "Failed to transcribe video"}), 500

        print(f"Transcription saved at: {transcription_path}")

        # JSON dosyasından full transcription'ı oku
        with open(transcription_path, "r", encoding="utf-8") as file:
            transcription_data = json.load(file)

        full_transcription = transcription_data.get("full_transcription", "")

        # Full transcription'ı backend'e gönder
        response = requests.put(
            f"{BACKEND_URL}/api/candidates/{candidate_id}/result",
            json={"transcription": full_transcription},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()

        print(f"Transcription successfully sent to backend for candidate {candidate_id}")
        return jsonify({"message": "Transcription completed and sent to backend"})

    except requests.exceptions.RequestException as e:
        print(f"Failed to send transcription to backend: {e}")
        return jsonify({"error": "Failed to send transcription to backend", "details": str(e)}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Temporary file deleted: {video_path}")


if __name__ == '__main__':
    app.run(debug=True)
