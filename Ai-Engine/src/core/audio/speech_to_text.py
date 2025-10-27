"""
Speech to Text - Chuyển đổi giọng nói thành text.
Sử dụng Whisper (OpenAI) hoặc Vosk.
"""
import asyncio
from typing import Optional, Dict
import numpy as np
from loguru import logger

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("⚠️  whisper chưa cài đặt")

from config.settings import AudioSettings


class TranscriptionResult:
    """Kết quả chuyển đổi giọng nói."""
    
    def __init__(
        self,
        text: str,
        language: str,
        confidence: float,
        duration: float,
        segments: Optional[list] = None
    ):
        """
        Khởi tạo TranscriptionResult.
        
        Args:
            text: Text đã chuyển đổi
            language: Ngôn ngữ phát hiện được
            confidence: Độ tin cậy (0.0 - 1.0)
            duration: Thời lượng audio (giây)
            segments: Chi tiết các segments (optional)
        """
        self.text = text
        self.language = language
        self.confidence = confidence
        self.duration = duration
        self.segments = segments or []


class SpeechToText:
    """
    Chuyển đổi giọng nói thành text sử dụng Whisper.
    """
    
    def __init__(
        self,
        model_size: str = "base",
        language: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        Khởi tạo Speech-to-Text.
        
        Args:
            model_size: Kích thước model ("tiny", "base", "small", "medium", "large")
            language: Ngôn ngữ (None = auto-detect)
            device: Device ("cpu" hoặc "cuda")
        """
        if not WHISPER_AVAILABLE:
            raise ImportError("Whisper chưa cài đặt. Cài: pip install openai-whisper")
        
        self.model_size = model_size
        self.language = language
        self.device = device
        
        # Load model
        self.model = None
        self._load_model()
        
        logger.info(f"Speech-to-Text đã khởi tạo (model: {model_size})")
    
    def _load_model(self) -> None:
        """Load Whisper model."""
        try:
            logger.info(f"Đang load Whisper model ({self.model_size})...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info("✅ Whisper model đã load")
            
        except Exception as e:
            logger.error(f"❌ Lỗi load model: {e}")
            raise
    
    def transcribe(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000
    ) -> Optional[TranscriptionResult]:
        """
        Chuyển đổi audio thành text.
        
        Args:
            audio_data: Audio data (numpy array)
            sample_rate: Sample rate của audio
            
        Returns:
            TranscriptionResult hoặc None
        """
        if self.model is None:
            logger.error("Model chưa được load")
            return None
        
        try:
            # Chuẩn bị audio
            audio = self._prepare_audio(audio_data, sample_rate)
            
            # Transcribe
            logger.info("Đang transcribe audio...")
            result = self.model.transcribe(
                audio,
                language=self.language,
                fp16=(self.device == "cuda")
            )
            
            # Parse result
            text = result.get("text", "").strip()
            language = result.get("language", "unknown")
            segments = result.get("segments", [])
            
            # Tính confidence trung bình
            if segments:
                confidences = [seg.get("no_speech_prob", 0) for seg in segments]
                avg_confidence = 1.0 - (sum(confidences) / len(confidences))
            else:
                avg_confidence = 0.5
            
            # Tính duration
            duration = len(audio_data) / sample_rate
            
            logger.info(f"✅ Transcribe thành công: '{text[:50]}...'")
            
            return TranscriptionResult(
                text=text,
                language=language,
                confidence=avg_confidence,
                duration=duration,
                segments=segments
            )
            
        except Exception as e:
            logger.error(f"❌ Lỗi transcribe: {e}")
            return None
    
    async def transcribe_async(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000
    ) -> Optional[TranscriptionResult]:
        """
        Async version của transcribe.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            
        Returns:
            TranscriptionResult hoặc None
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.transcribe,
            audio_data,
            sample_rate
        )
    
    def _prepare_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int
    ) -> np.ndarray:
        """
        Chuẩn bị audio cho Whisper.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate hiện tại
            
        Returns:
            Audio data đã chuẩn bị
        """
        # Whisper cần mono audio
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Flatten nếu cần
        audio_data = audio_data.flatten()
        
        # Whisper cần audio ở 16kHz
        if sample_rate != 16000:
            # Resample (đơn giản hóa, thực tế nên dùng librosa.resample)
            import librosa
            audio_data = librosa.resample(
                audio_data,
                orig_sr=sample_rate,
                target_sr=16000
            )
        
        # Normalize
        audio_data = audio_data.astype(np.float32)
        max_val = np.abs(audio_data).max()
        if max_val > 0:
            audio_data = audio_data / max_val
        
        return audio_data
    
    def transcribe_file(self, audio_path: str) -> Optional[TranscriptionResult]:
        """
        Transcribe từ file audio.
        
        Args:
            audio_path: Đường dẫn file audio
            
        Returns:
            TranscriptionResult hoặc None
        """
        try:
            logger.info(f"Đang transcribe file: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                fp16=(self.device == "cuda")
            )
            
            text = result.get("text", "").strip()
            language = result.get("language", "unknown")
            segments = result.get("segments", [])
            
            # Tính confidence
            if segments:
                confidences = [1.0 - seg.get("no_speech_prob", 0) for seg in segments]
                avg_confidence = sum(confidences) / len(confidences)
            else:
                avg_confidence = 0.5
            
            logger.info(f"✅ Transcribe file thành công")
            
            return TranscriptionResult(
                text=text,
                language=language,
                confidence=avg_confidence,
                duration=0.0,  # Không tính được từ file
                segments=segments
            )
            
        except Exception as e:
            logger.error(f"❌ Lỗi transcribe file: {e}")
            return None
    
    def detect_language(self, audio_data: np.ndarray) -> Optional[str]:
        """
        Phát hiện ngôn ngữ trong audio.
        
        Args:
            audio_data: Audio data
            
        Returns:
            Language code hoặc None
        """
        try:
            audio = self._prepare_audio(audio_data, 16000)
            
            # Load audio và detect language
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            
            logger.info(f"Ngôn ngữ phát hiện: {detected_lang} (confidence: {probs[detected_lang]:.2f})")
            return detected_lang
            
        except Exception as e:
            logger.error(f"Lỗi detect language: {e}")
            return None
    
    def get_available_models(self) -> list:
        """
        Lấy danh sách models có sẵn.
        
        Returns:
            List model names
        """
        return ["tiny", "base", "small", "medium", "large"]
    
    def change_model(self, model_size: str) -> bool:
        """
        Thay đổi model size.
        
        Args:
            model_size: Model size mới
            
        Returns:
            True nếu thành công
        """
        try:
            self.model_size = model_size
            self._load_model()
            return True
        except Exception as e:
            logger.error(f"Lỗi change model: {e}")
            return False
    
    def get_info(self) -> dict:
        """
        Lấy thông tin STT.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "model_size": self.model_size,
            "language": self.language or "auto",
            "device": self.device,
            "model_loaded": self.model is not None
        }