"""
Các hằng số và kiểu liệt kê toàn cục cho AI-Engine.
"""
from enum import Enum, IntEnum


# ==========================================
# Loại tin nhắn
# ==========================================
class MessageType(str, Enum):
    """Các loại tin nhắn WebSocket."""
    # Thị giác máy tính (Vision)
    FRAME = "frame"
    FACE_DETECTED = "face_detected"
    FACE_RECOGNIZED = "face_recognized"
    MOTION_DETECTED = "motion_detected"
    OBJECT_DETECTED = "object_detected"
    
    # Âm thanh (Audio)
    AUDIO_CHUNK = "audio_chunk"
    SPEECH_DETECTED = "speech_detected"
    SPEECH_TRANSCRIBED = "speech_transcribed"
    
    # Xử lý ngôn ngữ tự nhiên (NLP)
    TEXT_INPUT = "text_input"
    INTENT_CLASSIFIED = "intent_classified"
    LLM_RESPONSE = "llm_response"
    
    # Hành vi (Behavior)
    EMOTION_CHANGED = "emotion_changed"
    ACTION_COMMAND = "action_command"
    BEHAVIOR_STATE = "behavior_state"
    
    # Hệ thống (System)
    HEARTBEAT = "heartbeat"
    STATUS = "status"
    ERROR = "error"
    CONFIG_UPDATE = "config_update"


# ==========================================
# Trạng thái hành vi
# ==========================================
class BehaviorState(str, Enum):
    """Các trạng thái hành vi của robot."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    THINKING = "thinking"
    MOVING = "moving"
    INTERACTING = "interacting"
    ALERT = "alert"
    ERROR = "error"


class Emotion(str, Enum):
    """Các cảm xúc của robot."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CURIOUS = "curious"
    CONFUSED = "confused"
    SURPRISED = "surprised"
    ANGRY = "angry"
    AFRAID = "afraid"


# ==========================================
# Mức độ ưu tiên của tác vụ
# ==========================================
class Priority(IntEnum):
    """Các mức độ ưu tiên của nhiệm vụ."""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


# ==========================================
# Camera & Thị giác
# ==========================================
class DetectionType(str, Enum):
    """Các loại phát hiện hình ảnh."""
    FACE = "face"
    PERSON = "person"
    OBJECT = "object"
    MOTION = "motion"
    POSE = "pose"


# Nhận diện khuôn mặt
FACE_DETECTION_MIN_SIZE = 20  # Kích thước khuôn mặt tối thiểu (pixel)
FACE_RECOGNITION_DISTANCE_THRESHOLD = 0.6  # Ngưỡng khoảng cách nhận diện
FACE_EMBEDDING_SIZE = 512  # Kích thước vector đặc trưng khuôn mặt

# Phát hiện vật thể
YOLO_CONFIDENCE_THRESHOLD = 0.5  # Ngưỡng độ tin cậy YOLO
YOLO_NMS_THRESHOLD = 0.4  # Ngưỡng Non-Maximum Suppression

# Phát hiện chuyển động
MOTION_THRESHOLD = 25  # Ngưỡng khác biệt khung hình
MOTION_MIN_AREA = 500  # Diện tích tối thiểu cho vùng chuyển động


# ==========================================
# Xử lý âm thanh
# ==========================================
class AudioEvent(str, Enum):
    """Các loại sự kiện âm thanh."""
    SPEECH_START = "speech_start"
    SPEECH_END = "speech_end"
    NOISE = "noise"
    SILENCE = "silence"
    MUSIC = "music"
    ALARM = "alarm"


# Các hằng số âm thanh
VAD_THRESHOLD = 0.5  # Ngưỡng phát hiện giọng nói (Voice Activity Detection)
SILENCE_DURATION_MS = 1000  # Thời lượng im lặng để dừng ghi âm (ms)
MAX_RECORDING_DURATION = 30  # Thời lượng ghi âm tối đa (giây)


# ==========================================
# Xử lý ngôn ngữ tự nhiên & hội thoại
# ==========================================
class Intent(str, Enum):
    """Các loại ý định của người dùng."""
    GREETING = "greeting"
    QUESTION = "question"
    COMMAND = "command"
    CONVERSATION = "conversation"
    FAREWELL = "farewell"
    UNKNOWN = "unknown"


class Sentiment(str, Enum):
    """Kết quả phân tích cảm xúc."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# Các hằng số hội thoại
MAX_CONVERSATION_HISTORY = 10  # Số lượng lịch sử hội thoại tối đa
CONVERSATION_TIMEOUT_SECONDS = 300  # 5 phút (thời gian chờ hội thoại)


# ==========================================
# Trạng thái hệ thống & hiệu năng
# ==========================================
class SystemStatus(str, Enum):
    """Trạng thái sức khỏe hệ thống."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


# Ngưỡng hiệu năng
MAX_FRAME_PROCESSING_TIME_MS = 100  # Thời gian xử lý khung hình tối đa (ms)
MAX_AUDIO_PROCESSING_TIME_MS = 50   # Thời gian xử lý âm thanh tối đa (ms)
MAX_LLM_RESPONSE_TIME_S = 10        # Thời gian phản hồi LLM tối đa (giây)

# Ngưỡng bộ nhớ
MAX_MEMORY_USAGE_PERCENT = 80        # Giới hạn RAM tối đa (%)
MAX_GPU_MEMORY_USAGE_PERCENT = 90    # Giới hạn bộ nhớ GPU tối đa (%)


# ==========================================
# Đường dẫn mô hình (tương đối so với gốc dự án)
# ==========================================
MODELS_DIR = "src/models"
FACE_EMBEDDINGS_PATH = f"{MODELS_DIR}/face_recognition/embeddings.pkl"
FACE_METADATA_PATH = f"{MODELS_DIR}/face_recognition/metadata.json"
VOICE_MODELS_PATH = f"{MODELS_DIR}/voice/speaker_models.pkl"
BEHAVIOR_MODELS_PATH = f"{MODELS_DIR}/behavior/state_models.pkl"


# ==========================================
# Thông báo lỗi
# ==========================================
ERROR_MESSAGES = {
    "camera_not_found": "Không tìm thấy hoặc không truy cập được camera",
    "websocket_connection_failed": "Kết nối tới máy chủ WebSocket thất bại",
    "model_loading_failed": "Tải mô hình AI thất bại",
    "audio_device_error": "Không tìm thấy hoặc không truy cập được thiết bị âm thanh",
    "llm_api_error": "Yêu cầu tới API LLM thất bại",
    "face_recognition_failed": "Nhận diện khuôn mặt thất bại",
    "invalid_message_format": "Định dạng tin nhắn không hợp lệ",
}


# ==========================================
# Mã màu (dùng cho OpenCV)
# ==========================================
class Colors:
    """Mã màu BGR cho OpenCV."""
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 255)
    CYAN = (255, 255, 0)
    MAGENTA = (255, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)


# ==========================================
# Feature Flags (Runtime toggles)
# ==========================================
ENABLE_DEBUG_VISUALIZATION = True  # Show debug windows
ENABLE_PERFORMANCE_METRICS = True  # Track performance metrics
ENABLE_REMOTE_LOGGING = False  # Send logs to remote server
