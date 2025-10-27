"""
Behavior Module - Robot Behavior Intelligence.
Các module quản lý hành vi, cảm xúc và tính cách của robot.
"""

from src.core.behavior.behavior_engine import (
    BehaviorEngine,
    BehaviorTransition,
    BehaviorEvent
)
from src.core.behavior.emotion_model import (
    EmotionModel,
    EmotionState,
    EmotionTrigger
)
from src.core.behavior.decision_maker import (
    DecisionMaker,
    Action,
    ActionType,
    DecisionContext
)
from src.core.behavior.personality import Personality, PersonalityTrait


__all__ = [
    # Behavior Engine
    "BehaviorEngine",
    "BehaviorTransition",
    "BehaviorEvent",
    
    # Emotion Model
    "EmotionModel",
    "EmotionState",
    "EmotionTrigger",
    
    # Decision Making
    "DecisionMaker",
    "Action",
    "ActionType",
    "DecisionContext",
    
    # Personality
    "Personality",
    "PersonalityTrait",
]