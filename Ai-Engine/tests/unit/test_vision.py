"""
Unit tests cho Vision module.
"""
import pytest
import numpy as np

from src.core.vision import FaceDetector, Face


class TestFaceDetector:
    """Test FaceDetector class."""
    
    def test_initialization(self):
        """Test khởi tạo detector."""
        detector = FaceDetector(method="haar")
        assert detector is not None
        assert detector.method == "haar"
    
    def test_detect_faces_empty_frame(self):
        """Test detect với frame rỗng."""
        detector = FaceDetector()
        faces = detector.detect(None)
        assert faces == []
    
    def test_detect_faces_valid_frame(self):
        """Test detect với frame hợp lệ."""
        detector = FaceDetector()
        
        # Tạo fake frame (640x480 màu xám)
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        faces = detector.detect(frame)
        assert isinstance(faces, list)
    
    def test_face_object_properties(self):
        """Test Face object properties."""
        face = Face(bbox=(10, 20, 100, 100), confidence=0.9)
        
        assert face.x == 10
        assert face.y == 20
        assert face.width == 100
        assert face.height == 100
        assert face.area == 10000
        assert face.center == (60, 70)


@pytest.mark.slow
def test_face_detection_with_real_image():
    """Test với ảnh thật (slow test)."""
    # Load ảnh từ fixtures
    # Detect faces
    # Assert results
    pass