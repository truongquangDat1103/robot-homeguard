"""
Pose Estimator - Ước lượng tư thế con người.
Sử dụng MediaPipe Pose hoặc OpenPose.
"""
from typing import List, Dict, Tuple, Optional
import cv2
import numpy as np
from loguru import logger


try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("⚠️  MediaPipe chưa cài đặt")


class Keypoint:
    """Đại diện cho một keypoint (điểm khớp)."""
    
    def __init__(
        self,
        name: str,
        position: Tuple[int, int],
        confidence: float,
        visibility: float = 1.0
    ):
        """
        Khởi tạo Keypoint.
        
        Args:
            name: Tên keypoint (nose, left_shoulder, ...)
            position: Vị trí (x, y)
            confidence: Độ tin cậy
            visibility: Độ rõ ràng (0.0 - 1.0)
        """
        self.name = name
        self.position = position
        self.confidence = confidence
        self.visibility = visibility
    
    @property
    def x(self) -> int:
        return self.position[0]
    
    @property
    def y(self) -> int:
        return self.position[1]


class Pose:
    """Đại diện cho tư thế của một người."""
    
    def __init__(self, keypoints: List[Keypoint]):
        """
        Khởi tạo Pose.
        
        Args:
            keypoints: Danh sách các keypoints
        """
        self.keypoints = keypoints
        self._keypoint_dict = {kp.name: kp for kp in keypoints}
    
    def get_keypoint(self, name: str) -> Optional[Keypoint]:
        """
        Lấy keypoint theo tên.
        
        Args:
            name: Tên keypoint
            
        Returns:
            Keypoint hoặc None
        """
        return self._keypoint_dict.get(name)
    
    def get_all_keypoints(self) -> List[Keypoint]:
        """Lấy tất cả keypoints."""
        return self.keypoints.copy()
    
    def get_visible_keypoints(self, min_visibility: float = 0.5) -> List[Keypoint]:
        """
        Lấy các keypoints có visibility cao.
        
        Args:
            min_visibility: Ngưỡng visibility tối thiểu
            
        Returns:
            List keypoints
        """
        return [kp for kp in self.keypoints if kp.visibility >= min_visibility]


