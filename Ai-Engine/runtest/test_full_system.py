"""Test full system integration."""
import asyncio
import sys, os
from dataclasses import dataclass
from enum import Enum

# Thêm src vào PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.nlp import LLMManager, ConversationEngine, IntentClassifier
from src.core.behavior import BehaviorEngine, EmotionModel, DecisionMaker
from config.settings import settings


# Định nghĩa fallback cho IntentResult nếu classifier trả về None
class Intent(Enum):
    GREETING = "greeting"
    COMMAND = "command"
    QUESTION = "question"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    intent: Intent
    confidence: float
    entities: dict | None = None


async def test_full_system():
    print("🤖 Testing Full System Integration\n")

    # 1. Setup
    print("1️⃣ Setting up components...")
    llm = LLMManager(settings.llm)
    conversation = ConversationEngine(llm)
    intent_classifier = IntentClassifier()
    behavior = BehaviorEngine()
    emotion = EmotionModel()
    decision = DecisionMaker()

    print("✅ All components initialized\n")

    # 2. Test conversation flow
    test_inputs = [
        "Xin chào robot",
        "Bật đèn phòng khách",
        "Thời tiết hôm nay thế nào?",
        "Tạm biệt",
    ]

    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {user_input}")
        print("="*60)

        # Classify intent
        intent_result = intent_classifier.classify(user_input)

        # Nếu classifier trả về None → fallback
        if intent_result is None:
            intent_result = IntentResult(intent=Intent.UNKNOWN, confidence=0.0)

        print(f"📊 Intent: {intent_result.intent.value} (confidence: {intent_result.confidence:.2f})")

        if intent_result.entities:
            print(f"   Entities: {intent_result.entities}")

        # Update emotion
        if intent_result.intent.value == "greeting":
            emotion.trigger_positive_event(0.3)
        emotion.update()
        current_emotion = emotion.get_current_emotion()
        print(f"😊 Emotion: {current_emotion.value}")

        # Get LLM response
        response = await conversation.send_message(
            conversation_id="test_user",
            user_message=user_input,
        )

        if response:
            print(f"🤖 Response: {response.text}")
            print(f"   Tokens used: {response.tokens_used}")

        await asyncio.sleep(1)

    print(f"\n{'='*60}")
    print("✅ Full system test completed!")
    print(f"{'='*60}\n")

    # 3. Show conversation summary
    conv = conversation.get_conversation("test_user")
    if conv:
        print(conv.get_summary())


if __name__ == "__main__":
    asyncio.run(test_full_system())
