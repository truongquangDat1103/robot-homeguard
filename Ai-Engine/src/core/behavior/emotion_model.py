"""
Emotion Model - Mô hình cảm xúc của robot.
Mô phỏng và quản lý cảm xúc dựa trên các tác động bên ngoài.
"""
import time
from typing import Dict, Optional, List
from loguru import logger

from src.utils.constants import Emotion


class EmotionState:
    """Trạng thái cảm xúc tại một thời điểm."""
    
    def __init__(
        self,
        emotion: Emotion,
        intensity: float,
        valence: float,  # Tích cực/tiêu cực (-1.0 đến 1.0)
        arousal: float   # Năng lượng/kích thích (0.0 đến 1.0)
    ):
        """
        Khởi tạo EmotionState.
        
        Args:
            emotion: Loại emotion
            intensity: Cường độ (0.0 - 1.0)
            valence: Giá trị tích cực/tiêu cực
            arousal: Mức độ kích thích
        """
        self.emotion = emotion
        self.intensity = max(0.0, min(1.0, intensity))
        self.valence = max(-1.0, min(1.0, valence))
        self.arousal = max(0.0, min(1.0, arousal))
        self.timestamp = time.time()


class EmotionTrigger:
    """Trigger gây ra thay đổi cảm xúc."""
    
    def __init__(
        self,
        trigger_type: str,
        valence_delta: float,
        arousal_delta: float,
        duration: float = 5.0
    ):
        """
        Khởi tạo EmotionTrigger.
        
        Args:
            trigger_type: Loại trigger
            valence_delta: Thay đổi valence
            arousal_delta: Thay đổi arousal
            duration: Thời gian ảnh hưởng (giây)
        """
        self.trigger_type = trigger_type
        self.valence_delta = valence_delta
        self.arousal_delta = arousal_delta
        self.duration = duration
        self.created_at = time.time()
    
    def is_expired(self) -> bool:
        """Kiểm tra trigger đã hết hạn chưa."""
        return time.time() - self.created_at > self.duration


