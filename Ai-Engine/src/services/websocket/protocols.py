"""
Giao thức truyền tin nhắn, schema của tin nhắn WebSocket.
Định nghĩa cấu trúc các tin nhắn trao đổi với robot.
"""
from typing import Any, Dict, Optional, Union                                             # Để khai báo kiểu dữ liệu rõ ràng, giúp code an toàn, dễ đọc và dễ mở rộng.
from datetime import datetime                                                             # Để xử lý dấu thời gian                                            
from pydantic import BaseModel, Field, field_validator                                    # Để định nghĩa và xác thực mô hình dữ liệu                     
from src.utils.constants import MessageType, BehaviorState, Emotion                                      


class BaseMessage(BaseModel):
    """Cấu trúc cơ bản của tất cả các tin nhắn WebSocket."""
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HeartbeatMessage(BaseMessage):
    """Tin nhắn heartbeat/ping."""
    type: MessageType = MessageType.HEARTBEAT
    data: Dict[str, Any] = Field(default_factory=lambda: {"status": "alive"})


class StatusMessage(BaseMessage):
    """Tin nhắn trạng thái hệ thống."""
    type: MessageType = MessageType.STATUS
    
    class StatusData(BaseModel):
        cpu_usage: float = Field(ge=0.0, le=100.0)
        memory_usage: float = Field(ge=0.0, le=100.0)
        gpu_usage: Optional[float] = Field(None, ge=0.0, le=100.0)
        fps: Optional[float] = None
        active_services: list[str] = Field(default_factory=list)
    
    data: StatusData


class ErrorMessage(BaseMessage):
    """Tin nhắn lỗi."""
    type: MessageType = MessageType.ERROR
    
    class ErrorData(BaseModel):
        error_code: str
        error_message: str
        details: Optional[str] = None
        traceback: Optional[str] = None
    
    data: ErrorData


# ==========================================
# Tin nhắn Vision
# ==========================================

class FrameMessage(BaseMessage):
    """Tin nhắn khung hình video."""
    type: MessageType = MessageType.FRAME
    
    class FrameData(BaseModel):
        frame_id: int
        timestamp: float
        width: int
        height: int
        format: str = "jpeg"  # jpeg, png, base64
        data: str  # Hình ảnh mã hóa Base64
    
    data: FrameData


class FaceDetectedMessage(BaseMessage):
    """Tin nhắn phát hiện khuôn mặt."""
    type: MessageType = MessageType.FACE_DETECTED
    
    class FaceData(BaseModel):
        face_id: str
        bbox: list[int] = Field(min_length=4, max_length=4)  # [x, y, w, h]
        confidence: float = Field(ge=0.0, le=1.0)
        landmarks: Optional[list[list[int]]] = None
    
    data: list[FaceData]


class FaceRecognizedMessage(BaseMessage):
    """Tin nhắn nhận diện khuôn mặt."""
    type: MessageType = MessageType.FACE_RECOGNIZED
    
    class RecognizedFaceData(BaseModel):
        face_id: str
        person_name: str
        confidence: float = Field(ge=0.0, le=1.0)
        bbox: list[int] = Field(min_length=4, max_length=4)
        last_seen: Optional[datetime] = None
    
    data: list[RecognizedFaceData]


class MotionDetectedMessage(BaseMessage):
    """Tin nhắn phát hiện chuyển động."""
    type: MessageType = MessageType.MOTION_DETECTED
    
    class MotionData(BaseModel):
        motion_id: str
        bbox: list[int] = Field(min_length=4, max_length=4)
        area: int
        intensity: float = Field(ge=0.0, le=1.0)
    
    data: list[MotionData]


class ObjectDetectedMessage(BaseMessage):
    """Tin nhắn phát hiện vật thể."""
    type: MessageType = MessageType.OBJECT_DETECTED
    
    class ObjectData(BaseModel):
        object_id: str
        class_name: str
        confidence: float = Field(ge=0.0, le=1.0)
        bbox: list[int] = Field(min_length=4, max_length=4)
    
    data: list[ObjectData]


# ==========================================
# Tin nhắn Audio
# ==========================================

class AudioChunkMessage(BaseMessage):
    """Tin nhắn đoạn audio."""
    type: MessageType = MessageType.AUDIO_CHUNK
    
    class AudioData(BaseModel):
        chunk_id: int
        sample_rate: int
        channels: int
        format: str = "wav"
        data: str  # Audio mã hóa Base64
        duration_ms: float
    
    data: AudioData


class SpeechDetectedMessage(BaseMessage):
    """Tin nhắn phát hiện hoạt động nói."""
    type: MessageType = MessageType.SPEECH_DETECTED
    
    class SpeechData(BaseModel):
        is_speaking: bool
        confidence: float = Field(ge=0.0, le=1.0)
        duration_ms: float
    
    data: SpeechData


class SpeechTranscribedMessage(BaseMessage):
    """Tin nhắn phiên âm giọng nói."""
    type: MessageType = MessageType.SPEECH_TRANSCRIBED
    
    class TranscriptionData(BaseModel):
        text: str
        language: str
        confidence: float = Field(ge=0.0, le=1.0)
        duration_ms: float
        speaker_id: Optional[str] = None
    
    data: TranscriptionData


# ==========================================
# Tin nhắn NLP
# ==========================================

