"""
Motion Detector - Phát hiện chuyển động trong video.
Sử dụng background subtraction và contour detection.
"""
from typing import List, Tuple, Optional                                            # Kiểu dữ liệu cho type hints   
import cv2                                                                          # OpenCV để xử lý video và ảnh           
import numpy as np                                                                  # NumPy để xử lý mảng hình ảnh    
from loguru import logger                                                           # Loguru để logging 

from src.utils.constants import MOTION_THRESHOLD, MOTION_MIN_AREA


class MotionRegion:
    """Đại diện cho một vùng chuyển động."""
    
    def __init__(
        self,
        bbox: Tuple[int, int, int, int],
        area: int,
        center: Tuple[int, int],
        contour: np.ndarray
    ):
        """
        Khởi tạo MotionRegion.
        
        Args:
            bbox: Bounding box (x, y, w, h)
            area: Diện tích vùng chuyển động
            center: Tâm của vùng
            contour: Contour points
        """
        self.bbox = bbox
        self.area = area
        self.center = center
        self.contour = contour
    
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


class MotionDetector:
    """
    Phát hiện chuyển động sử dụng background subtraction.
    """
    
    def __init__(
        self,
        method: str = "mog2",
        threshold: int = MOTION_THRESHOLD,
        min_area: int = MOTION_MIN_AREA,
        learning_rate: float = 0.001
    ):
        """
        Khởi tạo motion detector.
        
        Args:
            method: Phương pháp detection ("mog2", "knn", "frame_diff")
            threshold: Ngưỡng để coi là chuyển động
            min_area: Diện tích tối thiểu của vùng chuyển động
            learning_rate: Tốc độ học background (0.0 - 1.0)
        """
        self.method = method
        self.threshold = threshold
        self.min_area = min_area
        self.learning_rate = learning_rate
        
        # Background subtractor
        self.bg_subtractor = None
        
        # Frame trước đó (cho frame differencing)
        self.prev_frame = None
        
        # Statistics
        self.motion_detected = False
        self.total_motion_area = 0
        
        # Khởi tạo
        self._initialize_subtractor()
        
        logger.info(f"Motion detector khởi tạo (method: {method})")
    
    def _initialize_subtractor(self) -> None:
        """Khởi tạo background subtractor."""
        if self.method == "mog2":
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                detectShadows=True
            )
        elif self.method == "knn":
            self.bg_subtractor = cv2.createBackgroundSubtractorKNN(
                detectShadows=True
            )
        elif self.method == "frame_diff":
            # Không cần subtractor, dùng frame differencing
            pass
        else:
            raise ValueError(f"Phương pháp không hợp lệ: {self.method}")
    
    def detect(self, frame: np.ndarray) -> List[MotionRegion]:
        """
        Phát hiện chuyển động trong frame.
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            List các MotionRegion objects
        """
        if frame is None or frame.size == 0:
            return []
        
        if self.method in ["mog2", "knn"]:
            return self._detect_bg_subtraction(frame)
        elif self.method == "frame_diff":
            return self._detect_frame_diff(frame)
        
        return []
    
    def _detect_bg_subtraction(self, frame: np.ndarray) -> List[MotionRegion]:
        """
        Phát hiện chuyển động bằng background subtraction.
        
        Args:
            frame: Input frame
            
        Returns:
            List các MotionRegion
        """
        # Apply background subtractor
        fg_mask = self.bg_subtractor.apply(frame, learningRate=self.learning_rate)
        
        # Loại bỏ shadows (giá trị 127)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        
        # Morphological operations để loại noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Tìm contours
        contours, _ = cv2.findContours(
            fg_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        return self._process_contours(contours)
    
    def _detect_frame_diff(self, frame: np.ndarray) -> List[MotionRegion]:
        """
        Phát hiện chuyển động bằng frame differencing.
        
        Args:
            frame: Input frame
            
        Returns:
            List các MotionRegion
        """
        # Convert sang grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Nếu chưa có frame trước, lưu lại
        if self.prev_frame is None:
            self.prev_frame = gray
            return []
        
        # Tính frame difference
        frame_diff = cv2.absdiff(self.prev_frame, gray)
        
        # Threshold
        _, thresh = cv2.threshold(frame_diff, self.threshold, 255, cv2.THRESH_BINARY)
        
        # Dilate để fill holes
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Tìm contours
        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Update prev frame
        self.prev_frame = gray
        
        return self._process_contours(contours)
    
    def _process_contours(self, contours: List) -> List[MotionRegion]:
        """
        Xử lý contours và tạo MotionRegion objects.
        
        Args:
            contours: List contours từ cv2.findContours
            
        Returns:
            List các MotionRegion
        """
        motion_regions = []
        self.total_motion_area = 0
        
        for contour in contours:
            # Tính diện tích
            area = cv2.contourArea(contour)
            
            # Lọc theo diện tích tối thiểu
            if area < self.min_area:
                continue
            
            # Tính bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Tính center
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx = x + w // 2
                cy = y + h // 2
            
            # Tạo MotionRegion
            region = MotionRegion(
                bbox=(x, y, w, h),
                area=int(area),
                center=(cx, cy),
                contour=contour
            )
            
            motion_regions.append(region)
            self.total_motion_area += area
        
        # Update motion status
        self.motion_detected = len(motion_regions) > 0
        
        return motion_regions
    
    def draw_motion(
        self,
        frame: np.ndarray,
        regions: List[MotionRegion],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2
    ) -> np.ndarray:
        """
        Vẽ các vùng chuyển động lên frame.
        
        Args:
            frame: Input frame
            regions: List các MotionRegion
            color: Màu vẽ (BGR)
            thickness: Độ dày đường viền
            
        Returns:
            Frame đã vẽ
        """
        output = frame.copy()
        
        for region in regions:
            # Vẽ bounding box
            cv2.rectangle(
                output,
                (region.x, region.y),
                (region.x + region.width, region.y + region.height),
                color,
                thickness
            )
            
            # Vẽ center point
            cv2.circle(output, region.center, 5, color, -1)
            
            # Vẽ text (area)
            text = f"Area: {region.area}"
            cv2.putText(
                output,
                text,
                (region.x, region.y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )
        
        return output
    
    def get_motion_mask(self, frame: np.ndarray) -> np.ndarray:
        """
        Lấy motion mask (binary image).
        
        Args:
            frame: Input frame
            
        Returns:
            Binary mask
        """
        if self.method in ["mog2", "knn"]:
            fg_mask = self.bg_subtractor.apply(frame, learningRate=self.learning_rate)
            _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
            return fg_mask
        
        elif self.method == "frame_diff":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            if self.prev_frame is None:
                self.prev_frame = gray
                return np.zeros(frame.shape[:2], dtype=np.uint8)
            
            frame_diff = cv2.absdiff(self.prev_frame, gray)
            _, thresh = cv2.threshold(frame_diff, self.threshold, 255, cv2.THRESH_BINARY)
            self.prev_frame = gray
            
            return thresh
        
        return np.zeros(frame.shape[:2], dtype=np.uint8)
    
    def is_motion_detected(self) -> bool:
        """Kiểm tra có phát hiện chuyển động không."""
        return self.motion_detected
    
    def get_total_motion_area(self) -> int:
        """Lấy tổng diện tích chuyển động."""
        return self.total_motion_area
    
    def reset(self) -> None:
        """Reset detector (clear background model)."""
        self._initialize_subtractor()
        self.prev_frame = None
        self.motion_detected = False
        self.total_motion_area = 0
        logger.info("Motion detector đã reset")
    
    def set_learning_rate(self, learning_rate: float) -> None:
        """
        Thay đổi learning rate.
        
        Args:
            learning_rate: Learning rate mới (0.0 - 1.0)
        """
        self.learning_rate = max(0.0, min(1.0, learning_rate))
        logger.debug(f"Learning rate: {self.learning_rate}")
    
    def set_threshold(self, threshold: int) -> None:
        """
        Thay đổi threshold.
        
        Args:
            threshold: Threshold mới
        """
        self.threshold = threshold
        logger.debug(f"Threshold: {self.threshold}")