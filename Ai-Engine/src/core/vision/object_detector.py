"""
Object Detector - Phát hiện các vật thể trong ảnh/video.
Sử dụng YOLO (You Only Look Once) model.
"""
from typing import List, Tuple, Optional
import cv2
import numpy as np
from loguru import logger

from src.utils.constants import YOLO_CONFIDENCE_THRESHOLD, YOLO_NMS_THRESHOLD


class DetectedObject:
    """Đại diện cho một vật thể được phát hiện."""
    
    def __init__(
        self,
        class_id: int,
        class_name: str,
        confidence: float,
        bbox: Tuple[int, int, int, int]
    ):
        """
        Khởi tạo DetectedObject.
        
        Args:
            class_id: ID của class
            class_name: Tên class (person, car, dog, ...)
            confidence: Độ tin cậy (0.0 - 1.0)
            bbox: Bounding box (x, y, w, h)
        """
        self.class_id = class_id
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox
    
    @property
    def x(self) -> int:
        return self.bbox[0]
    
    @property
    def y(self) -> int:
        return self.bbox[1]
    
    @property
    def width(self) -> int:
        return self.bbox[2]
    
    @property
    def height(self) -> int:
        return self.bbox[3]
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def area(self) -> int:
        return self.width * self.height


class ObjectDetector:
    """
    Phát hiện vật thể sử dụng YOLO.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        config_path: Optional[str] = None,
        classes_path: Optional[str] = None,
        confidence_threshold: float = YOLO_CONFIDENCE_THRESHOLD,
        nms_threshold: float = YOLO_NMS_THRESHOLD,
        use_gpu: bool = True
    ):
        """
        Khởi tạo object detector.
        
        Args:
            model_path: Đường dẫn đến YOLO weights
            config_path: Đường dẫn đến YOLO config
            classes_path: Đường dẫn đến file classes
            confidence_threshold: Ngưỡng confidence
            nms_threshold: Ngưỡng NMS (Non-Maximum Suppression)
            use_gpu: Sử dụng GPU hay không
        """
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.use_gpu = use_gpu
        
        # YOLO model
        self.net = None
        self.output_layers = []
        self.classes = []
        
        # Load model nếu có paths
        if model_path and config_path:
            self._load_yolo_model(model_path, config_path, classes_path)
        else:
            # Sử dụng ultralytics YOLO (đơn giản hơn)
            self._load_ultralytics_yolo()
        
        logger.info("Object detector đã khởi tạo")
    
    def _load_yolo_model(
        self,
        model_path: str,
        config_path: str,
        classes_path: Optional[str]
    ) -> None:
        """
        Load YOLO model từ files.
        
        Args:
            model_path: Đường dẫn weights
            config_path: Đường dẫn config
            classes_path: Đường dẫn classes
        """
        try:
            # Load network
            self.net = cv2.dnn.readNet(model_path, config_path)
            
            # Cấu hình backend
            if self.use_gpu:
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            else:
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            
            # Lấy output layers
            layer_names = self.net.getLayerNames()
            self.output_layers = [
                layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()
            ]
            
            # Load classes
            if classes_path:
                with open(classes_path, 'r') as f:
                    self.classes = [line.strip() for line in f.readlines()]
            
            logger.info(f"✅ YOLO model đã load ({len(self.classes)} classes)")
            
        except Exception as e:
            logger.error(f"❌ Lỗi load YOLO model: {e}")
            raise
    
    def _load_ultralytics_yolo(self) -> None:
        """Load YOLO model từ ultralytics."""
        try:
            from ultralytics import YOLO
            
            # Load pre-trained YOLOv8 model
            self.yolo_model = YOLO('yolov8n.pt')  # nano model (nhẹ nhất)
            
            # Lấy class names
            self.classes = list(self.yolo_model.names.values())
            
            logger.info(f"✅ YOLOv8 đã load ({len(self.classes)} classes)")
            
        except ImportError:
            logger.warning("⚠️  Ultralytics chưa cài đặt")
            logger.info("Cài đặt: pip install ultralytics")
            self.yolo_model = None
        except Exception as e:
            logger.error(f"❌ Lỗi load YOLOv8: {e}")
            self.yolo_model = None
    
    def detect(self, frame: np.ndarray) -> List[DetectedObject]:
        """
        Phát hiện vật thể trong frame.
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            List các DetectedObject
        """
        if frame is None or frame.size == 0:
            return []
        
        # Sử dụng ultralytics nếu có
        if hasattr(self, 'yolo_model') and self.yolo_model:
            return self._detect_ultralytics(frame)
        
        # Sử dụng OpenCV DNN
        if self.net:
            return self._detect_opencv_dnn(frame)
        
        logger.warning("Không có model để detect")
        return []
    
    def _detect_ultralytics(self, frame: np.ndarray) -> List[DetectedObject]:
        """
        Phát hiện sử dụng ultralytics YOLO.
        
        Args:
            frame: Input frame
            
        Returns:
            List DetectedObject
        """
        try:
            # Run inference
            results = self.yolo_model(frame, verbose=False)[0]
            
            detected_objects = []
            
            # Parse results
            for box in results.boxes:
                # Lấy thông tin
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                # Lọc theo confidence
                if confidence < self.confidence_threshold:
                    continue
                
                # Convert sang (x, y, w, h)
                x, y = int(x1), int(y1)
                w, h = int(x2 - x1), int(y2 - y1)
                
                # Lấy class name
                class_name = self.classes[class_id] if class_id < len(self.classes) else f"class_{class_id}"
                
                # Tạo DetectedObject
                obj = DetectedObject(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox=(x, y, w, h)
                )
                
                detected_objects.append(obj)
            
            return detected_objects
            
        except Exception as e:
            logger.error(f"Lỗi detect ultralytics: {e}")
            return []
    
    def _detect_opencv_dnn(self, frame: np.ndarray) -> List[DetectedObject]:
        """
        Phát hiện sử dụng OpenCV DNN.
        
        Args:
            frame: Input frame
            
        Returns:
            List DetectedObject
        """
        height, width = frame.shape[:2]
        
        # Tạo blob
        blob = cv2.dnn.blobFromImage(
            frame,
            1/255.0,
            (416, 416),
            swapRB=True,
            crop=False
        )
        
        # Forward pass
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)
        
        # Parse outputs
        class_ids = []
        confidences = []
        boxes = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.confidence_threshold:
                    # Tính bounding box
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = center_x - w // 2
                    y = center_y - h // 2
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes,
            confidences,
            self.confidence_threshold,
            self.nms_threshold
        )
        
        # Tạo DetectedObject list
        detected_objects = []
        
        if len(indices) > 0:
            for i in indices.flatten():
                class_name = self.classes[class_ids[i]] if class_ids[i] < len(self.classes) else f"class_{class_ids[i]}"
                
                obj = DetectedObject(
                    class_id=class_ids[i],
                    class_name=class_name,
                    confidence=confidences[i],
                    bbox=tuple(boxes[i])
                )
                
                detected_objects.append(obj)
        
        return detected_objects
    
    def draw_objects(
        self,
        frame: np.ndarray,
        objects: List[DetectedObject],
        show_confidence: bool = True
    ) -> np.ndarray:
        """
        Vẽ các vật thể lên frame.
        
        Args:
            frame: Input frame
            objects: List DetectedObject
            show_confidence: Hiển thị confidence score
            
        Returns:
            Frame đã vẽ
        """
        output = frame.copy()
        
        # Màu cho mỗi class (random)
        np.random.seed(42)
        colors = np.random.randint(0, 255, size=(len(self.classes), 3), dtype=np.uint8)
        
        for obj in objects:
            # Lấy màu
            color = tuple(map(int, colors[obj.class_id % len(colors)]))
            
            # Vẽ bounding box
            cv2.rectangle(
                output,
                (obj.x, obj.y),
                (obj.x + obj.width, obj.y + obj.height),
                color,
                2
            )
            
            # Vẽ label
            label = obj.class_name
            if show_confidence:
                label = f"{label}: {obj.confidence:.2f}"
            
            # Vẽ background cho text
            (label_w, label_h), _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                1
            )
            
            cv2.rectangle(
                output,
                (obj.x, obj.y - label_h - 10),
                (obj.x + label_w, obj.y),
                color,
                -1
            )
            
            # Vẽ text
            cv2.putText(
                output,
                label,
                (obj.x, obj.y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )
        
        return output
    
    def filter_by_class(
        self,
        objects: List[DetectedObject],
        class_names: List[str]
    ) -> List[DetectedObject]:
        """
        Lọc objects theo class names.
        
        Args:
            objects: List DetectedObject
            class_names: Danh sách class names cần giữ
            
        Returns:
            List objects đã lọc
        """
        return [obj for obj in objects if obj.class_name in class_names]
    
    def get_classes(self) -> List[str]:
        """Lấy danh sách classes."""
        return self.classes.copy()