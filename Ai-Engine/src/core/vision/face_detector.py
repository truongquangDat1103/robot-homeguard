"""
Face Detector - Phát hiện khuôn mặt trong ảnh/video.
Sử dụng MTCNN hoặc Haar Cascade từ OpenCV.
"""
from typing import List, Tuple, Optional                                                            # Kiểu dữ liệu cho type hints
import cv2                                                                                          # OpenCV để xử lý ảnh và video                           
import numpy as np                                                                                  # NumPy để xử lý mảng hình ảnh 
from loguru import logger                                                                           # Loguru để logging     

from src.utils.constants import FACE_DETECTION_MIN_SIZE


class Face:
    """Đại diện cho một khuôn mặt được phát hiện."""
    
    def __init__(
        self,
        bbox: Tuple[int, int, int, int],
        confidence: float,
        landmarks: Optional[np.ndarray] = None
    ):
        """
        Khởi tạo Face object.
        
        Args:
            bbox: Bounding box (x, y, w, h)
            confidence: Độ tin cậy (0.0 - 1.0)
            landmarks: Các điểm đặc trưng khuôn mặt
        """
        self.bbox = bbox
        self.confidence = confidence
        self.landmarks = landmarks
    
    @property
    def x(self) -> int:
        """X coordinate của góc trên bên trái."""
        return self.bbox[0]
    
    @property
    def y(self) -> int:
        """Y coordinate của góc trên bên trái."""
        return self.bbox[1]
    
    @property
    def width(self) -> int:
        """Chiều rộng của bbox."""
        return self.bbox[2]
    
    @property
    def height(self) -> int:
        """Chiều cao của bbox."""
        return self.bbox[3]
    
    @property
    def center(self) -> Tuple[int, int]:
        """Tâm của khuôn mặt."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def area(self) -> int:
        """Diện tích bbox."""
        return self.width * self.height


class FaceDetector:
    """
    Phát hiện khuôn mặt sử dụng Haar Cascade hoặc DNN.
    """
    
    def __init__(
        self,
        method: str = "haar",
        confidence_threshold: float = 0.7,
        min_face_size: int = FACE_DETECTION_MIN_SIZE
    ):
        """
        Khởi tạo face detector.
        
        Args:
            method: Phương pháp detection ("haar" hoặc "dnn")
            confidence_threshold: Ngưỡng độ tin cậy tối thiểu
            min_face_size: Kích thước khuôn mặt tối thiểu (pixels)
        """
        self.method = method
        self.confidence_threshold = confidence_threshold
        self.min_face_size = min_face_size
        
        # Cascade classifier
        self.face_cascade = None
        self.eye_cascade = None
        
        # DNN model
        self.dnn_net = None
        
        # Initialize detector
        self._initialize_detector()
        
        logger.info(f"Face detector khởi tạo (method: {method})")
    
    def _initialize_detector(self) -> None:
        """Khởi tạo detector model."""
        if self.method == "haar":
            self._initialize_haar_cascade()
        elif self.method == "dnn":
            self._initialize_dnn()
        else:
            raise ValueError(f"Phương pháp không hợp lệ: {self.method}")
    
    def _initialize_haar_cascade(self) -> None:
        """Khởi tạo Haar Cascade classifier."""
        try:
            # Load face cascade
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Load eye cascade (optional, để improve accuracy)
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
            
            logger.info("✅ Haar Cascade đã load")
            
        except Exception as e:
            logger.error(f"❌ Lỗi load Haar Cascade: {e}")
            raise
    
    def _initialize_dnn(self) -> None:
        """Khởi tạo DNN face detector."""
        try:
            # Load pre-trained model
            model_file = "deploy.prototxt"
            weights_file = "res10_300x300_ssd_iter_140000.caffemodel"
            
            self.dnn_net = cv2.dnn.readNetFromCaffe(model_file, weights_file)
            logger.info("✅ DNN model đã load")
            
        except Exception as e:
            logger.warning(f"⚠️  Không load được DNN model: {e}")
            logger.info("Chuyển sang dùng Haar Cascade")
            self.method = "haar"
            self._initialize_haar_cascade()
    
    def detect(self, frame: np.ndarray) -> List[Face]:
        """
        Phát hiện khuôn mặt trong frame.
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            List các Face objects
        """
        if frame is None or frame.size == 0:
            return []
        
        if self.method == "haar":
            return self._detect_haar(frame)
        elif self.method == "dnn":
            return self._detect_dnn(frame)
        
        return []
    
    def _detect_haar(self, frame: np.ndarray) -> List[Face]:
        """
        Phát hiện khuôn mặt bằng Haar Cascade.
        
        Args:
            frame: Input frame
            
        Returns:
            List các Face objects
        """
        # Convert sang grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces_rect = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(self.min_face_size, self.min_face_size)
        )
        
        faces = []
        for (x, y, w, h) in faces_rect:
            # Kiểm tra kích thước tối thiểu
            if w < self.min_face_size or h < self.min_face_size:
                continue
            
            # Tạo Face object
            face = Face(
                bbox=(x, y, w, h),
                confidence=1.0  # Haar không có confidence score
            )
            faces.append(face)
        
        return faces
    
    def _detect_dnn(self, frame: np.ndarray) -> List[Face]:
        """
        Phát hiện khuôn mặt bằng DNN.
        
        Args:
            frame: Input frame
            
        Returns:
            List các Face objects
        """
        h, w = frame.shape[:2]
        
        # Prepare input blob
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )
        
        # Forward pass
        self.dnn_net.setInput(blob)
        detections = self.dnn_net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            # Lọc theo confidence threshold
            if confidence < self.confidence_threshold:
                continue
            
            # Tính bounding box
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")
            
            # Convert sang (x, y, w, h)
            x = max(0, x1)
            y = max(0, y1)
            width = min(w - x, x2 - x1)
            height = min(h - y, y2 - y1)
            
            # Kiểm tra kích thước
            if width < self.min_face_size or height < self.min_face_size:
                continue
            
            face = Face(
                bbox=(x, y, width, height),
                confidence=float(confidence)
            )
            faces.append(face)
        
        return faces
    
    def detect_largest(self, frame: np.ndarray) -> Optional[Face]:
        """
        Phát hiện khuôn mặt lớn nhất trong frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Face object lớn nhất hoặc None
        """
        faces = self.detect(frame)
        
        if not faces:
            return None
        
        # Tìm face có diện tích lớn nhất
        return max(faces, key=lambda f: f.area)
    
    def draw_faces(
        self,
        frame: np.ndarray,
        faces: List[Face],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Vẽ bounding boxes lên frame.
        
        Args:
            frame: Input frame
            faces: List các Face objects
            color: Màu của bbox (BGR)
            thickness: Độ dày đường viền
            
        Returns:
            Frame đã vẽ
        """
        output = frame.copy()
        
        for face in faces:
            # Vẽ bounding box
            cv2.rectangle(
                output,
                (face.x, face.y),
                (face.x + face.width, face.y + face.height),
                color,
                thickness
            )
            
            # Vẽ confidence score
            if face.confidence < 1.0:
                text = f"{face.confidence:.2f}"
                cv2.putText(
                    output,
                    text,
                    (face.x, face.y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1
                )
        
        return output
    
    def get_face_roi(self, frame: np.ndarray, face: Face) -> np.ndarray:
        """
        Trích xuất vùng khuôn mặt từ frame.
        
        Args:
            frame: Input frame
            face: Face object
            
        Returns:
            ROI của khuôn mặt
        """
        return frame[
            face.y:face.y + face.height,
            face.x:face.x + face.width
        ]