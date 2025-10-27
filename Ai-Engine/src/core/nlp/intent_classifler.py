"""
Intent Classifier - Phân loại ý định của người dùng.
Xác định user muốn làm gì (hỏi, yêu cầu, chat, ...).
"""
from typing import Optional, List, Dict
import re
from loguru import logger

from src.utils.constants import Intent


class IntentResult:
    """Kết quả phân loại intent."""
    
    def __init__(
        self,
        intent: Intent,
        confidence: float,
        entities: Optional[Dict] = None
    ):
        """
        Khởi tạo IntentResult.
        
        Args:
            intent: Intent đã phát hiện
            confidence: Độ tin cậy (0.0 - 1.0)
            entities: Các entities trích xuất được
        """
        self.intent = intent
        self.confidence = confidence
        self.entities = entities or {}


class IntentClassifier:
    """
    Phân loại intent sử dụng rule-based và pattern matching.
    Có thể mở rộng với ML models sau.
    """
    
    # Patterns cho từng intent
    GREETING_PATTERNS = [
        r"\b(xin chào|chào|hello|hi|hey|hê lô)\b",
        r"\b(good morning|good afternoon|good evening)\b",
        r"\b(chào (buổi )?(sáng|trưa|chiều|tối))\b"
    ]
    
    QUESTION_PATTERNS = [
        r"^(ai|gì|đâu|sao|khi nào|bao giờ|như thế nào|thế nào)",
        r"\b(what|who|where|when|why|how|which)\b",
        r"[?？]$",
        r"\b(có phải|có phải không|đúng không)\b"
    ]
    
    COMMAND_PATTERNS = [
        r"^(bật|tắt|mở|đóng|tăng|giảm|điều chỉnh)",
        r"\b(turn on|turn off|open|close|increase|decrease)\b",
        r"^(hãy|xin|làm ơn|vui lòng)",
        r"^(set|play|stop|start|pause|resume)"
    ]
    
    FAREWELL_PATTERNS = [
        r"\b(tạm biệt|chào|bye|goodbye|see you|gặp lại)\b",
        r"\b(good night|chúc ngủ ngon)\b",
        r"\b(hẹn gặp lại|tạm biệt nhé)\b"
    ]
    
    def __init__(self, confidence_threshold: float = 0.6):
        """
        Khởi tạo Intent Classifier.
        
        Args:
            confidence_threshold: Ngưỡng confidence tối thiểu
        """
        self.confidence_threshold = confidence_threshold
        
        logger.info("Intent Classifier đã khởi tạo")
    
    def classify(self, text: str) -> IntentResult:
        """
        Phân loại intent của text.
        
        Args:
            text: Input text
            
        Returns:
            IntentResult
        """
        if not text or not text.strip():
            return IntentResult(Intent.UNKNOWN, 0.0)
        
        text