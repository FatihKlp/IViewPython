from io import BytesIO
from pydub import AudioSegment
from pydub.effects import normalize
import subprocess
import speech_recognition as sr

def transcribe_video(video_stream):
    """
    Videodan ses çıkarır, gürültüyü azaltır ve Türkçe metni döner.
    """
    try:
        # FFmpeg ile ses çıkarma
        command = [
            "ffmpeg", "-i", "pipe:0",
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "pipe:1"
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        audio_data, _ = process.communicate(input=video_stream.read())

        # Pydub ile normalize edilmiş ses
        audio = AudioSegment.from_file(BytesIO(audio_data), format="wav")
        normalized_audio = normalize(audio)

        # SpeechRecognition ile ses dosyasını işleme
        recognizer = sr.Recognizer()
        transcription_segments = []
        full_transcription = ""

        with sr.AudioFile(BytesIO(normalized_audio.raw_data)) as source:
            total_duration = int(source.DURATION)
            for offset in range(0, total_duration, 30):
                try:
                    audio_data = recognizer.record(source, duration=30)
                    text = recognizer.recognize_google(audio_data, language="tr-TR")
                    transcription_segments.append({"start": offset, "text": text})
                    full_transcription += f"{text} "
                except sr.UnknownValueError:
                    transcription_segments.append({"start": offset, "text": None})
                except sr.RequestError as e:
                    print(f"API request failed: {e}")

        # Sonuçları döndür
        return {
            "segments": transcription_segments,
            "full_transcription": full_transcription.strip()
        }
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error in transcription: {e}")
        return None