class PoseEstimator:
    """
    Ước lượng tư thế con người sử dụng MediaPipe.
    """
    
    # MediaPipe keypoint names
    KEYPOINT_NAMES = [
        "nose", "left_eye_inner", "left_eye", "left_eye_outer",
        "right_eye_inner", "right_eye", "right_eye_outer",
        "left_ear", "right_ear", "mouth_left", "mouth_right",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_pinky", "right_pinky",
        "left_index", "right_index", "left_thumb", "right_thumb",
        "left_hip", "right_hip", "left_knee", "right_knee",
        "left_ankle", "right_ankle", "left_heel", "right_heel",
        "left_foot_index", "right_foot_index"
    ]
    
    # Connections cho vẽ skeleton
    CONNECTIONS = [
        # Face
        ("left_eye", "right_eye"),
        ("left_eye", "nose"),
        ("right_eye", "nose"),
        ("left_ear", "left_eye"),
        ("right_ear", "right_eye"),
        
        # Body
        ("left_shoulder", "right_shoulder"),
        ("left_shoulder", "left_elbow"),
        ("left_elbow", "left_wrist"),
        ("right_shoulder", "right_elbow"),
        ("right_elbow", "right_wrist"),
        ("left_shoulder", "left_hip"),
        ("right_shoulder", "right_hip"),
        ("left_hip", "right_hip"),
        
        # Legs
        ("left_hip", "left_knee"),
        ("left_knee", "left_ankle"),
        ("right_hip", "right_knee"),
        ("right_knee", "right_ankle"),
    ]
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_complexity: int = 1
    ):
        """
        Khởi tạo pose estimator.
        
        Args:
            min_detection_confidence: Ngưỡng confidence cho detection
            min_tracking_confidence: Ngưỡng confidence cho tracking
            model_complexity: Độ phức tạp model (0, 1, hoặc 2)
        """
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError("MediaPipe chưa được cài đặt. Cài: pip install mediapipe")
        
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.model_complexity = model_complexity
        
        # Khởi tạo MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        logger.info("Pose estimator đã khởi tạo")
    
    def estimate(self, frame: np.ndarray) -> Optional[Pose]:
        """
        Ước lượng tư thế từ frame.
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            Pose object hoặc None
        """
        if frame is None or frame.size == 0:
            return None
        
        try:
            # Convert BGR sang RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process
            results = self.pose.process(rgb_frame)
            
            if not results.pose_landmarks:
                return None
            
            # Parse keypoints
            keypoints = self._parse_keypoints(results.pose_landmarks, frame.shape)
            
            return Pose(keypoints)
            
        except Exception as e:
            logger.error(f"Lỗi estimate pose: {e}")
            return None
    
    def _parse_keypoints(
        self,
        landmarks,
        frame_shape: Tuple[int, int, int]
    ) -> List[Keypoint]:
        """
        Parse MediaPipe landmarks thành Keypoints.
        
        Args:
            landmarks: MediaPipe pose landmarks
            frame_shape: Shape của frame (h, w, c)
            
        Returns:
            List Keypoints
        """
        h, w = frame_shape[:2]
        keypoints = []
        
        for idx, landmark in enumerate(landmarks.landmark):
            if idx >= len(self.KEYPOINT_NAMES):
                break
            
            # Convert normalized coordinates sang pixel coordinates
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            
            keypoint = Keypoint(
                name=self.KEYPOINT_NAMES[idx],
                position=(x, y),
                confidence=landmark.visibility,
                visibility=landmark.visibility
            )
            
            keypoints.append(keypoint)
        
        return keypoints
    
    def draw_pose(
        self,
        frame: np.ndarray,
        pose: Pose,
        draw_keypoints: bool = True,
        draw_skeleton: bool = True,
        keypoint_color: Tuple[int, int, int] = (0, 255, 0),
        skeleton_color: Tuple[int, int, int] = (255, 0, 0)
    ) -> np.ndarray:
        """
        Vẽ pose lên frame.
        
        Args:
            frame: Input frame
            pose: Pose object
            draw_keypoints: Vẽ keypoints hay không
            draw_skeleton: Vẽ skeleton hay không
            keypoint_color: Màu keypoints (BGR)
            skeleton_color: Màu skeleton (BGR)
            
        Returns:
            Frame đã vẽ
        """
        output = frame.copy()
        
        # Vẽ skeleton (connections)
        if draw_skeleton:
            for start_name, end_name in self.CONNECTIONS:
                start_kp = pose.get_keypoint(start_name)
                end_kp = pose.get_keypoint(end_name)
                
                if start_kp and end_kp:
                    # Chỉ vẽ nếu cả 2 keypoints đều visible
                    if start_kp.visibility > 0.5 and end_kp.visibility > 0.5:
                        cv2.line(
                            output,
                            start_kp.position,
                            end_kp.position,
                            skeleton_color,
                            2
                        )
        
        # Vẽ keypoints
        if draw_keypoints:
            for keypoint in pose.get_visible_keypoints(min_visibility=0.5):
                cv2.circle(
                    output,
                    keypoint.position,
                    5,
                    keypoint_color,
                    -1
                )
                
                # Vẽ tên keypoint (optional)
                cv2.putText(
                    output,
                    keypoint.name,
                    (keypoint.x + 10, keypoint.y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    keypoint_color,
                    1
                )
        
        return output
    
    def get_body_angle(
        self,
        pose: Pose,
        point1_name: str,
        point2_name: str,
        point3_name: str
    ) -> Optional[float]:
        """
        Tính góc giữa 3 điểm (point1 -> point2 -> point3).
        
        Args:
            pose: Pose object
            point1_name: Tên keypoint 1
            point2_name: Tên keypoint 2 (đỉnh góc)
            point3_name: Tên keypoint 3
            
        Returns:
            Góc (degrees) hoặc None
        """
        kp1 = pose.get_keypoint(point1_name)
        kp2 = pose.get_keypoint(point2_name)
        kp3 = pose.get_keypoint(point3_name)
        
        if not (kp1 and kp2 and kp3):
            return None
        
        # Tính vectors
        v1 = np.array([kp1.x - kp2.x, kp1.y - kp2.y])
        v2 = np.array([kp3.x - kp2.x, kp3.y - kp2.y])
        
        # Tính góc
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
        
        return float(angle)
    
    def detect_gesture(self, pose: Pose) -> str:
        """
        Phát hiện cử chỉ đơn giản.
        
        Args:
            pose: Pose object
            
        Returns:
            Tên gesture ("hands_up", "waving", "standing", ...)
        """
        # Lấy keypoints cần thiết
        left_wrist = pose.get_keypoint("left_wrist")
        right_wrist = pose.get_keypoint("right_wrist")
        left_shoulder = pose.get_keypoint("left_shoulder")
        right_shoulder = pose.get_keypoint("right_shoulder")
        nose = pose.get_keypoint("nose")
        
        if not all([left_wrist, right_wrist, left_shoulder, right_shoulder, nose]):
            return "unknown"
        
        # Hands up (cả 2 tay giơ cao)
        if (left_wrist.y < nose.y and right_wrist.y < nose.y):
            return "hands_up"
        
        # Waving (1 tay giơ cao)
        elif left_wrist.y < left_shoulder.y or right_wrist.y < right_shoulder.y:
            return "waving"
        
        # Standing normally
        else:
            return "standing"
    
    def is_sitting(self, pose: Pose) -> bool:
        """
        Kiểm tra xem người có đang ngồi không.
        
        Args:
            pose: Pose object
            
        Returns:
            True nếu đang ngồi
        """
        left_hip = pose.get_keypoint("left_hip")
        right_hip = pose.get_keypoint("right_hip")
        left_knee = pose.get_keypoint("left_knee")
        right_knee = pose.get_keypoint("right_knee")
        
        if not all([left_hip, right_hip, left_knee, right_knee]):
            return False
        
        # Tính góc knee
        left_knee_angle = self.get_body_angle(pose, "left_hip", "left_knee", "left_ankle")
        right_knee_angle = self.get_body_angle(pose, "right_hip", "right_knee", "right_ankle")
        
        if left_knee_angle and right_knee_angle:
            # Nếu góc gối < 120 độ thì có thể đang ngồi
            return (left_knee_angle < 120 or right_knee_angle < 120)
        
        return False
    
    def is_standing(self, pose: Pose) -> bool:
        """
        Kiểm tra xem người có đang đứng không.
        
        Args:
            pose: Pose object
            
        Returns:
            True nếu đang đứng
        """
        # Lấy keypoints
        left_hip = pose.get_keypoint("left_hip")
        left_knee = pose.get_keypoint("left_knee")
        left_ankle = pose.get_keypoint("left_ankle")
        
        if not all([left_hip, left_knee, left_ankle]):
            return False
        
        # Kiểm tra các keypoints gần như thẳng hàng (đứng thẳng)
        hip_knee_dist = abs(left_hip.x - left_knee.x)
        knee_ankle_dist = abs(left_knee.x - left_ankle.x)
        
        # Nếu khoảng cách x nhỏ -> đang đứng thẳng
        return (hip_knee_dist < 50 and knee_ankle_dist < 50)
    
    def get_center_of_mass(self, pose: Pose) -> Optional[Tuple[int, int]]:
        """
        Tính center of mass (trọng tâm) của pose.
        
        Args:
            pose: Pose object
            
        Returns:
            (x, y) của center of mass
        """
        visible_keypoints = pose.get_visible_keypoints(min_visibility=0.5)
        
        if not visible_keypoints:
            return None
        
        # Tính trung bình vị trí
        x_sum = sum(kp.x for kp in visible_keypoints)
        y_sum = sum(kp.y for kp in visible_keypoints)
        
        count = len(visible_keypoints)
        
        return (x_sum // count, y_sum // count)
    
    def release(self) -> None:
        """Giải phóng resources."""
        if hasattr(self, 'pose'):
            self.pose.close()
        logger.info("Pose estimator đã release")
    
    def __del__(self):
        """Destructor."""
        self.release()