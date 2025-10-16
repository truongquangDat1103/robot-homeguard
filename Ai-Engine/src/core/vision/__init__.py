"""
Vision Module - Computer Vision components.
Các module xử lý hình ảnh và video.
"""

from src.core.vision.camera_manager import CameraManager, CameraSource, CameraState
from src.core.vision.face_detector import FaceDetector, Face
from src.core.vision.face_recognizer import (
    FaceRecognizer,
    FaceEncoding,
    RecognizedFace
)
from src.core.vision.motion_detector import MotionDetector, MotionRegion
from src.core.vision.object_detector import ObjectDetector, DetectedObject
from src.core.vision.pose_estimator import PoseEstimator, Pose, Keypoint


__all__ = [
    # Camera
    "CameraManager",
    "CameraSource",
    "CameraState",
    
    # Face Detection
    "FaceDetector",
    "Face",
    
    # Face Recognition
    "FaceRecognizer",
    "FaceEncoding",
    "RecognizedFace",
    
    # Motion Detection
    "MotionDetector",
    "MotionRegion",
    
    # Object Detection
    "ObjectDetector",
    "DetectedObject",
    
    # Pose Estimation
    "PoseEstimator",
    "Pose",
    "Keypoint",
]   