"""
Demo cơ bản sử dụng WebSocket.
Kết nối và gửi/nhận messages đơn giản.
"""
import asyncio
from loguru import logger

from src.services.websocket import get_websocket_manager
from src.services.websocket.protocols import TextInputMessage


async def main():
    """Hàm chính demo."""
    logger.info("🚀 Bắt đầu WebSocket Demo")
    
    # Lấy WebSocket manager (singleton)
    ws_manager = get_websocket_manager()
    
    # Khởi động WebSocket service
    logger.info("Đang kết nối đến WebSocket server...")
    success = await ws_manager.start()
    
    if not success:
        logger.error("❌ Không thể kết nối đến server")
        return
    
    # Đợi cho đến khi kết nối thành công
    connected = await ws_manager.wait_until_connected(timeout=10.0)
    
    if connected:
        logger.info("✅ Đã kết nối thành công!")
        
        # Gửi heartbeat
        await ws_manager.send_heartbeat()
        logger.info("💓 Đã gửi heartbeat")
        
        # Gửi status
        await ws_manager.send_status(
            cpu_usage=45.5,
            memory_usage=60.2,
            fps=30.0,
            active_services=["camera", "voice", "llm"]
        )
        logger.info("📊 Đã gửi status update")
        
        # Gửi text message
        text_msg = TextInputMessage(
            data=TextInputMessage.TextData(
                text="Xin chào robot!",
                source="user",
                language="vi"
            )
        )
        await ws_manager.send_message(text_msg)
        logger.info("💬 Đã gửi tin nhắn text")
        
        # Giữ kết nối trong 5 giây
        logger.info("Đang lắng nghe messages trong 5 giây...")
        await asyncio.sleep(5)
        
    else:
        logger.error("❌ Timeout khi kết nối")
    
    # Đóng kết nối
    await ws_manager.stop()
    logger.info("👋 Đã đóng kết nối")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Dừng bởi user")
    except Exception as e:
        logger.error(f"Lỗi: {e}")