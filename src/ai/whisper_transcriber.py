# whisper_transcriber.py
import os
from typing import Optional

import streamlit as st
import whisper


class WhisperTranscriber:
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper transcriber

        Args:
            model_size: Size of Whisper model ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_size = model_size
        self.model = None

    @st.cache_resource
    def _load_model(_self):
        """Load Whisper model (cached for performance)"""
        try:
            return whisper.load_model(_self.model_size)
        except Exception as e:
            st.error(f"Failed to load Whisper model: {str(e)}")
            return None

    def transcribe(self, audio_path: str, language: str = None) -> Optional[str]:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'hi', 'en', 'te')

        Returns:
            Transcribed text or None if failed
        """
        if not os.path.exists(audio_path):
            st.error(f"Audio file not found: {audio_path}")
            return None

        try:
            # Load model if not already loaded
            if self.model is None:
                self.model = self._load_model()

            if self.model is None:
                return None

            # Map language codes to Whisper format
            language_mapping = {
                "hi": "hindi",
                "te": "telugu",
                "ta": "tamil",
                "bn": "bengali",
                "mr": "marathi",
                "gu": "gujarati",
                "kn": "kannada",
                "ml": "malayalam",
                "pa": "punjabi",
                "en": "english",
            }

            whisper_language = language_mapping.get(language, "english")

            # Transcribe
            result = self.model.transcribe(
                audio_path,
                language=whisper_language if language != "auto" else None,
                fp16=False,  # Better compatibility
            )

            return result["text"].strip()

        except Exception as e:
            st.error(f"Transcription failed: {str(e)}")
            return None

    def get_supported_languages(self) -> dict:
        """Get supported languages"""
        return {
            "Hindi": "hi",
            "Telugu": "te",
            "Tamil": "ta",
            "Bengali": "bn",
            "Marathi": "mr",
            "Gujarati": "gu",
            "Kannada": "kn",
            "Malayalam": "ml",
            "Punjabi": "pa",
            "English": "en",
        }

    def detect_language(self, audio_path: str) -> Optional[str]:
        """
        Detect language of audio file

        Args:
            audio_path: Path to audio file

        Returns:
            Detected language code or None
        """
        try:
            if self.model is None:
                self.model = self._load_model()

            if self.model is None:
                return None

            # Load audio and pad/trim to 30 seconds
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)

            # Make log-Mel spectrogram and move to same device as model
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

            # Detect language
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)

            return detected_language

        except Exception as e:
            st.warning(f"Language detection failed: {str(e)}")
            return None