class EmotionModel:
    """
    Mô hình cảm xúc của robot dựa trên Circumplex Model.
    Sử dụng 2 chiều: Valence (tích cực/tiêu cực) và Arousal (kích thích).
    """
    
    # Emotion mapping (valence, arousal)
    EMOTION_MAP = {
        Emotion.HAPPY: (0.8, 0.7),      # Tích cực, kích thích cao
        Emotion.EXCITED: (0.9, 0.9),    # Rất tích cực, rất kích thích
        Emotion.NEUTRAL: (0.0, 0.3),    # Trung tính, kích thích thấp
        Emotion.CURIOUS: (0.5, 0.6),    # Hơi tích cực, kích thích trung bình
        Emotion.SAD: (-0.7, 0.3),       # Tiêu cực, kích thích thấp
        Emotion.AFRAID: (-0.6, 0.8),    # Tiêu cực, kích thích cao
        Emotion.ANGRY: (-0.8, 0.9),     # Rất tiêu cực, rất kích thích
        Emotion.CONFUSED: (-0.2, 0.5),  # Hơi tiêu cực, kích thích trung bình
        Emotion.SURPRISED: (0.3, 0.8),  # Hơi tích cực, kích thích cao
    }
    
    def __init__(
        self,
        initial_emotion: Emotion = Emotion.NEUTRAL,
        decay_rate: float = 0.1
    ):
        """
        Khởi tạo Emotion Model.
        
        Args:
            initial_emotion: Emotion khởi đầu
            decay_rate: Tốc độ giảm cường độ emotion
        """
        self.decay_rate = decay_rate
        
        # Current emotion state
        valence, arousal = self.EMOTION_MAP[initial_emotion]
        self.current_state = EmotionState(
            emotion=initial_emotion,
            intensity=0.5,
            valence=valence,
            arousal=arousal
        )
        
        # Active triggers
        self.active_triggers: List[EmotionTrigger] = []
        
        # Emotion history
        self.emotion_history: List[EmotionState] = []
        self.max_history = 50
        
        # Personality traits (ảnh hưởng đến emotion)
        self.personality_traits = {
            'openness': 0.7,      # Độ cởi mở
            'friendliness': 0.8,  # Độ thân thiện
            'patience': 0.6,      # Độ kiên nhẫn
            'curiosity': 0.7,     # Độ tò mò
            'sensitivity': 0.5    # Độ nhạy cảm
        }
        
        logger.info(f"Emotion Model đã khởi tạo (emotion: {initial_emotion.value})")
    
    def apply_trigger(
        self,
        trigger_type: str,
        valence_delta: float,
        arousal_delta: float,
        duration: float = 5.0
    ) -> None:
        """
        Áp dụng emotion trigger.
        
        Args:
            trigger_type: Loại trigger
            valence_delta: Thay đổi valence
            arousal_delta: Thay đổi arousal
            duration: Thời gian ảnh hưởng
        """
        trigger = EmotionTrigger(trigger_type, valence_delta, arousal_delta, duration)
        self.active_triggers.append(trigger)
        
        logger.debug(f"Applied trigger: {trigger_type} (v:{valence_delta:+.2f}, a:{arousal_delta:+.2f})")
        
        # Update emotion ngay lập tức
        self.update()
    
    def update(self) -> None:
        """Cập nhật emotion state dựa trên triggers."""
        # Loại bỏ expired triggers
        self.active_triggers = [t for t in self.active_triggers if not t.is_expired()]
        
        # Tính total delta từ tất cả triggers
        valence_delta = sum(t.valence_delta for t in self.active_triggers)
        arousal_delta = sum(t.arousal_delta for t in self.active_triggers)
        
        # Apply personality modifiers
        valence_delta *= self.personality_traits['sensitivity']
        arousal_delta *= (1.0 - self.personality_traits['patience'])
        
        # Update valence và arousal
        new_valence = self.current_state.valence + valence_delta
        new_arousal = self.current_state.arousal + arousal_delta
        
        # Decay về neutral
        new_valence *= (1.0 - self.decay_rate)
        new_arousal = max(0.3, new_arousal * (1.0 - self.decay_rate))
        
        # Clamp values
        new_valence = max(-1.0, min(1.0, new_valence))
        new_arousal = max(0.0, min(1.0, new_arousal))
        
        # Map sang emotion
        new_emotion = self._map_to_emotion(new_valence, new_arousal)
        
        # Tính intensity
        intensity = (abs(new_valence) + new_arousal) / 2.0
        
        # Check nếu emotion thay đổi
        if new_emotion != self.current_state.emotion:
            logger.info(
                f"😊 Emotion: {self.current_state.emotion.value} -> {new_emotion.value} "
                f"(v:{new_valence:.2f}, a:{new_arousal:.2f})"
            )
        
        # Update state
        self.current_state = EmotionState(
            emotion=new_emotion,
            intensity=intensity,
            valence=new_valence,
            arousal=new_arousal
        )
        
        # Add to history
        self.emotion_history.append(self.current_state)
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)
    
    def _map_to_emotion(self, valence: float, arousal: float) -> Emotion:
        """
        Map valence/arousal sang Emotion.
        
        Args:
            valence: Giá trị valence
            arousal: Giá trị arousal
            
        Returns:
            Emotion tương ứng
        """
        # Tính khoảng cách đến từng emotion
        min_distance = float('inf')
        closest_emotion = Emotion.NEUTRAL
        
        for emotion, (target_v, target_a) in self.EMOTION_MAP.items():
            distance = ((valence - target_v) ** 2 + (arousal - target_a) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_emotion = emotion
        
        return closest_emotion
    
    def trigger_positive_event(self, intensity: float = 0.5) -> None:
        """
        Trigger positive event (praise, success, ...).
        
        Args:
            intensity: Cường độ
        """
        self.apply_trigger(
            trigger_type="positive_event",
            valence_delta=0.3 * intensity,
            arousal_delta=0.2 * intensity,
            duration=10.0
        )
    
    def trigger_negative_event(self, intensity: float = 0.5) -> None:
        """
        Trigger negative event (criticism, failure, ...).
        
        Args:
            intensity: Cường độ
        """
        self.apply_trigger(
            trigger_type="negative_event",
            valence_delta=-0.3 * intensity,
            arousal_delta=0.1 * intensity,
            duration=15.0
        )
    
    def trigger_surprise(self, intensity: float = 0.7) -> None:
        """Trigger surprise event."""
        self.apply_trigger(
            trigger_type="surprise",
            valence_delta=0.1,
            arousal_delta=0.5 * intensity,
            duration=5.0
        )
    
    def trigger_confusion(self, intensity: float = 0.5) -> None:
        """Trigger confusion."""
        self.apply_trigger(
            trigger_type="confusion",
            valence_delta=-0.2 * intensity,
            arousal_delta=0.3 * intensity,
            duration=8.0
        )
    
    def get_current_emotion(self) -> Emotion:
        """Lấy emotion hiện tại."""
        return self.current_state.emotion
    
    def get_emotion_intensity(self) -> float:
        """Lấy cường độ emotion."""
        return self.current_state.intensity
    
    def get_emotion_description(self) -> str:
        """
        Lấy mô tả emotion hiện tại.
        
        Returns:
            Mô tả text
        """
        emotion = self.current_state.emotion
        intensity = self.current_state.intensity
        
        if intensity < 0.3:
            level = "nhẹ"
        elif intensity < 0.7:
            level = "trung bình"
        else:
            level = "mạnh"
        
        return f"{emotion.value} ({level})"
    
    def set_personality_trait(self, trait: str, value: float) -> None:
        """
        Set personality trait.
        
        Args:
            trait: Tên trait
            value: Giá trị (0.0 - 1.0)
        """
        if trait in self.personality_traits:
            self.personality_traits[trait] = max(0.0, min(1.0, value))
            logger.info(f"Personality trait '{trait}' = {value:.2f}")
    
    def get_emotion_history(self, count: int = 10) -> List[EmotionState]:
        """
        Lấy emotion history.
        
        Args:
            count: Số lượng entries
            
        Returns:
            List EmotionStates
        """
        return self.emotion_history[-count:]
    
    def reset(self) -> None:
        """Reset về neutral."""
        valence, arousal = self.EMOTION_MAP[Emotion.NEUTRAL]
        self.current_state = EmotionState(
            emotion=Emotion.NEUTRAL,
            intensity=0.5,
            valence=valence,
            arousal=arousal
        )
        self.active_triggers.clear()
        logger.info("Emotion model đã reset")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin emotion model.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "current_emotion": self.current_state.emotion.value,
            "intensity": self.current_state.intensity,
            "valence": self.current_state.valence,
            "arousal": self.current_state.arousal,
            "active_triggers": len(self.active_triggers),
            "personality": self.personality_traits,
            "description": self.get_emotion_description()
        }