"""
Face Recognizer - Nhận diện khuôn mặt đã được đăng ký.
Sử dụng face embeddings và similarity matching.
"""
import pickle                                                                               # Dùng để lưu và load database                  
from pathlib import Path                                                                    # Quản lý đường dẫn file                   
from typing import List, Dict, Optional, Tuple                                              # Kiểu dữ liệu cho type hints           
import numpy as np                                                                          # NumPy để xử lý mảng hình ảnh                   
import cv2                                                                                  # OpenCV để xử lý ảnh và video 
from loguru import logger                                                                   # Loguru để logging 

from src.core.vision.face_detector import Face
from src.utils.constants import FACE_RECOGNITION_DISTANCE_THRESHOLD


class FaceEncoding:
    """Đại diện cho encoding của một khuôn mặt."""
    
    def __init__(
        self,
        person_name: str,
        encoding: np.ndarray,
        metadata: Optional[Dict] = None
    ):
        """
        Khởi tạo FaceEncoding.
        
        Args:
            person_name: Tên người
            encoding: Vector embedding của khuôn mặt
            metadata: Thông tin bổ sung
        """
        self.person_name = person_name
        self.encoding = encoding
        self.metadata = metadata or {}


class RecognizedFace:
    """Kết quả nhận diện khuôn mặt."""
    
    def __init__(
        self,
        face: Face,
        person_name: str,
        confidence: float,
        distance: float
    ):
        """
        Khởi tạo RecognizedFace.
        
        Args:
            face: Face object từ detector
            person_name: Tên người được nhận diện
            confidence: Độ tin cậy (0.0 - 1.0)
            distance: Khoảng cách embedding
        """
        self.face = face
        self.person_name = person_name
        self.confidence = confidence
        self.distance = distance


