"""
API Schemas - Pydantic models cho API requests/responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ==========================================
# Health & Status
# ==========================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")


class StatusResponse(BaseModel):
    """System status response."""
    cpu_usage: float = Field(..., description="CPU usage %")
    memory_usage: float = Field(..., description="Memory usage %")
    active_services: List[str] = Field(..., description="Danh sách services đang chạy")
    uptime: float = Field(..., description="Uptime (giây)")


# ==========================================
# NLP
# ==========================================

class TextInputRequest(BaseModel):
    """Text input request."""
    text: str = Field(..., description="Text từ user")
    conversation_id: Optional[str] = Field(None, description="ID conversation")
    user_name: Optional[str] = Field(None, description="Tên user")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Bật đèn phòng khách",
                "conversation_id": "user_123",
                "user_name": "John"
            }
        }


class TextInputResponse(BaseModel):
    """Text input response."""
    response: str = Field(..., description="Response text")
    intent: Optional[str] = Field(None, description="Intent được phát hiện")
    confidence: float = Field(..., description="Độ tin cậy")
    processing_time: float = Field(..., description="Thời gian xử lý (ms)")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "Đã bật đèn phòng khách",
                "intent": "command",
                "confidence": 0.92,
                "processing_time": 150.5
            }
        }


# ==========================================
# Sensors
# ==========================================

class SensorDataRequest(BaseModel):
    """Sensor data request."""
    sensor_id: str = Field(..., description="ID sensor")
    value: float = Field(..., description="Giá trị đo được")
    unit: Optional[str] = Field("", description="Đơn vị")
    timestamp: Optional[float] = Field(None, description="Timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "sensor_id": "temperature_living_room",
                "value": 25.5,
                "unit": "°C"
            }
        }


class SensorDataResponse(BaseModel):
    """Sensor data response."""
    success: bool = Field(..., description="Thành công hay không")
    message: str = Field(..., description="Thông báo")


# ==========================================
# Vision
# ==========================================

class FaceDetectionRequest(BaseModel):
    """Face detection request."""
    image_base64: str = Field(..., description="Ảnh dạng base64")
    detect_landmarks: bool = Field(False, description="Detect landmarks không")


class FaceDetectionResponse(BaseModel):
    """Face detection response."""
    face_count: int = Field(..., description="Số khuôn mặt")
    faces: List[Dict[str, Any]] = Field(..., description="Thông tin các khuôn mặt")
    processing_time: float = Field(..., description="Thời gian xử lý (ms)")


# ==========================================
# Audio
# ==========================================

class SpeechToTextRequest(BaseModel):
    """Speech-to-text request."""
    audio_base64: str = Field(..., description="Audio dạng base64")
    language: Optional[str] = Field("auto", description="Ngôn ngữ")


class SpeechToTextResponse(BaseModel):
    """Speech-to-text response."""
    text: str = Field(..., description="Text đã transcribe")
    language: str = Field(..., description="Ngôn ngữ phát hiện")
    confidence: float = Field(..., description="Độ tin cậy")


class TextToSpeechRequest(BaseModel):
    """Text-to-speech request."""
    text: str = Field(..., description="Text cần chuyển")
    language: str = Field("vi", description="Ngôn ngữ")
    slow: bool = Field(False, description="Tốc độ chậm")


class TextToSpeechResponse(BaseModel):
    """Text-to-speech response."""
    audio_base64: str = Field(..., description="Audio dạng base64")
    duration: float = Field(..., description="Thời lượng (giây)")


# ==========================================
# Behavior
# ==========================================

class BehaviorStateResponse(BaseModel):
    """Behavior state response."""
    current_state: str = Field(..., description="State hiện tại")
    previous_state: Optional[str] = Field(None, description="State trước")
    current_emotion: str = Field(..., description="Emotion hiện tại")
    emotion_intensity: float = Field(..., description="Cường độ emotion")
    is_busy: bool = Field(..., description="Robot có bận không")


class EmotionRequest(BaseModel):
    """Set emotion request."""
    emotion: str = Field(..., description="Emotion name")
    intensity: float = Field(0.5, ge=0.0, le=1.0, description="Cường độ")
    
    class Config:
        schema_extra = {
            "example": {
                "emotion": "happy",
                "intensity": 0.8
            }
        }


# ==========================================
# Analytics
# ==========================================

class AnomalyDetectionRequest(BaseModel):
    """Anomaly detection request."""
    sensor_id: str = Field(..., description="ID sensor")
    method: str = Field("zscore", description="Method (zscore, iqr, moving-average)")


class AnomalyDetectionResponse(BaseModel):
    """Anomaly detection response."""
    anomalies_found: int = Field(..., description="Số anomalies")
    anomalies: List[Dict[str, Any]] = Field(..., description="Chi tiết anomalies")


class PredictionRequest(BaseModel):
    """Prediction request."""
    sensor_id: str = Field(..., description="ID sensor")
    steps_ahead: int = Field(1, description="Số bước dự đoán")
    method: str = Field("ensemble", description="Method")


class PredictionResponse(BaseModel):
    """Prediction response."""
    predicted_value: float = Field(..., description="Giá trị dự đoán")
    confidence_interval: tuple = Field(..., description="Khoảng tin cậy")
    method: str = Field(..., description="Method đã dùng")