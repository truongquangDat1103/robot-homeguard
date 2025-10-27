"""
Voice Recognition - Nhận diện người nói (Speaker Identification).
Phân biệt các người nói khác nhau dựa trên đặc điểm giọng nói.
"""
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
from loguru import logger

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("⚠️  librosa chưa cài đặt")


class VoicePrint:
    """Đại diện cho voiceprint của một người."""
    
    def __init__(
        self,
        speaker_name: str,
        features: np.ndarray,
        metadata: Optional[Dict] = None
    ):
        """
        Khởi tạo VoicePrint.
        
        Args:
            speaker_name: Tên người nói
            features: Voice features (MFCC, ...)
            metadata: Thông tin bổ sung
        """
        self.speaker_name = speaker_name
        self.features = features
        self.metadata = metadata or {}


class RecognizedSpeaker:
    """Kết quả nhận diện người nói."""
    
    def __init__(
        self,
        speaker_name: str,
        confidence: float,
        distance: float
    ):
        """
        Khởi tạo RecognizedSpeaker.
        
        Args:
            speaker_name: Tên người nói
            confidence: Độ tin cậy (0.0 - 1.0)
            distance: Khoảng cách feature
        """
        self.speaker_name = speaker_name
        self.confidence = confidence
        self.distance = distance


