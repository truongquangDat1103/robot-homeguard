"""
Behavior Engine - Quản lý behavior state machine của robot.
Điều khiển các trạng thái và hành vi của robot.
"""
import time
from typing import Optional, Dict, List, Callable
from enum import Enum
from loguru import logger

from src.utils.constants import BehaviorState, Emotion


class BehaviorTransition:
    """Đại diện cho một transition giữa các states."""
    
    def __init__(
        self,
        from_state: BehaviorState,
        to_state: BehaviorState,
        condition: Optional[Callable] = None,
        action: Optional[Callable] = None
    ):
        """
        Khởi tạo BehaviorTransition.
        
        Args:
            from_state: State nguồn
            to_state: State đích
            condition: Điều kiện để transition (function trả về bool)
            action: Action thực hiện khi transition
        """
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
        self.action = action


class BehaviorEvent:
    """Event trigger behavior change."""
    
    def __init__(
        self,
        event_type: str,
        data: Optional[Dict] = None,
        priority: int = 2
    ):
        """
        Khởi tạo BehaviorEvent.
        
        Args:
            event_type: Loại event
            data: Dữ liệu kèm theo
            priority: Độ ưu tiên (0=highest, 3=lowest)
        """
        self.event_type = event_type
        self.data = data or {}
        self.priority = priority
        self.timestamp = time.time()


