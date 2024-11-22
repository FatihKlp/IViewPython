import os
import requests

def download_video_by_signed_url(signed_url, video_id):
    video_path = os.path.join("/tmp/videos", video_id)  # Geçici video dosya yolu

    try:
        # Gelen URL ve video_id bilgilerini yazdır
        print(f"Downloading video with ID: {video_id}")
        print(f"Signed URL: {signed_url}")
        
        response = requests.get(signed_url, stream=True)
        response.raise_for_status()  # HTTP hatalarını yakalamak için

        os.makedirs("/tmp/videos", exist_ok=True)
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
