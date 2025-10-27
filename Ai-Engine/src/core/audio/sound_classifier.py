"""
Sound Classifier - Phân loại các loại âm thanh.
Phát hiện alarm, doorbell, dog barking, baby crying, v.v.
"""
from typing import List, Tuple, Optional
import numpy as np
from loguru import logger

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("⚠️  librosa chưa cài đặt")


class SoundClass:
    """Đại diện cho một loại âm thanh."""
    
    def __init__(
        self,
        class_name: str,
        confidence: float,
        timestamp: float = 0.0
    ):
        """
        Khởi tạo SoundClass.
        
        Args:
            class_name: Tên loại âm thanh
            confidence: Độ tin cậy (0.0 - 1.0)
            timestamp: Thời điểm xuất hiện (giây)
        """
        self.class_name = class_name
        self.confidence = confidence
        self.timestamp = timestamp


class SoundClassifier:
    """
    Phân loại âm thanh sử dụng feature extraction.
    Đơn giản hóa - dựa trên đặc điểm cơ bản của âm thanh.
    """
    
    # Định nghĩa các loại âm thanh có thể detect
    SOUND_CLASSES = [
        "speech",      # Giọng nói
        "music",       # Nhạc
        "alarm",       # Chuông báo động
        "doorbell",    # Chuông cửa
        "dog_bark",    # Chó sủa
        "baby_cry",    # Em bé khóc
        "glass_break", # Kính vỡ
        "footsteps",   # Bước chân
        "silence",     # Im lặng
        "unknown"      # Không xác định
    ]
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Khởi tạo sound classifier.
        
        Args:
            confidence_threshold: Ngưỡng confidence tối thiểu
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("librosa chưa cài đặt. Cài: pip install librosa")
        
        self.confidence_threshold = confidence_threshold
        
        logger.info("Sound classifier đã khởi tạo")
    
    def classify(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000
    ) -> Optional[SoundClass]:
        """
        Phân loại âm thanh.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            
        Returns:
            SoundClass hoặc None
        """
        try:
            # Extract features
            features = self._extract_features(audio_data, sample_rate)
            
            # Phân loại dựa trên features (rule-based đơn giản)
            class_name, confidence = self._classify_by_features(features, audio_data, sample_rate)
            
            if confidence < self.confidence_threshold:
                class_name = "unknown"
            
            result = SoundClass(
                class_name=class_name,
                confidence=confidence
            )
            
            logger.debug(f"Phân loại: {class_name} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Lỗi classify sound: {e}")
            return None
    
    def _extract_features(
        self,
        audio_data: np.ndarray,
        sample_rate: int
    ) -> dict:
        """
        Trích xuất các features từ audio.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            
        Returns:
            Dictionary features
        """
        # Chuẩn bị audio
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        audio_data = audio_data.flatten()
        
        features = {}
        
        # Zero Crossing Rate (tốc độ audio thay đổi dấu)
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        features['zcr_mean'] = np.mean(zcr)
        features['zcr_std'] = np.std(zcr)
        
        # Spectral Centroid (trung tâm phổ tần)
        spectral_centroids = librosa.feature.spectral_centroid(
            y=audio_data,
            sr=sample_rate
        )[0]
        features['spectral_centroid_mean'] = np.mean(spectral_centroids)
        features['spectral_centroid_std'] = np.std(spectral_centroids)
        
        # RMS Energy (năng lượng)
        rms = librosa.feature.rms(y=audio_data)[0]
        features['rms_mean'] = np.mean(rms)
        features['rms_std'] = np.std(rms)
        
        # MFCCs
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        features['mfcc_mean'] = np.mean(mfccs, axis=1)
        
        return features
    
    def _classify_by_features(
        self,
        features: dict,
        audio_data: np.ndarray,
        sample_rate: int
    ) -> Tuple[str, float]:
        """
        Phân loại dựa trên features (rule-based).
        
        Args:
            features: Dictionary features
            audio_data: Audio data gốc
            sample_rate: Sample rate
            
        Returns:
            (class_name, confidence)
        """
        # Kiểm tra silence
        if features['rms_mean'] < 0.01:
            return ("silence", 0.9)
        
        # Kiểm tra speech (ZCR trung bình, spectral centroid không quá cao)
        if (0.05 < features['zcr_mean'] < 0.15 and
            1000 < features['spectral_centroid_mean'] < 3000):
            return ("speech", 0.7)
        
        # Kiểm tra music (spectral centroid cao, RMS ổn định)
        if (features['spectral_centroid_mean'] > 2000 and
            features['rms_std'] < 0.05):
            return ("music", 0.6)
        
        # Kiểm tra alarm (tần số cao, ổn định)
        if (features['spectral_centroid_mean'] > 3000 and
            features['zcr_mean'] > 0.2):
            return ("alarm", 0.65)
        
        # Kiểm tra dog bark (burst ngắn, tần số trung bình-cao)
        if (features['rms_std'] > 0.1 and
            1500 < features['spectral_centroid_mean'] < 4000):
            return ("dog_bark", 0.5)
        
        # Default
        return ("unknown", 0.3)
    
    def detect_events(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        window_size: float = 1.0
    ) -> List[SoundClass]:
        """
        Phát hiện các sound events trong audio dài.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            window_size: Kích thước window (giây)
            
        Returns:
            List SoundClass
        """
        events = []
        
        # Tính số samples trong 1 window
        window_samples = int(window_size * sample_rate)
        
        # Slide window qua audio
        for i in range(0, len(audio_data), window_samples // 2):  # 50% overlap
            window = audio_data[i:i + window_samples]
            
            if len(window) < window_samples // 2:
                break
            
            # Classify window
            sound_class = self.classify(window, sample_rate)
            
            if sound_class and sound_class.class_name != "unknown":
                sound_class.timestamp = i / sample_rate
                events.append(sound_class)
        
        return events
    
    def is_voice_active(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000
    ) -> bool:
        """
        Voice Activity Detection (VAD) đơn giản.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            
        Returns:
            True nếu có giọng nói
        """
        sound_class = self.classify(audio_data, sample_rate)
        
        if sound_class:
            return sound_class.class_name == "speech"
        
        return False
    
    def get_supported_classes(self) -> List[str]:
        """Lấy danh sách classes hỗ trợ."""
        return self.SOUND_CLASSES.copy()
    
    def get_info(self) -> dict:
        """
        Lấy thông tin classifier.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "supported_classes": len(self.SOUND_CLASSES),
            "confidence_threshold": self.confidence_threshold,
            "classes": self.SOUND_CLASSES
        }