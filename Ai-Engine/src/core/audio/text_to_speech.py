"""
Text to Speech - Chuyển text thành giọng nói.
Sử dụng gTTS (Google Text-to-Speech) hoặc Coqui TTS.
"""
import asyncio
from pathlib import Path
from typing import Optional
import numpy as np
from loguru import logger

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("⚠️  gTTS chưa cài đặt")

try:
    from pydub import AudioSegment
    from pydub.playback import play
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("⚠️  pydub chưa cài đặt")


class TextToSpeech:
    """
    Chuyển text thành giọng nói sử dụng gTTS.
    """
    
    def __init__(
        self,
        language: str = "en",
        slow: bool = False,
        engine: str = "gtts"
    ):
        """
        Khởi tạo Text-to-Speech.
        
        Args:
            language: Ngôn ngữ ("en", "vi", "ja", ...)
            slow: Tốc độ nói chậm hay không
            engine: TTS engine ("gtts" hoặc "coqui")
        """
        self.language = language
        self.slow = slow
        self.engine = engine
        
        # Check dependencies
        if engine == "gtts" and not GTTS_AVAILABLE:
            raise ImportError("gTTS chưa cài đặt. Cài: pip install gtts")
        
        logger.info(f"Text-to-Speech đã khởi tạo (engine: {engine}, lang: {language})")
    
    def speak(
        self,
        text: str,
        save_path: Optional[str] = None,
        play_audio: bool = True
    ) -> bool:
        """
        Chuyển text thành giọng nói.
        
        Args:
            text: Text cần nói
            save_path: Đường dẫn lưu file audio (optional)
            play_audio: Phát audio hay không
            
        Returns:
            True nếu thành công
        """
        if not text or not text.strip():
            logger.warning("Text rỗng")
            return False
        
        try:
            logger.info(f"Đang tạo audio: '{text[:50]}...'")
            
            # Tạo TTS object
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            
            # Lưu vào file tạm hoặc file chỉ định
            if save_path is None:
                save_path = "temp_tts.mp3"
            
            tts.save(save_path)
            logger.info(f"✅ Đã lưu audio: {save_path}")
            
            # Phát audio nếu cần
            if play_audio and PYDUB_AVAILABLE:
                self.play_audio_file(save_path)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi TTS: {e}")
            return False
    
    async def speak_async(
        self,
        text: str,
        save_path: Optional[str] = None,
        play_audio: bool = True
    ) -> bool:
        """
        Async version của speak.
        
        Args:
            text: Text cần nói
            save_path: Đường dẫn lưu file
            play_audio: Phát audio hay không
            
        Returns:
            True nếu thành công
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.speak,
            text,
            save_path,
            play_audio
        )
    
    def text_to_audio_data(self, text: str) -> Optional[np.ndarray]:
        """
        Chuyển text thành audio data (numpy array).
        
        Args:
            text: Text cần chuyển
            
        Returns:
            Audio data (numpy array) hoặc None
        """
        try:
            # Tạo file tạm
            temp_file = "temp_tts.mp3"
            
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            tts.save(temp_file)
            
            # Đọc audio data
            if PYDUB_AVAILABLE:
                audio = AudioSegment.from_mp3(temp_file)
                
                # Convert sang numpy array
                samples = np.array(audio.get_array_of_samples())
                
                # Normalize về [-1, 1]
                samples = samples.astype(np.float32) / (2**15)
                
                # Xóa file tạm
                Path(temp_file).unlink(missing_ok=True)
                
                return samples
            
            return None
            
        except Exception as e:
            logger.error(f"Lỗi convert text to audio data: {e}")
            return None
    
    def play_audio_file(self, audio_path: str) -> bool:
        """
        Phát audio từ file.
        
        Args:
            audio_path: Đường dẫn file audio
            
        Returns:
            True nếu phát thành công
        """
        if not PYDUB_AVAILABLE:
            logger.warning("pydub không có, không thể phát audio")
            return False
        
        try:
            logger.info(f"Đang phát audio: {audio_path}")
            
            # Load và phát audio
            audio = AudioSegment.from_file(audio_path)
            play(audio)
            
            logger.info("✅ Đã phát xong audio")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi phát audio: {e}")
            return False
    
    def get_supported_languages(self) -> dict:
        """
        Lấy danh sách ngôn ngữ hỗ trợ.
        
        Returns:
            Dictionary {code: name}
        """
        # Một số ngôn ngữ phổ biến
        languages = {
            "en": "English",
            "vi": "Vietnamese",
            "ja": "Japanese",
            "ko": "Korean",
            "zh-CN": "Chinese (Simplified)",
            "zh-TW": "Chinese (Traditional)",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "ru": "Russian",
            "ar": "Arabic",
            "hi": "Hindi",
            "th": "Thai",
            "id": "Indonesian",
        }
        return languages
    
    def set_language(self, language: str) -> None:
        """
        Thay đổi ngôn ngữ.
        
        Args:
            language: Language code
        """
        self.language = language
        logger.info(f"Đã đổi ngôn ngữ: {language}")
    
    def set_speed(self, slow: bool) -> None:
        """
        Thay đổi tốc độ nói.
        
        Args:
            slow: True = chậm, False = bình thường
        """
        self.slow = slow
        logger.info(f"Tốc độ nói: {'chậm' if slow else 'bình thường'}")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin TTS.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "engine": self.engine,
            "language": self.language,
            "slow": self.slow,
            "gtts_available": GTTS_AVAILABLE,
            "pydub_available": PYDUB_AVAILABLE
        }