class FaceRecognizer:
    """
    Nhận diện khuôn mặt dựa trên    
    Sử dụng face_recognition library hoặc OpenCV.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        distance_threshold: float = FACE_RECOGNITION_DISTANCE_THRESHOLD
    ):
        """
        Khởi tạo face recognizer.
        
        Args:
            model_path: Đường dẫn đến file embeddings
            distance_threshold: Ngưỡng khoảng cách để match
        """
        self.model_path = model_path
        self.distance_threshold = distance_threshold
        
        # Database của known faces
        self.known_encodings: List[FaceEncoding] = []
        self.known_names: List[str] = []
        
        # Face recognition model (sử dụng OpenCV LBPHFaceRecognizer)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer_trained = False
        
        # Load database nếu có
        if model_path:
            self.load_database(model_path)
        
        logger.info("Face recognizer đã khởi tạo")
    
    def add_face(
        self,
        person_name: str,
        face_image: np.ndarray,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Thêm khuôn mặt mới vào database.
        
        Args:
            person_name: Tên người
            face_image: Ảnh khuôn mặt (grayscale)
            metadata: Thông tin bổ sung
            
        Returns:
            True nếu thêm thành công
        """
        try:
            # Tạo encoding (đơn giản hóa, thực tế nên dùng deep learning)
            # Ở đây chỉ lưu ảnh để train LBPH
            encoding = FaceEncoding(
                person_name=person_name,
                encoding=face_image,
                metadata=metadata
            )
            
            self.known_encodings.append(encoding)
            
            if person_name not in self.known_names:
                self.known_names.append(person_name)
            
            logger.info(f"✅ Đã thêm khuôn mặt: {person_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi thêm khuôn mặt: {e}")
            return False
    
    def train(self) -> bool:
        """
        Train recognizer với database hiện tại.
        
        Returns:
            True nếu train thành công
        """
        if not self.known_encodings:
            logger.warning("Không có dữ liệu để train")
            return False
        
        try:
            # Chuẩn bị dữ liệu training
            faces = []
            labels = []
            
            for encoding in self.known_encodings:
                # Resize về kích thước chuẩn
                face_resized = cv2.resize(encoding.encoding, (200, 200))
                faces.append(face_resized)
                
                # Convert name sang label ID
                label = self.known_names.index(encoding.person_name)
                labels.append(label)
            
            # Train model
            self.recognizer.train(faces, np.array(labels))
            self.recognizer_trained = True
            
            logger.info(f"✅ Đã train với {len(faces)} khuôn mặt")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi train model: {e}")
            return False
    
    def recognize(
        self,
        face_image: np.ndarray,
        return_all: bool = False
    ) -> Optional[RecognizedFace]:
        """
        Nhận diện khuôn mặt.
        
        Args:
            face_image: Ảnh khuôn mặt cần nhận diện (grayscale)
            return_all: Trả về tất cả matches hay chỉ best match
            
        Returns:
            RecognizedFace object hoặc None
        """
        if not self.recognizer_trained:
            logger.warning("Model chưa được train")
            return None
        
        try:
            # Resize về kích thước chuẩn
            face_resized = cv2.resize(face_image, (200, 200))
            
            # Predict
            label, confidence = self.recognizer.predict(face_resized)
            
            # Confidence của LBPH: càng thấp càng tốt
            # Convert sang distance metric
            distance = confidence / 100.0
            
            # Kiểm tra threshold
            if distance > self.distance_threshold:
                logger.debug(f"Không match (distance: {distance:.2f})")
                return None
            
            # Lấy tên người
            person_name = self.known_names[label]
            
            # Tạo RecognizedFace
            # Note: Cần Face object từ detector, ở đây tạm tạo dummy
            dummy_face = Face(bbox=(0, 0, face_image.shape[1], face_image.shape[0]), confidence=1.0)
            
            recognized = RecognizedFace(
                face=dummy_face,
                person_name=person_name,
                confidence=1.0 - distance,
                distance=distance
            )
            
            logger.info(f"✅ Nhận diện: {person_name} (confidence: {recognized.confidence:.2f})")
            return recognized
            
        except Exception as e:
            logger.error(f"❌ Lỗi nhận diện: {e}")
            return None
    
    def recognize_faces(
        self,
        frame: np.ndarray,
        faces: List[Face]
    ) -> List[RecognizedFace]:
        """
        Nhận diện nhiều khuôn mặt trong frame.
        
        Args:
            frame: Input frame (BGR)
            faces: List các Face objects từ detector
            
        Returns:
            List các RecognizedFace objects
        """
        recognized_faces = []
        
        # Convert sang grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for face in faces:
            # Trích xuất ROI
            roi = gray[
                face.y:face.y + face.height,
                face.x:face.x + face.width
            ]
            
            # Nhận diện
            result = self.recognize(roi)
            
            if result:
                # Update face object
                result.face = face
                recognized_faces.append(result)
        
        return recognized_faces
    
    def save_database(self, filepath: str) -> bool:
        """
        Lưu database ra file.
        
        Args:
            filepath: Đường dẫn file
            
        Returns:
            True nếu lưu thành công
        """
        try:
            data = {
                'encodings': self.known_encodings,
                'names': self.known_names,
                'trained': self.recognizer_trained
            }
            
            # Save recognizer model
            model_path = str(Path(filepath).with_suffix('.yml'))
            if self.recognizer_trained:
                self.recognizer.save(model_path)
            
            # Save encodings
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"✅ Đã lưu database: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi lưu database: {e}")
            return False
    
    def load_database(self, filepath: str) -> bool:
        """
        Load database từ file.
        
        Args:
            filepath: Đường dẫn file
            
        Returns:
            True nếu load thành công
        """
        try:
            if not Path(filepath).exists():
                logger.warning(f"File không tồn tại: {filepath}")
                return False
            
            # Load encodings
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.known_encodings = data['encodings']
            self.known_names = data['names']
            self.recognizer_trained = data.get('trained', False)
            
            # Load recognizer model
            model_path = str(Path(filepath).with_suffix('.yml'))
            if Path(model_path).exists() and self.recognizer_trained:
                self.recognizer.read(model_path)
            
            logger.info(f"✅ Đã load database: {len(self.known_encodings)} faces")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi load database: {e}")
            return False
    
    def get_known_names(self) -> List[str]:
        """Lấy danh sách tên đã đăng ký."""
        return self.known_names.copy()
    
    def remove_person(self, person_name: str) -> bool:
        """
        Xóa một người khỏi database.
        
        Args:
            person_name: Tên người cần xóa
            
        Returns:
            True nếu xóa thành công
        """
        try:
            # Xóa encodings
            self.known_encodings = [
                enc for enc in self.known_encodings
                if enc.person_name != person_name
            ]
            
            # Xóa name
            if person_name in self.known_names:
                self.known_names.remove(person_name)
            
            # Cần train lại
            self.recognizer_trained = False
            
            logger.info(f"✅ Đã xóa: {person_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi xóa person: {e}")
            return False