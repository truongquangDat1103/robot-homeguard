"""
Configuration management using Pydantic Settings.
Type-safe configuration with environment variable loading.
"""
from typing import List, Literal                                                        # Thư viện chuẩn để hỗ trợ chú thích kiểu dữ liệu
from pydantic import Field, field_validator                                             # Thư viện để định nghĩa và xác thực mô hình dữ liệu                                    
from pydantic_settings import BaseSettings, SettingsConfigDict                          # Thư viện để quản lý cấu hình ứng dụng                   


class WebSocketSettings(BaseSettings):
    """WebSocket connection configuration."""
    url: str = Field(default="ws://192.168.1.100:8080/ws")
    reconnect_interval: int = Field(default=5, ge=1, le=60)
    max_retries: int = Field(default=10, ge=1)
    ping_interval: int = Field(default=30, ge=10)
    timeout: int = Field(default=60, ge=10)

    model_config = SettingsConfigDict(env_prefix="WEBSOCKET_")


class CameraSettings(BaseSettings):
    """Camera and video processing configuration."""
    index: int = Field(default=0, ge=0)
    width: int = Field(default=640, ge=320)
    height: int = Field(default=480, ge=240)
    fps: int = Field(default=30, ge=1, le=60)
    buffer_size: int = Field(default=10, ge=1)
    processing_fps: int = Field(default=15, ge=1)
    
    # Feature flags
    enable_face_detection: bool = True
    enable_motion_detection: bool = True
    enable_object_detection: bool = False
    enable_pose_estimation: bool = False
    
    # Face recognition
    face_detection_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    face_recognition_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    face_db_path: str = "src/models/face_recognition/embeddings.pkl"

    model_config = SettingsConfigDict(env_prefix="CAMERA_")


class AudioSettings(BaseSettings):
    """Audio processing configuration."""
    sample_rate: int = Field(default=16000, ge=8000)
    channels: int = Field(default=1, ge=1, le=2)
    chunk_size: int = Field(default=1024, ge=256)
    buffer_duration: int = Field(default=5, ge=1)
    
    # STT (Speech-to-Text)
    stt_model: Literal["tiny", "base", "small", "medium", "large"] = "base"
    stt_language: str = "en"
    enable_vad: bool = True
    
    # TTS (Text-to-Speech)
    tts_engine: Literal["gtts", "coqui"] = "gtts"
    tts_language: str = "en"
    tts_voice: str = "en-US"

    model_config = SettingsConfigDict(env_prefix="AUDIO_")


class LLMSettings(BaseSettings):
    """Large Language Model configuration."""
    provider: Literal["openai", "anthropic", "ollama"] = "openai"
    model: str = "gpt-4-turbo-preview"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=50)
    timeout: int = Field(default=30, ge=5)
    
    # API Keys
    openai_api_key: str = Field(default="")
    openai_org_id: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    
    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    model_config = SettingsConfigDict(env_prefix="LLM_")

    @field_validator("openai_api_key", "anthropic_api_key")
    def validate_api_key(cls, v: str, info) -> str:
        """Warn if API key is not set."""
        if not v and info.field_name == "openai_api_key":
            print("⚠️  Warning: OpenAI API key not set")
        return v


class BehaviorSettings(BaseSettings):
    """Robot behavior and personality configuration."""
    robot_name: str = "Atlas"
    personality: Literal["friendly", "professional", "playful"] = "friendly"
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    enable_emotions: bool = True
    emotion_response_delay: float = Field(default=0.5, ge=0.0)

    model_config = SettingsConfigDict(env_prefix="ROBOT_")


class PerformanceSettings(BaseSettings):
    """Performance and resource management."""
    max_workers: int = Field(default=4, ge=1)
    enable_gpu: bool = True
    gpu_device: int = Field(default=0, ge=0)
    model_precision: Literal["fp32", "fp16"] = "fp16"
    max_memory_mb: int = Field(default=2048, ge=512)
    enable_memory_profiling: bool = False

    model_config = SettingsConfigDict(env_prefix="")


class StorageSettings(BaseSettings):
    """Storage and database configuration."""
    redis_host: str = "localhost"
    redis_port: int = Field(default=6379, ge=1, le=65535)
    redis_db: int = Field(default=0, ge=0)
    redis_password: str = ""
    database_url: str = "sqlite:///./ai_engine.db"

    model_config = SettingsConfigDict(env_prefix="")


class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration."""
    enable_metrics: bool = True
    metrics_port: int = Field(default=9090, ge=1024, le=65535)
    log_file: str = "logs/ai_engine.log"
    log_rotation: str = "10 MB"
    log_retention: str = "7 days"
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(env_prefix="")


class APISettings(BaseSettings):
    """API server configuration (optional)."""
    enabled: bool = False
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1024, le=65535)
    workers: int = Field(default=2, ge=1)

    model_config = SettingsConfigDict(env_prefix="API_")


class SecuritySettings(BaseSettings):
    """Security configuration."""
    secret_key: str = Field(default="change-this-to-a-random-secret-key")
    api_key: str = Field(default="")
    enable_cors: bool = True
    allowed_origins: List[str] = Field(default=["http://localhost:3000"])

    model_config = SettingsConfigDict(env_prefix="")


class FeatureFlags(BaseSettings):
    """Feature toggle flags."""
    enable_face_recognition: bool = True
    enable_voice_recognition: bool = True
    enable_conversation: bool = True
    enable_behavior_engine: bool = True
    enable_analytics: bool = False

    model_config = SettingsConfigDict(env_prefix="ENABLE_")


class Settings(BaseSettings):
    """Main application settings."""
    env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    # Sub-configurations
    websocket: WebSocketSettings = Field(default_factory=WebSocketSettings)
    camera: CameraSettings = Field(default_factory=CameraSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    behavior: BehaviorSettings = Field(default_factory=BehaviorSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env == "production"

    def is_development(self) -> bool:
        """Check if running in development."""
        return self.env == "development"


# Global settings instance
settings = Settings()


# Helper function to reload settings
def reload_settings() -> Settings:
    """Reload settings from environment."""
    global settings
    settings = Settings()
    return settings