class BehaviorEngine:
    """
    Behavior State Machine để quản lý hành vi robot.
    """
    
    def __init__(
        self,
        initial_state: BehaviorState = BehaviorState.IDLE,
        initial_emotion: Emotion = Emotion.NEUTRAL
    ):
        """
        Khởi tạo Behavior Engine.
        
        Args:
            initial_state: State khởi đầu
            initial_emotion: Emotion khởi đầu
        """
        self.current_state = initial_state
        self.previous_state: Optional[BehaviorState] = None
        
        # Emotion state
        self.current_emotion = initial_emotion
        self.emotion_intensity = 0.5  # 0.0 - 1.0
        
        # Transitions
        self.transitions: List[BehaviorTransition] = []
        
        # State callbacks
        self.state_enter_callbacks: Dict[BehaviorState, List[Callable]] = {}
        self.state_exit_callbacks: Dict[BehaviorState, List[Callable]] = {}
        
        # Event queue
        self.event_queue: List[BehaviorEvent] = []
        
        # Statistics
        self.state_change_count = 0
        self.last_state_change = time.time()
        
        # Setup default transitions
        self._setup_default_transitions()
        
        logger.info(f"Behavior Engine đã khởi tạo (state: {initial_state.value})")
    
    def _setup_default_transitions(self) -> None:
        """Setup các transitions mặc định."""
        # IDLE -> LISTENING (khi có input)
        self.add_transition(BehaviorState.IDLE, BehaviorState.LISTENING)
        
        # LISTENING -> PROCESSING (khi nhận được speech)
        self.add_transition(BehaviorState.LISTENING, BehaviorState.PROCESSING)
        
        # PROCESSING -> THINKING (khi cần suy nghĩ)
        self.add_transition(BehaviorState.PROCESSING, BehaviorState.THINKING)
        
        # THINKING -> SPEAKING (khi có response)
        self.add_transition(BehaviorState.THINKING, BehaviorState.SPEAKING)
        
        # SPEAKING -> IDLE (sau khi nói xong)
        self.add_transition(BehaviorState.SPEAKING, BehaviorState.IDLE)
        
        # Any state -> ALERT (khi có alert)
        for state in BehaviorState:
            if state != BehaviorState.ALERT:
                self.add_transition(state, BehaviorState.ALERT)
        
        # ALERT -> IDLE (sau khi xử lý xong alert)
        self.add_transition(BehaviorState.ALERT, BehaviorState.IDLE)
        
        # Any state -> ERROR (khi có lỗi)
        for state in BehaviorState:
            if state != BehaviorState.ERROR:
                self.add_transition(state, BehaviorState.ERROR)
        
        logger.debug("Đã setup default transitions")
    
    def add_transition(
        self,
        from_state: BehaviorState,
        to_state: BehaviorState,
        condition: Optional[Callable] = None,
        action: Optional[Callable] = None
    ) -> None:
        """
        Thêm transition mới.
        
        Args:
            from_state: State nguồn
            to_state: State đích
            condition: Điều kiện
            action: Action khi transition
        """
        transition = BehaviorTransition(from_state, to_state, condition, action)
        self.transitions.append(transition)
    
    def change_state(
        self,
        new_state: BehaviorState,
        reason: Optional[str] = None
    ) -> bool:
        """
        Thay đổi state.
        
        Args:
            new_state: State mới
            reason: Lý do thay đổi
            
        Returns:
            True nếu thay đổi thành công
        """
        if new_state == self.current_state:
            logger.debug(f"State không đổi: {new_state.value}")
            return False
        
        # Kiểm tra có transition hợp lệ không
        if not self._is_valid_transition(self.current_state, new_state):
            logger.warning(f"Transition không hợp lệ: {self.current_state.value} -> {new_state.value}")
            return False
        
        # Exit callbacks
        self._trigger_exit_callbacks(self.current_state)
        
        # Update states
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Statistics
        self.state_change_count += 1
        self.last_state_change = time.time()
        
        logger.info(
            f"🔄 State changed: {self.previous_state.value} -> {new_state.value}"
            + (f" (reason: {reason})" if reason else "")
        )
        
        # Enter callbacks
        self._trigger_enter_callbacks(new_state)
        
        return True
    
    def _is_valid_transition(
        self,
        from_state: BehaviorState,
        to_state: BehaviorState
    ) -> bool:
        """Kiểm tra transition có hợp lệ không."""
        for transition in self.transitions:
            if transition.from_state == from_state and transition.to_state == to_state:
                # Kiểm tra condition nếu có
                if transition.condition:
                    return transition.condition()
                return True
        return False
    
    def _trigger_enter_callbacks(self, state: BehaviorState) -> None:
        """Trigger callbacks khi enter state."""
        callbacks = self.state_enter_callbacks.get(state, [])
        for callback in callbacks:
            try:
                callback(state)
            except Exception as e:
                logger.error(f"Lỗi enter callback: {e}")
    
    def _trigger_exit_callbacks(self, state: BehaviorState) -> None:
        """Trigger callbacks khi exit state."""
        callbacks = self.state_exit_callbacks.get(state, [])
        for callback in callbacks:
            try:
                callback(state)
            except Exception as e:
                logger.error(f"Lỗi exit callback: {e}")
    
    def register_state_enter(
        self,
        state: BehaviorState,
        callback: Callable
    ) -> None:
        """
        Đăng ký callback khi enter state.
        
        Args:
            state: State
            callback: Callback function
        """
        if state not in self.state_enter_callbacks:
            self.state_enter_callbacks[state] = []
        self.state_enter_callbacks[state].append(callback)
    
    def register_state_exit(
        self,
        state: BehaviorState,
        callback: Callable
    ) -> None:
        """
        Đăng ký callback khi exit state.
        
        Args:
            state: State
            callback: Callback function
        """
        if state not in self.state_exit_callbacks:
            self.state_exit_callbacks[state] = []
        self.state_exit_callbacks[state].append(callback)
    
    def post_event(self, event: BehaviorEvent) -> None:
        """
        Post event vào queue.
        
        Args:
            event: BehaviorEvent
        """
        self.event_queue.append(event)
        # Sort by priority
        self.event_queue.sort(key=lambda e: e.priority)
        logger.debug(f"Posted event: {event.event_type}")
    
    def process_events(self) -> None:
        """Xử lý các events trong queue."""
        while self.event_queue:
            event = self.event_queue.pop(0)
            self._handle_event(event)
    
    def _handle_event(self, event: BehaviorEvent) -> None:
        """
        Xử lý một event.
        
        Args:
            event: Event cần xử lý
        """
        logger.debug(f"Handling event: {event.event_type}")
        
        # Event-to-state mapping
        event_state_map = {
            'speech_detected': BehaviorState.LISTENING,
            'speech_end': BehaviorState.PROCESSING,
            'thinking': BehaviorState.THINKING,
            'response_ready': BehaviorState.SPEAKING,
            'speaking_done': BehaviorState.IDLE,
            'alert': BehaviorState.ALERT,
            'error': BehaviorState.ERROR,
        }
        
        if event.event_type in event_state_map:
            target_state = event_state_map[event.event_type]
            self.change_state(target_state, reason=event.event_type)
    
    def get_current_state(self) -> BehaviorState:
        """Lấy state hiện tại."""
        return self.current_state
    
    def get_current_emotion(self) -> Emotion:
        """Lấy emotion hiện tại."""
        return self.current_emotion
    
    def set_emotion(
        self,
        emotion: Emotion,
        intensity: float = 0.5
    ) -> None:
        """
        Set emotion.
        
        Args:
            emotion: Emotion mới
            intensity: Cường độ (0.0 - 1.0)
        """
        self.current_emotion = emotion
        self.emotion_intensity = max(0.0, min(1.0, intensity))
        logger.info(f"😊 Emotion changed: {emotion.value} (intensity: {intensity:.2f})")
    
    def is_busy(self) -> bool:
        """Kiểm tra robot có đang bận không."""
        busy_states = [
            BehaviorState.LISTENING,
            BehaviorState.PROCESSING,
            BehaviorState.THINKING,
            BehaviorState.SPEAKING
        ]
        return self.current_state in busy_states
    
    def is_idle(self) -> bool:
        """Kiểm tra robot có đang idle không."""
        return self.current_state == BehaviorState.IDLE
    
    def reset(self) -> None:
        """Reset về state ban đầu."""
        self.change_state(BehaviorState.IDLE, reason="reset")
        self.current_emotion = Emotion.NEUTRAL
        self.emotion_intensity = 0.5
        self.event_queue.clear()
        logger.info("Behavior Engine đã reset")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin behavior engine.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "current_emotion": self.current_emotion.value,
            "emotion_intensity": self.emotion_intensity,
            "is_busy": self.is_busy(),
            "state_change_count": self.state_change_count,
            "event_queue_size": len(self.event_queue),
            "time_in_current_state": time.time() - self.last_state_change
        }