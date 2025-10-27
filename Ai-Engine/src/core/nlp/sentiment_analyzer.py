"""
Sentiment Analyzer - Phân tích cảm xúc trong text.
Xác định text mang cảm xúc tích cực, tiêu cực hay trung tính.
"""
import re
from typing import Optional, List, Dict
from loguru import logger

from src.utils.constants import Sentiment


class SentimentResult:
    """Kết quả phân tích cảm xúc."""
    
    def __init__(
        self,
        sentiment: Sentiment,
        confidence: float,
        scores: Dict[str, float]
    ):
        """
        Khởi tạo SentimentResult.
        
        Args:
            sentiment: Sentiment đã phát hiện
            confidence: Độ tin cậy
            scores: Scores cho từng sentiment
        """
        self.sentiment = sentiment
        self.confidence = confidence
        self.scores = scores


class SentimentAnalyzer:
    """
    Phân tích cảm xúc sử dụng lexicon-based approach.
    """
    
    # Từ điển positive words
    POSITIVE_WORDS = {
        # Tiếng Việt
        'tốt', 'hay', 'đẹp', 'tuyệt', 'xuất sắc', 'tuyệt vời', 'yêu',
        'thích', 'vui', 'hạnh phúc', 'tốt lắm', 'ok', 'oke', 'được',
        'cảm ơn', 'thanks', 'cám ơn', 'tốt quá', 'tốt lắm',
        # English
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'love',
        'like', 'happy', 'nice', 'perfect', 'awesome', 'fantastic'
    }
    
    # Từ điển negative words
    NEGATIVE_WORDS = {
        # Tiếng Việt
        'xấu', 'tệ', 'dở', 'kém', 'tồi', 'thất vọng', 'buồn',
        'khó chịu', 'ghét', 'không thích', 'tệ quá', 'không',
        'chán', 'nhàm chán', 'tệ hại', 'kinh khủng',
        # English
        'bad', 'terrible', 'horrible', 'awful', 'poor', 'sad',
        'disappointed', 'hate', 'dislike', 'ugly', 'worst'
    }
    
    # Intensifiers (tăng cường độ)
    INTENSIFIERS = {
        'rất', 'cực kỳ', 'vô cùng', 'quá', 'thực sự',
        'very', 'extremely', 'really', 'so', 'too'
    }
    
    # Negators (đảo ngược sentiment)
    NEGATORS = {
        'không', 'chẳng', 'chả', 'không phải',
        'not', 'no', 'never'
    }
    
    def __init__(self):
        """Khởi tạo Sentiment Analyzer."""
        logger.info("Sentiment Analyzer đã khởi tạo")
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Phân tích cảm xúc của text.
        
        Args:
            text: Input text
            
        Returns:
            SentimentResult
        """
        if not text or not text.strip():
            return SentimentResult(
                sentiment=Sentiment.NEUTRAL,
                confidence=0.0,
                scores={}
            )
        
        text_lower = text.lower()
        
        # Tính scores
        positive_score = self._calculate_positive_score(text_lower)
        negative_score = self._calculate_negative_score(text_lower)
        
        # Xác định sentiment
        if positive_score > negative_score and positive_score > 0:
            sentiment = Sentiment.POSITIVE
            confidence = min(positive_score / (positive_score + negative_score + 1), 1.0)
        elif negative_score > positive_score and negative_score > 0:
            sentiment = Sentiment.NEGATIVE
            confidence = min(negative_score / (positive_score + negative_score + 1), 1.0)
        else:
            sentiment = Sentiment.NEUTRAL
            confidence = 0.5
        
        scores = {
            'positive': positive_score,
            'negative': negative_score,
            'neutral': 1.0 - (positive_score + negative_score)
        }
        
        logger.debug(f"Sentiment: {sentiment.value} (confidence: {confidence:.2f})")
        
        return SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            scores=scores
        )
    
    def _calculate_positive_score(self, text: str) -> float:
        """Tính positive score."""
        score = 0.0
        words = text.split()
        
        for i, word in enumerate(words):
            if word in self.POSITIVE_WORDS:
                weight = 1.0
                
                # Kiểm tra intensifier trước đó
                if i > 0 and words[i-1] in self.INTENSIFIERS:
                    weight = 1.5
                
                # Kiểm tra negator trước đó
                if i > 0 and words[i-1] in self.NEGATORS:
                    weight = -weight  # Đảo ngược
                
                score += weight
        
        return max(score, 0.0)
    
    def detect_emotion(self, text: str) -> Optional[str]:
        """
        Phát hiện emotion cụ thể trong text.
        
        Args:
            text: Input text
            
        Returns:
            Emotion name hoặc None
        """
        text_lower = text.lower()
        
        # Emotion keywords
        emotions = {
            'happy': ['vui', 'happy', 'hạnh phúc', 'vui vẻ', 'vui mừng'],
            'sad': ['buồn', 'sad', 'buồn bã', 'u sầu', 'đau khổ'],
            'angry': ['giận', 'angry', 'tức', 'bực', 'tức giận'],
            'excited': ['hào hứng', 'excited', 'phấn khích', 'háo hức'],
            'surprised': ['ngạc nhiên', 'surprised', 'bất ngờ', 'kinh ngạc'],
            'afraid': ['sợ', 'afraid', 'sợ hãi', 'lo lắng', 'lo sợ']
        }
        
        for emotion, keywords in emotions.items():
            if any(kw in text_lower for kw in keywords):
                return emotion
        
        return None
    
    def add_positive_word(self, word: str) -> None:
        """
        Thêm positive word vào dictionary.
        
        Args:
            word: Word cần thêm
        """
        self.POSITIVE_WORDS.add(word.lower())
        logger.debug(f"Đã thêm positive word: {word}")
    
    def add_negative_word(self, word: str) -> None:
        """
        Thêm negative word vào dictionary.
        
        Args:
            word: Word cần thêm
        """
        self.NEGATIVE_WORDS.add(word.lower())
        logger.debug(f"Đã thêm negative word: {word}")
    
    def get_sentiment_words(self, text: str) -> Dict[str, List[str]]:
        """
        Lấy danh sách sentiment words có trong text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary {'positive': [...], 'negative': [...]}
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_found = [w for w in words if w in self.POSITIVE_WORDS]
        negative_found = [w for w in words if w in self.NEGATIVE_WORDS]
        
        return {
            'positive': positive_found,
            'negative': negative_found
        }
    
    def get_info(self) -> dict:
        """
        Lấy thông tin analyzer.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "positive_words_count": len(self.POSITIVE_WORDS),
            "negative_words_count": len(self.NEGATIVE_WORDS),
            "intensifiers_count": len(self.INTENSIFIERS),
            "negators_count": len(self.NEGATORS),
            "supported_sentiments": [s.value for s in Sentiment]
        }
    def _calculate_negative_score(self, text: str) -> float:
        """Tính negative score."""
        score = 0.0
        words = text.split()
        
        for i, word in enumerate(words):
            if word in self.NEGATIVE_WORDS:
                weight = 1.0
                
                # Kiểm tra intensifier
                if i > 0 and words[i-1] in self.INTENSIFIERS:
                    weight = 1.5
                
                # Kiểm tra negator (đảo ngược thành positive)
                if i > 0 and words[i-1] in self.NEGATORS:
                    weight = -weight
                
                score += weight
        
        return max(score, 0.0)
    