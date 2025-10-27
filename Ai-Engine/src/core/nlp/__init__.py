"""
NLP Module - Natural Language Processing components.
Các module xử lý ngôn ngữ tự nhiên.
"""

from src.core.nlp.llm_manager import LLMManager, LLMProvider, LLMResponse
from src.core.nlp.conversation_engine import (
    ConversationEngine,
    Conversation,
    Message
)
from src.core.nlp.intent_classifier import IntentClassifier, IntentResult
from src.core.nlp.entity_extractor import EntityExtractor, Entity
from src.core.nlp.sentiment_analyzer import SentimentAnalyzer, SentimentResult


__all__ = [
    # LLM
    "LLMManager",
    "LLMProvider",
    "LLMResponse",
    
    # Conversation
    "ConversationEngine",
    "Conversation",
    "Message",
    
    # Intent Classification
    "IntentClassifier",
    "IntentResult",
    
    # Entity Extraction
    "EntityExtractor",
    "Entity",
    
    # Sentiment Analysis
    "SentimentAnalyzer",
    "SentimentResult",
]