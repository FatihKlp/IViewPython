import subprocess
import speech_recognition as sr
import os

# FFmpeg'in bulunduğu yolu ekleyin
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

def transcribe_video(video_path):
    try:
        if not os.path.exists(video_path):
            print(f"Video file not found at path: {video_path}")
            return None
        
        print(f"Transcribing video at path: {video_path}")
        
        # Ses dosyasını çıkartmak için ffmpeg komutunu çalıştır
        audio_path = "temp_audio.wav"
        command = [
            "ffmpeg", "-i", video_path, 
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", audio_path
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        # Speech-to-text işlemi
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        os.remove(audio_path)
        return text
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error transcribing video: {e}")
        return None