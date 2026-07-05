import io
import base64
from gtts import gTTS
import speech_recognition as sr
from backend.app.utils.helpers import get_iso_lang_code

class SpeechService:
    @staticmethod
    def text_to_speech_base64(text: str, language_name: str = "English") -> str:
        """
        Converts text to MP3 audio using gTTS and returns it as a base64 encoded string.
        Can be played in Streamlit via the HTML5 <audio> tag.
        """
        try:
            lang_code = get_iso_lang_code(language_name)
            
            # Generate TTS audio in memory
            tts = gTTS(text=text, lang=lang_code, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            # Encode to base64
            audio_bytes = fp.read()
            b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
            return f"data:audio/mp3;base64,{b64_audio}"
        except Exception as e:
            print(f"TTS conversion failed: {e}")
            return ""

    @staticmethod
    def transcribe_audio(audio_file_bytes: bytes) -> str:
        """
        Transcribes an uploaded audio file (WAV or other supported formats) using SpeechRecognition.
        """
        try:
            r = sr.Recognizer()
            # Convert bytes to an audio file-like object
            audio_file = io.BytesIO(audio_file_bytes)
            
            with sr.AudioFile(audio_file) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data)
                return text
        except Exception as e:
            print(f"STT transcription failed: {e}")
            return "Transcription failed. Please type your message."
