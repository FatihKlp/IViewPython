import os
import requests
from config import VIDEO_API_LINK, VIDEO_API_PROJECT, VIDEO_API_BUCKET, VIDEO_FOLDER

def download_video_by_id(video_id):
    video_api_url = f"{VIDEO_API_LINK}/uploads/{VIDEO_API_PROJECT}/{VIDEO_API_BUCKET}/{video_id}"
    video_path = os.path.join(VIDEO_FOLDER, video_id)  # Dosya adı olarak video_id kullanıyoruz

    try:
        # Gelen URL ve video_id bilgilerini yazdır
        print(f"Downloading video with ID: {video_id}")
        print(f"Generated video URL: {video_api_url}")
        
        response = requests.get(video_api_url, stream=True)
        response.raise_for_status()  # HTTP hatalarını yakalamak için

        os.makedirs(VIDEO_FOLDER, exist_ok=True)
        with open(video_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):  # 8KB'lık daha büyük parçalar
                if chunk:
                    file.write(chunk)

        if os.path.getsize(video_path) > 0:
            print(f"Video successfully downloaded to: {video_path}")
            return video_path
        else:
            print("Downloaded file is empty.")
            os.remove(video_path)  # Boş dosyayı sil
            return None

    except requests.exceptions.RequestException as e:
        print(f"Failed to download video: {e}")
        return None