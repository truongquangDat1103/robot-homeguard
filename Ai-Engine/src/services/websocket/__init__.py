"""
Quản lý dịch vụ WebSocket.
Quản lý vòng đời client WebSocket và định tuyến tin nhắn.
"""
from typing import Optional                                                                       # Để khai báo kiểu dữ liệu rõ ràng, giúp code an toàn, dễ đọc và dễ mở rộng.                                                    
from loguru import  logger                                                                        # Ghi log                             

from config.settings import settings
from src.services.websocket.client import WebSocketClient, ConnectionState
from src.services.websocket.message_handler import MessageHandler
from src.services.websocket.protocols import (
    BaseMessage,
    HeartbeatMessage,
    StatusMessage,
    ErrorMessage,
    create_message,
)
from src.utils.constants import MessageType


class WebSocketManager:
    """
    Quản lý dịch vụ WebSocket cấp cao.
    Kết hợp client và bộ xử lý tin nhắn.
    """
    
    def __init__(self):
        """Khởi tạo WebSocket manager."""
        self.client = WebSocketClient(settings.websocket)
        self.message_handler = MessageHandler()
        self._initialized = False
        
        logger.info("WebSocket manager đã được tạo")
    
    async def start(self) -> bool:
        """
        Khởi động dịch vụ WebSocket.
        
        Returns:
            True nếu khởi động thành công
        """
        if self._initialized:
            logger.warning("WebSocket manager đã được khởi động")
            return True
        
        logger.info("Đang khởi động WebSocket manager...")
        
        # Đăng ký bộ định tuyến tin nhắn
        self.client.register_default_handler(self.message_handler.route_message)
        
        # Kết nối tới server
        success = await self.client.connect()
        
        if success:
            self._initialized = True
            logger.info("✅ WebSocket manager đã khởi động")
        else:
            logger.error("❌ Khởi động WebSocket manager thất bại")
        
        return success
    
    async def stop(self) -> None:
        """Dừng dịch vụ WebSocket."""
        logger.info("Đang dừng WebSocket manager...")
        
        await self.client.disconnect()
        self._initialized = False
        
        logger.info("WebSocket manager đã dừng")
    
    async def send_message(self, message: BaseMessage) -> bool:
        """
        Gửi tin nhắn tới server.
        
        Args:
            message: Tin nhắn cần gửi
            
        Returns:
            True nếu gửi thành công
        """
        return await self.client.send_message(message)
    
    async def send_heartbeat(self) -> bool:
        """Gửi tin nhắn heartbeat."""
        heartbeat = HeartbeatMessage()
        return await self.send_message(heartbeat)
    
    async def send_status(
        self,
        cpu_usage: float,
        memory_usage: float,
        gpu_usage: Optional[float] = None,
        fps: Optional[float] = None,
        active_services: list[str] = None
    ) -> bool:
        """
        Gửi tin nhắn trạng thái hệ thống.
        
        Args:
            cpu_usage: Phần trăm sử dụng CPU
            memory_usage: Phần trăm sử dụng bộ nhớ
            gpu_usage: Phần trăm sử dụng GPU (tùy chọn)
            fps: FPS hiện tại (tùy chọn)
            active_services: Danh sách tên dịch vụ đang hoạt động
            
        Returns:
            True nếu gửi thành công
        """
        if active_services is None:
            active_services = []
        
        status_data = StatusMessage.StatusData(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            gpu_usage=gpu_usage,
            fps=fps,
            active_services=active_services
        )
        
        status_msg = StatusMessage(data=status_data)
        return await self.send_message(status_msg)
    
    async def send_error(
        self,
        error_code: str,
        error_message: str,
        details: Optional[str] = None
    ) -> bool:
        """
        Gửi tin nhắn lỗi.
        
        Args:
            error_code: Mã lỗi
            error_message: Thông điệp lỗi
            details: Thông tin bổ sung
            
        Returns:
            True nếu gửi thành công
        """
        error_data = ErrorMessage.ErrorData(
            error_code=error_code,
            error_message=error_message,
            details=details
        )
        
        error_msg = ErrorMessage(data=error_data)
        return await self.send_message(error_msg)
    
    def register_message_processor(
        self,
        message_type: MessageType,
        processor
    ) -> None:
        """
        Đăng ký bộ xử lý tin nhắn tùy chỉnh.
        
        Args:
            message_type: Loại tin nhắn cần xử lý
            processor: Hàm xử lý (có thể là async)
        """
        self.message_handler.register_processor(message_type, processor)
    
    def is_connected(self) -> bool:
        """Kiểm tra xem WebSocket có kết nối không."""
        return self.client.is_connected()
    
    def get_connection_state(self) -> ConnectionState:
        """Lấy trạng thái kết nối hiện tại."""
        return self.client.get_state()
    
    async def wait_until_connected(self, timeout: float = 30.0) -> bool:
        """
        Chờ cho đến khi WebSocket kết nối.
        
        Args:
            timeout: Thời gian tối đa chờ tính bằng giây
            
        Returns:
            True nếu kết nối thành công trong thời gian timeout
        """
        import asyncio
        
        start_time = asyncio.get_event_loop().time()
        
        while not self.is_connected():
            if asyncio.get_event_loop().time() - start_time > timeout:
                logger.error(f"Timeout kết nối sau {timeout}s")
                return False
            
            await asyncio.sleep(0.1)
        
        return True


# Instance singleton
_websocket_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """
    Lấy hoặc tạo instance WebSocket manager singleton.
    
    Returns:
        Instance WebSocket manager
    """
    global _websocket_manager
    
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    
    return _websocket_manager


# Xuất tiện lợi
__all__ = [
    "WebSocketManager",
    "WebSocketClient",
    "MessageHandler",
    "get_websocket_manager",
    "ConnectionState",
]
