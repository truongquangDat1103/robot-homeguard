"""
Decision Maker - Hệ thống ra quyết định cho robot.
Quyết định hành động dựa trên context, emotion, và priority.
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time
from loguru import logger

from src.utils.constants import Priority, BehaviorState, Emotion


class ActionType(str, Enum):
    """Các loại actions robot có thể thực hiện."""
    SPEAK = "speak"
    MOVE = "move"
    GESTURE = "gesture"
    LOOK_AT = "look_at"
    PLAY_SOUND = "play_sound"
    CONTROL_DEVICE = "control_device"
    WAIT = "wait"
    ASK_CLARIFICATION = "ask_clarification"


@dataclass
class Action:
    """Đại diện cho một action."""
    action_type: ActionType
    parameters: Dict[str, Any]
    priority: Priority = Priority.MEDIUM
    estimated_duration: float = 1.0  # giây
    can_interrupt: bool = False
    
    def __post_init__(self):
        """Post init để set timestamp."""
        self.created_at = time.time()


@dataclass
class DecisionContext:
    """Context để ra quyết định."""
    current_state: BehaviorState
    current_emotion: Emotion
    user_intent: Optional[str] = None
    user_sentiment: Optional[str] = None
    entities: Optional[Dict] = None
    environment: Optional[Dict] = None  # Thông tin môi trường
    history: Optional[List] = None  # Lịch sử actions


class DecisionMaker:
    """
    Hệ thống ra quyết định cho robot.
    """
    
    def __init__(self):
        """Khởi tạo Decision Maker."""
        # Action queue (priority-based)
        self.action_queue: List[Action] = []
        
        # Current action
        self.current_action: Optional[Action] = None
        
        # Decision rules
        self.rules: List[Dict] = []
        
        # Statistics
        self.decisions_made = 0
        self.actions_completed = 0
        
        # Setup default rules
        self._setup_default_rules()
        
        logger.info("Decision Maker đã khởi tạo")
    
    def _setup_default_rules(self) -> None:
        """Setup các rules mặc định."""
        # Rule: Khi confused, ask clarification
        self.add_rule(
            condition=lambda ctx: ctx.current_emotion == Emotion.CONFUSED,
            action_type=ActionType.ASK_CLARIFICATION,
            priority=Priority.HIGH
        )
        
        # Rule: Khi happy, speak với positive tone
        self.add_rule(
            condition=lambda ctx: ctx.current_emotion == Emotion.HAPPY,
            action_type=ActionType.GESTURE,
            priority=Priority.LOW
        )
        
        logger.debug("Đã setup default rules")
    
    def add_rule(
        self,
        condition: callable,
        action_type: ActionType,
        priority: Priority = Priority.MEDIUM,
        parameters: Optional[Dict] = None
    ) -> None:
        """
        Thêm decision rule.
        
        Args:
            condition: Function kiểm tra điều kiện
            action_type: Loại action
            priority: Priority
            parameters: Parameters cho action
        """
        rule = {
            'condition': condition,
            'action_type': action_type,
            'priority': priority,
            'parameters': parameters or {}
        }
        self.rules.append(rule)
    
    def decide(self, context: DecisionContext) -> Optional[Action]:
        """
        Ra quyết định dựa trên context.
        
        Args:
            context: Decision context
            
        Returns:
            Action cần thực hiện hoặc None
        """
        self.decisions_made += 1
        
        # Kiểm tra các rules
        for rule in self.rules:
            try:
                if rule['condition'](context):
                    action = Action(
                        action_type=rule['action_type'],
                        parameters=rule['parameters'],
                        priority=rule['priority']
                    )
                    
                    logger.debug(f"Rule matched: {action.action_type.value}")
                    return action
            except Exception as e:
                logger.error(f"Lỗi check rule: {e}")
        
        # Nếu không có rule match, decide based on intent
        if context.user_intent:
            return self._decide_from_intent(context)
        
        return None
    
    def _decide_from_intent(self, context: DecisionContext) -> Optional[Action]:
        """
        Quyết định dựa trên user intent.
        
        Args:
            context: Context
            
        Returns:
            Action
        """
        intent = context.user_intent
        entities = context.entities or {}
        
        # Intent-to-action mapping
        if intent == "greeting":
            return Action(
                action_type=ActionType.SPEAK,
                parameters={'text': 'Xin chào!'},
                priority=Priority.HIGH
            )
        
        elif intent == "question":
            return Action(
                action_type=ActionType.SPEAK,
                parameters={'text': 'Để tôi suy nghĩ...'},
                priority=Priority.HIGH
            )
        
        elif intent == "command":
            # Nếu có device entity
            if 'device' in entities:
                return Action(
                    action_type=ActionType.CONTROL_DEVICE,
                    parameters={
                        'device': entities['device'],
                        'action': entities.get('action', 'toggle')
                    },
                    priority=Priority.HIGH
                )
        
        elif intent == "farewell":
            return Action(
                action_type=ActionType.SPEAK,
                parameters={'text': 'Tạm biệt!'},
                priority=Priority.MEDIUM
            )
        
        # Default: speak
        return Action(
            action_type=ActionType.SPEAK,
            parameters={'text': 'Tôi hiểu rồi.'},
            priority=Priority.LOW
        )
    
    def queue_action(self, action: Action) -> None:
        """
        Thêm action vào queue.
        
        Args:
            action: Action cần queue
        """
        self.action_queue.append(action)
        
        # Sort by priority
        self.action_queue.sort(key=lambda a: a.priority.value)
        
        logger.info(f"Queued action: {action.action_type.value} (priority: {action.priority.value})")
    
    def get_next_action(self) -> Optional[Action]:
        """
        Lấy action tiếp theo từ queue.
        
        Returns:
            Action hoặc None
        """
        if not self.action_queue:
            return None
        
        # Lấy action có priority cao nhất
        action = self.action_queue.pop(0)
        self.current_action = action
        
        logger.info(f"▶️  Executing action: {action.action_type.value}")
        return action
    
    def complete_current_action(self) -> None:
        """Đánh dấu action hiện tại đã hoàn thành."""
        if self.current_action:
            self.actions_completed += 1
            logger.debug(f"✅ Action completed: {self.current_action.action_type.value}")
            self.current_action = None
    
    def can_interrupt_current(self, new_action: Action) -> bool:
        """
        Kiểm tra có thể interrupt action hiện tại không.
        
        Args:
            new_action: Action mới
            
        Returns:
            True nếu có thể interrupt
        """
        if not self.current_action:
            return True
        
        # High priority có thể interrupt
        if new_action.priority.value < self.current_action.priority.value:
            return True
        
        # Action hiện tại cho phép interrupt
        if self.current_action.can_interrupt:
            return True
        
        return False
    
    def interrupt_current_action(self, new_action: Action) -> bool:
        """
        Interrupt action hiện tại.
        
        Args:
            new_action: Action mới
            
        Returns:
            True nếu interrupt thành công
        """
        if not self.can_interrupt_current(new_action):
            logger.warning("Không thể interrupt action hiện tại")
            return False
        
        # Push current action back to queue
        if self.current_action:
            logger.info(f"⏸️  Interrupted: {self.current_action.action_type.value}")
            self.action_queue.insert(0, self.current_action)
        
        # Execute new action
        self.current_action = new_action
        logger.info(f"▶️  Executing (interrupt): {new_action.action_type.value}")
        
        return True
    
    def clear_queue(self) -> None:
        """Xóa action queue."""
        self.action_queue.clear()
        logger.info("Action queue đã xóa")
    
    def has_pending_actions(self) -> bool:
        """Kiểm tra có actions đang chờ không."""
        return len(self.action_queue) > 0
    
    def get_queue_size(self) -> int:
        """Lấy số lượng actions trong queue."""
        return len(self.action_queue)
    
    def estimate_total_time(self) -> float:
        """
        Ước tính tổng thời gian để hoàn thành tất cả actions.
        
        Returns:
            Thời gian (giây)
        """
        total = sum(action.estimated_duration for action in self.action_queue)
        
        if self.current_action:
            total += self.current_action.estimated_duration
        
        return total
    
    def get_info(self) -> dict:
        """
        Lấy thông tin decision maker.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "decisions_made": self.decisions_made,
            "actions_completed": self.actions_completed,
            "queue_size": self.get_queue_size(),
            "current_action": self.current_action.action_type.value if self.current_action else None,
            "estimated_time_remaining": self.estimate_total_time(),
            "rules_count": len(self.rules)
        }