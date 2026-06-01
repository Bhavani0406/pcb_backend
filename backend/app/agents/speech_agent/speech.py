import base64
import os
import tempfile
from typing import Optional
from gtts import gTTS
from app.core.config.settings import settings
from app.core.logger.logging import logger


class SpeechAgent:
    def __init__(self):
        pass

    def text_to_speech_base64(self, text: str) -> Optional[str]:
        """
        Converts text to speech using gTTS and returns the audio encoded in a Base64 data-URI string.
        Returns None if gTTS fails (e.g., no internet), allowing the frontend to use Web Speech API fallback.
        """
        if not settings.ENABLE_SERVER_TTS:
            logger.info("Server TTS disabled. Frontend will use Web Speech API fallback.")
            return None

        try:
            logger.info("SpeechAgent converting text to speech using gTTS")
            tts = gTTS(text=text, lang="en", tld="com", slow=False)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_filename = fp.name

            try:
                tts.save(temp_filename)
                with open(temp_filename, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                return f"data:audio/mp3;base64,{base64_audio}"
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        except Exception as e:
            logger.error(f"Text-to-Speech conversion failed: {str(e)}. Frontend will use Web Speech API fallback.")
            return None

    def transcribe_audio_base64(self, audio_base64: str) -> str:
        """
        Intended for server-side transcription of base64-encoded audio.
        In the current hybrid design, the browser Web Speech API is the primary, zero-latency STT engine.
        The frontend sends the final transcribed string directly over WebSocket, bypassing heavy
        native audio binary dependencies (like PyAudio/Whisper C-extensions).
        This method exists as the extension point for adding Whisper-based processing later.
        """
        if not audio_base64:
            return ""
        logger.info("SpeechAgent received audio chunk (server-side transcription placeholder)")
        return "[Server-side audio received — client-side transcript preferred]"