class VoiceRecognition:
    """
    Nhận diện người nói dựa trên đặc điểm giọng nói.
    """
    
    def __init__(
        self,
        database_path: Optional[str] = None,
        distance_threshold: float = 0.6
    ):
        """
        Khởi tạo voice recognition.
        
        Args:
            database_path: Đường dẫn database voiceprints
            distance_threshold: Ngưỡng khoảng cách để match
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("librosa chưa cài đặt. Cài: pip install librosa")
        
        self.database_path = database_path
        self.distance_threshold = distance_threshold
        
        # Database voiceprints
        self.voiceprints: List[VoicePrint] = []
        self.speaker_names: List[str] = []
        
        # Load database nếu có
        if database_path and Path(database_path).exists():
            self.load_database(database_path)
        
        logger.info("Voice recognition đã khởi tạo")
    
    def extract_features(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000
    ) -> np.ndarray:
        """
        Trích xuất features từ audio (MFCC).
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            
        Returns:
            Feature vector
        """
        try:
            # Chuẩn bị audio
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            audio_data = audio_data.flatten()
            
            # Trích xuất MFCC (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(
                y=audio_data,
                sr=sample_rate,
                n_mfcc=13
            )
            
            # Lấy mean và std của MFCCs
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)
            
            # Combine thành feature vector
            features = np.concatenate([mfcc_mean, mfcc_std])
            
            return features
            
        except Exception as e:
            logger.error(f"Lỗi extract features: {e}")
            return np.array([])
    
    def add_speaker(
        self,
        speaker_name: str,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Thêm voiceprint mới vào database.
        
        Args:
            speaker_name: Tên người nói
            audio_data: Audio data
            sample_rate: Sample rate
            metadata: Thông tin bổ sung
            
        Returns:
            True nếu thêm thành công
        """
        try:
            # Extract features
            features = self.extract_features(audio_data, sample_rate)
            
            if features.size == 0:
                logger.error("Không extract được features")
                return False
            
            # Tạo voiceprint
            voiceprint = VoicePrint(
                speaker_name=speaker_name,
                features=features,
                metadata=metadata
            )
            
            self.voiceprints.append(voiceprint)
            
            if speaker_name not in self.speaker_names:
                self.speaker_names.append(speaker_name)
            
            logger.info(f"✅ Đã thêm voiceprint: {speaker_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi thêm speaker: {e}")
            return False
    
    def recognize(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000
    ) -> Optional[RecognizedSpeaker]:
        """
        Nhận diện người nói.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            
        Returns:
            RecognizedSpeaker hoặc None
        """
        if not self.voiceprints:
            logger.warning("Database voiceprints rỗng")
            return None
        
        try:
            # Extract features
            features = self.extract_features(audio_data, sample_rate)
            
            if features.size == 0:
                return None
            
            # Tìm voiceprint gần nhất
            best_match = None
            min_distance = float('inf')
            
            for voiceprint in self.voiceprints:
                # Tính khoảng cách Euclidean
                distance = np.linalg.norm(features - voiceprint.features)
                
                if distance < min_distance:
                    min_distance = distance
                    best_match = voiceprint
            
            # Kiểm tra threshold
            if min_distance > self.distance_threshold:
                logger.debug(f"Không match (distance: {min_distance:.2f})")
                return None
            
            # Tạo RecognizedSpeaker
            confidence = 1.0 - min(min_distance / self.distance_threshold, 1.0)
            
            result = RecognizedSpeaker(
                speaker_name=best_match.speaker_name,
                confidence=confidence,
                distance=min_distance
            )
            
            logger.info(f"✅ Nhận diện: {result.speaker_name} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Lỗi recognize: {e}")
            return None
    
    def get_all_matches(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        top_k: int = 3
    ) -> List[RecognizedSpeaker]:
        """
        Lấy top K matches gần nhất.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            top_k: Số lượng results
            
        Returns:
            List RecognizedSpeaker (sorted by confidence)
        """
        if not self.voiceprints:
            return []
        
        try:
            features = self.extract_features(audio_data, sample_rate)
            
            if features.size == 0:
                return []
            
            # Tính distances cho tất cả voiceprints
            matches = []
            
            for voiceprint in self.voiceprints:
                distance = np.linalg.norm(features - voiceprint.features)
                confidence = 1.0 - min(distance / self.distance_threshold, 1.0)
                
                match = RecognizedSpeaker(
                    speaker_name=voiceprint.speaker_name,
                    confidence=confidence,
                    distance=distance
                )
                
                matches.append(match)
            
            # Sort by confidence (descending)
            matches.sort(key=lambda x: x.confidence, reverse=True)
            
            return matches[:top_k]
            
        except Exception as e:
            logger.error(f"Lỗi get all matches: {e}")
            return []
    
    def save_database(self, filepath: str) -> bool:
        """
        Lưu database voiceprints.
        
        Args:
            filepath: Đường dẫn file
            
        Returns:
            True nếu lưu thành công
        """
        try:
            data = {
                'voiceprints': self.voiceprints,
                'speaker_names': self.speaker_names
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"✅ Đã lưu database: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi lưu database: {e}")
            return False
    
    def load_database(self, filepath: str) -> bool:
        """
        Load database voiceprints.
        
        Args:
            filepath: Đường dẫn file
            
        Returns:
            True nếu load thành công
        """
        try:
            if not Path(filepath).exists():
                logger.warning(f"File không tồn tại: {filepath}")
                return False
            
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.voiceprints = data['voiceprints']
            self.speaker_names = data['speaker_names']
            
            logger.info(f"✅ Đã load database: {len(self.voiceprints)} voiceprints")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi load database: {e}")
            return False
    
    def remove_speaker(self, speaker_name: str) -> bool:
        """
        Xóa speaker khỏi database.
        
        Args:
            speaker_name: Tên speaker
            
        Returns:
            True nếu xóa thành công
        """
        try:
            # Xóa voiceprints
            self.voiceprints = [
                vp for vp in self.voiceprints
                if vp.speaker_name != speaker_name
            ]
            
            # Xóa name
            if speaker_name in self.speaker_names:
                self.speaker_names.remove(speaker_name)
            
            logger.info(f"✅ Đã xóa speaker: {speaker_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi xóa speaker: {e}")
            return False
    
    def get_speaker_names(self) -> List[str]:
        """Lấy danh sách speakers."""
        return self.speaker_names.copy()
    
    def get_speaker_count(self) -> int:
        """Lấy số lượng speakers."""
        return len(self.speaker_names)
    
    def clear_database(self) -> None:
        """Xóa toàn bộ database."""
        self.voiceprints.clear()
        self.speaker_names.clear()
        logger.info("Database đã được xóa")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin voice recognition.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "speaker_count": self.get_speaker_count(),
            "voiceprint_count": len(self.voiceprints),
            "distance_threshold": self.distance_threshold,
            "database_path": self.database_path
        }