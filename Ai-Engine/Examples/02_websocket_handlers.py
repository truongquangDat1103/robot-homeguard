"""
Demo sử dụng WebSocket với custom message handlers.
Xử lý các loại messages khác nhau từ robot.
"""
import asyncio
from loguru import logger

from src.services.websocket import get_websocket_manager
from src.services.websocket.protocols import (
    FaceRecognizedMessage,
    SpeechTranscribedMessage,
    LLMResponseMessage,
    EmotionChangedMessage,
)
from src.utils.constants import MessageType


# ==========================================
# Custom Message Handlers
# ==========================================

async def handle_face_recognized(message: FaceRecognizedMessage):
    """Xử lý khi nhận diện được khuôn mặt."""
    logger.info("👤 Phát hiện khuôn mặt:")
    for face in message.data:
        logger.info(
            f"  - {face.person_name} "
            f"(độ tin cậy: {face.confidence:.2%})"
        )


async def handle_speech_transcribed(message: SpeechTranscribedMessage):
    """Xử lý khi chuyển đổi giọng nói thành text."""
    text = message.data.text
    confidence = message.data.confidence
    language = message.data.language
    
    logger.info(f"🎤 Giọng nói → Text:")
    logger.info(f"  - Nội dung: '{text}'")
    logger.info(f"  - Ngôn ngữ: {language}")
    logger.info(f"  - Độ chính xác: {confidence:.2%}")


async def handle_llm_response(message: LLMResponseMessage):
    """Xử lý response từ LLM."""
    response = message.data.response_text
    model = message.data.model
    tokens = message.data.tokens_used
    time_ms = message.data.processing_time_ms
    
    logger.info(f"🤖 LLM Response:")
    logger.info(f"  - Model: {model}")
    logger.info(f"  - Response: {response}")
    logger.info(f"  - Tokens: {tokens}")
    logger.info(f"  - Thời gian: {time_ms:.0f}ms")


async def handle_emotion_changed(message: EmotionChangedMessage):
    """Xử lý khi cảm xúc robot thay đổi."""
    prev = message.data.previous_emotion
    curr = message.data.current_emotion
    intensity = message.data.intensity
    trigger = message.data.trigger
    
    logger.info(f"😊 Cảm xúc thay đổi:")
    logger.info(f"  - Từ: {prev.value}")
    logger.info(f"  - Sang: {curr.value}")
    logger.info(f"  - Cường độ: {intensity:.2%}")
    if trigger:
        logger.info(f"  - Nguyên nhân: {trigger}")


async def main():
    """Hàm chính demo."""
    logger.info("🚀 WebSocket Handlers Demo")
    
    # Lấy WebSocket manager
    ws_manager = get_websocket_manager()
    
    # Đăng ký các message handlers
    logger.info("📝 Đăng ký message handlers...")
    
    ws_manager.register_message_processor(
        MessageType.FACE_RECOGNIZED,
        handle_face_recognized
    )
    
    ws_manager.register_message_processor(
        MessageType.SPEECH_TRANSCRIBED,
        handle_speech_transcribed
    )
    
    ws_manager.register_message_processor(
        MessageType.LLM_RESPONSE,
        handle_llm_response
    )
    
    ws_manager.register_message_processor(
        MessageType.EMOTION_CHANGED,
        handle_emotion_changed
    )
    
    logger.info("✅ Đã đăng ký 4 handlers")
    
    # Kết nối
    success = await ws_manager.start()
    
    if not success:
        logger.error("❌ Không thể kết nối")
        return
    
    await ws_manager.wait_until_connected(timeout=10.0)
    
    if ws_manager.is_connected():
        logger.info("✅ Đã kết nối - Đang lắng nghe messages...")
        logger.info("(Nhấn Ctrl+C để dừng)")
        
        try:
            # Gửi status mỗi 10 giây
            while True:
                await ws_manager.send_status(
                    cpu_usage=50.0,
                    memory_usage=65.0,
                    active_services=["camera", "voice", "llm"]
                )
                
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Đang dừng...")
    
    # Cleanup
    await ws_manager.stop()
    logger.info("👋 Đã đóng kết nối")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Dừng bởi user")
    except Exception as e:
        logger.error(f"Lỗi: {e}")