from pydub import AudioSegment
from pydub.effects import normalize
import subprocess
import speech_recognition as sr
import os
import json

# FFmpeg'in bulunduğu yolu ekleyin
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

def transcribe_video(video_path, video_id):
    """
    Videodan ses çıkarır, gürültüyü azaltır ve Türkçe metin döker.
    """
    try:
        # Kayıt dizinini oluştur
        os.makedirs("transcriptions", exist_ok=True)

        # Ses dosyasını çıkar
        raw_audio_path = f"transcriptions/{video_id}_raw_audio.wav"
        processed_audio_path = f"transcriptions/{video_id}_processed_audio.wav"

        # FFmpeg ile ses çıkarma
        command = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", raw_audio_path
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Pydub ile normalize edilmiş ve gürültü azaltılmış ses
        audio = AudioSegment.from_file(raw_audio_path, format="wav")
        audio = normalize(audio)  # Ses seviyesini normalize et
        audio.export(processed_audio_path, format="wav")

        # SpeechRecognition ile ses dosyasını işleme
        recognizer = sr.Recognizer()
        transcription_segments = []
        full_transcription = ""

        with sr.AudioFile(processed_audio_path) as source:
            total_duration = int(source.DURATION)
            print(f"Audio duration: {total_duration} seconds")
            if total_duration == 0:
                print("No audio detected in the video.")
                return None

            # 30 saniyelik segmentlerle işle
            for offset in range(0, total_duration, 30):
                print(f"Processing segment starting at {offset}s...")
                try:
                    audio_data = recognizer.record(source, duration=30)
                    text = recognizer.recognize_google(audio_data, language="tr-TR")
                    transcription_segments.append({"start": offset, "text": text})
                    full_transcription += f"{text} "  # Segmenti birleştir
                except sr.UnknownValueError:
                    print(f"Could not understand audio at segment starting at {offset}s.")
                    transcription_segments.append({"start": offset, "text": None})
                except sr.RequestError as e:
                    print(f"API request failed: {e}")
                    transcription_segments.append({"start": offset, "text": None})

        # Birleştirilmiş ve segmentli metni JSON olarak kaydet
        transcription_path = f"transcriptions/{video_id}_transcription.json"
        with open(transcription_path, "w", encoding="utf-8") as file:
            json.dump({
                "segments": transcription_segments,
                "full_transcription": full_transcription.strip()
            }, file, ensure_ascii=False, indent=4)

        print(f"Transcription saved to {transcription_path}")
        
        # Cleanup temporary audio files
        os.remove(raw_audio_path)
        os.remove(processed_audio_path)
        
        return transcription_path

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error in transcription: {e}")
        return None
    finally:
        import gc
        gc.collect()  # Gereksiz belleği temizler