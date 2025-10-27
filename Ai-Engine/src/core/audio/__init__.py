"""
Audio Module - Audio Processing components.
Các module xử lý âm thanh và giọng nói.
"""

from src.core.audio.audio_capture import AudioCapture, AudioState
from src.core.audio.speech_to_text import SpeechToText, TranscriptionResult
from src.core.audio.text_to_speech import TextToSpeech
from src.core.audio.voice_recognition import (
    VoiceRecognition,
    VoicePrint,
    RecognizedSpeaker
)
from src.core.audio.sound_classifier import SoundClassifier, SoundClass
from src.core.audio.noise_reducer import NoiseReducer


__all__ = [
    # Audio Capture
    "AudioCapture",
    "AudioState",
    
    # Speech to Text
    "SpeechToText",
    "TranscriptionResult",
    
    # Text to Speech
    "TextToSpeech",
    
    # Voice Recognition
    "VoiceRecognition",
    "VoicePrint",
    "RecognizedSpeaker",
    
    # Sound Classification
    "SoundClassifier",
    "SoundClass",
    
    # Noise Reduction
    "NoiseReducer",
]