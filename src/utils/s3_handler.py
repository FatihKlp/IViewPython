from io import BytesIO
import requests
from config import VIDEO_API_LINK, VIDEO_API_PROJECT, VIDEO_API_BUCKET

def download_video_by_id(video_id):
    video_api_url = f"{VIDEO_API_LINK}/uploads/{VIDEO_API_PROJECT}/{VIDEO_API_BUCKET}/{video_id}"
    try:
        print(f"Downloading video with ID: {video_id}")
        response = requests.get(video_api_url, stream=True)
        response.raise_for_status()  # HTTP hatalarını kontrol et
        return BytesIO(response.content)  # Bellekte döndür
    except requests.exceptions.RequestException as e:
        print(f"Failed to download video: {e}")
        return None