class TextInputMessage(BaseMessage):
    """Tin nhắn nhập liệu văn bản."""
    type: MessageType = MessageType.TEXT_INPUT
    
    class TextData(BaseModel):
        text: str
        source: str = "user"  # user, system, voice
        language: str = "en"
    
    data: TextData


class IntentClassifiedMessage(BaseMessage):
    """Tin nhắn phân loại ý định."""
    type: MessageType = MessageType.INTENT_CLASSIFIED
    
    class IntentData(BaseModel):
        intent: str
        confidence: float = Field(ge=0.0, le=1.0)
        entities: Dict[str, Any] = Field(default_factory=dict)
        sentiment: Optional[str] = None
    
    data: IntentData


class LLMResponseMessage(BaseMessage):
    """Tin nhắn phản hồi từ LLM."""
    type: MessageType = MessageType.LLM_RESPONSE
    
    class LLMData(BaseModel):
        response_text: str
        model: str
        tokens_used: Optional[int] = None
        processing_time_ms: float
        emotion: Optional[Emotion] = None
    
    data: LLMData


# ==========================================
# Tin nhắn Hành vi
# ==========================================

class EmotionChangedMessage(BaseMessage):
    """Tin nhắn thay đổi trạng thái cảm xúc."""
    type: MessageType = MessageType.EMOTION_CHANGED
    
    class EmotionData(BaseModel):
        previous_emotion: Emotion
        current_emotion: Emotion
        intensity: float = Field(ge=0.0, le=1.0)
        trigger: Optional[str] = None
    
    data: EmotionData


class ActionCommandMessage(BaseMessage):
    """Tin nhắn lệnh hành động điều khiển robot."""
    type: MessageType = MessageType.ACTION_COMMAND
    
    class ActionData(BaseModel):
        action: str  # move, speak, gesture, v.v.
        parameters: Dict[str, Any] = Field(default_factory=dict)
        priority: int = Field(ge=0, le=3)
        timeout_ms: Optional[int] = None
    
    data: ActionData


class BehaviorStateMessage(BaseMessage):
    """Tin nhắn trạng thái hành vi."""
    type: MessageType = MessageType.BEHAVIOR_STATE
    
    class BehaviorData(BaseModel):
        previous_state: BehaviorState
        current_state: BehaviorState
        emotion: Emotion
        reason: Optional[str] = None
    
    data: BehaviorData


class ConfigUpdateMessage(BaseMessage):
    """Tin nhắn cập nhật cấu hình."""
    type: MessageType = MessageType.CONFIG_UPDATE
    
    class ConfigData(BaseModel):
        config_key: str
        config_value: Any
        scope: str = "runtime"  # runtime, persistent
    
    data: ConfigData


# ==========================================
# Nhà máy tạo tin nhắn
# ==========================================

MESSAGE_TYPE_MAP = {
    MessageType.HEARTBEAT: HeartbeatMessage,
    MessageType.STATUS: StatusMessage,
    MessageType.ERROR: ErrorMessage,
    MessageType.FRAME: FrameMessage,
    MessageType.FACE_DETECTED: FaceDetectedMessage,
    MessageType.FACE_RECOGNIZED: FaceRecognizedMessage,
    MessageType.MOTION_DETECTED: MotionDetectedMessage,
    MessageType.OBJECT_DETECTED: ObjectDetectedMessage,
    MessageType.AUDIO_CHUNK: AudioChunkMessage,
    MessageType.SPEECH_DETECTED: SpeechDetectedMessage,
    MessageType.SPEECH_TRANSCRIBED: SpeechTranscribedMessage,
    MessageType.TEXT_INPUT: TextInputMessage,
    MessageType.INTENT_CLASSIFIED: IntentClassifiedMessage,
    MessageType.LLM_RESPONSE: LLMResponseMessage,
    MessageType.EMOTION_CHANGED: EmotionChangedMessage,
    MessageType.ACTION_COMMAND: ActionCommandMessage,
    MessageType.BEHAVIOR_STATE: BehaviorStateMessage,
    MessageType.CONFIG_UPDATE: ConfigUpdateMessage,
}


def create_message(message_type: MessageType, data: Dict[str, Any]) -> BaseMessage:
    """
    Hàm nhà máy tạo tin nhắn theo kiểu cụ thể.
    
    Args:
        message_type: Loại tin nhắn cần tạo
        data: Dữ liệu tin nhắn
        
    Returns:
        Thể hiện tin nhắn đã được kiểu hóa
    """
    message_class = MESSAGE_TYPE_MAP.get(message_type, BaseMessage)
    return message_class(type=message_type, data=data)


def parse_message(raw_data: Dict[str, Any]) -> BaseMessage:
    """
    Phân tích dữ liệu thô thành tin nhắn đã kiểu hóa.
    
    Args:
        raw_data: Từ điển tin nhắn thô
        
    Returns:
        Thể hiện tin nhắn đã được kiểu hóa
        
    Raises:
        ValueError: Nếu loại tin nhắn không hợp lệ
    """
    try:
        message_type = MessageType(raw_data.get("type"))
        message_class = MESSAGE_TYPE_MAP.get(message_type, BaseMessage)
        return message_class(**raw_data)
    except Exception as e:
        raise ValueError(f"Không thể phân tích tin nhắn: {e}")
