"""
Client WebSocket để giao tiếp hai chiều với robot.
Xử lý kết nối, kết nối lại và định tuyến tin nhắn.
"""
import asyncio                                                                                      # Thư viện lập trình bất đồng bộ
import json                                                                                         # Xử lý JSON                                                    
from typing import Optional, Callable, Dict, Any                                                    # Khai báo kiểu dữ liệu rõ ràng, giúp code an toàn, dễ đọc và dễ mở rộng.                                 
from enum import Enum                                                                               # Định nghĩa Enum                          

import websockets                                                                                   # Thư viện WebSocket                              
from websockets.client import WebSocketClientProtocol                                               # Giao thức client WebSocket                                                    
from loguru import logger                                                                           # Ghi log                                 

from config.settings import WebSocketSettings                                                       # Cấu hình WebSocket                                                                
from src.services.websocket.protocols import BaseMessage, parse_message, HeartbeatMessage           # Giao thức tin nhắn WebSocket                              
from src.utils.constants import MessageType                                                         # Các hằng số dùng chung                                                               


class ConnectionState(Enum):
    """Các trạng thái kết nối WebSocket."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


class WebSocketClient:
    """
    Client WebSocket với tự động kết nối lại và xử lý tin nhắn.
    """
    
    def __init__(self, config: WebSocketSettings):
        """
        Khởi tạo client WebSocket.
        
        Args:
            config: Cấu hình WebSocket
        """
        self.config = config
        self.url = config.url
        
        # Trạng thái kết nối
        self.state = ConnectionState.DISCONNECTED
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.reconnect_attempts = 0
        
        # Bộ xử lý tin nhắn
        self.message_handlers: Dict[MessageType, list[Callable]] = {}
        self.default_handler: Optional[Callable] = None
        
        # Nhiệm vụ chạy nền
        self.receiver_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.running = False
        
        logger.info(f"WebSocket client khởi tạo - URL: {self.url}")
    
    async def connect(self) -> bool:
        """
        Kết nối tới server WebSocket.
        
        Returns:
            True nếu kết nối thành công
        """
        if self.state == ConnectionState.CONNECTED:
            logger.warning("Đã kết nối")
            return True
        
        self.state = ConnectionState.CONNECTING
        logger.info(f"Đang kết nối tới {self.url}...")
        
        try:
            self.websocket = await websockets.connect(
                self.url,
                ping_interval=self.config.ping_interval,
                ping_timeout=self.config.timeout,
                close_timeout=10
            )
            
            self.state = ConnectionState.CONNECTED
            self.reconnect_attempts = 0
            self.running = True
            
            # Bắt đầu các nhiệm vụ chạy nền
            self.receiver_task = asyncio.create_task(self._receive_loop())
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            logger.info("✅ Kết nối WebSocket thành công")
            return True
            
        except Exception as e:
            self.state = ConnectionState.FAILED
            logger.error(f"❌ Kết nối thất bại: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Ngắt kết nối khỏi server WebSocket."""
        logger.info("Đang ngắt kết nối WebSocket...")
        self.running = False
        
        # Hủy các nhiệm vụ chạy nền
        if self.receiver_task:
            self.receiver_task.cancel()
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        # Đóng kết nối
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        self.state = ConnectionState.DISCONNECTED
        logger.info("WebSocket đã ngắt kết nối")
    
    async def reconnect(self) -> bool:
        """
        Thử kết nối lại với server WebSocket.
        
        Returns:
            True nếu kết nối lại thành công
        """
        if self.reconnect_attempts >= self.config.max_retries:
            logger.error(f"Đạt số lần thử kết nối tối đa ({self.config.max_retries})")
            self.state = ConnectionState.FAILED
            return False
        
        self.state = ConnectionState.RECONNECTING
        self.reconnect_attempts += 1
        
        logger.warning(
            f"Đang kết nối lại... (lần {self.reconnect_attempts}/{self.config.max_retries})"
        )
        
        await asyncio.sleep(self.config.reconnect_interval)
        return await self.connect()
    
    async def send_message(self, message: BaseMessage) -> bool:
        """
        Gửi tin nhắn tới server.
        
        Args:
            message: Tin nhắn cần gửi
            
        Returns:
            True nếu gửi thành công
        """
        if not self.is_connected():
            logger.error("Không thể gửi tin nhắn - chưa kết nối")
            return False
        
        try:
            message_json = message.model_dump_json()
            await self.websocket.send(message_json)
            logger.debug(f"Đã gửi tin nhắn: {message.type}")
            return True
            
        except Exception as e:
            logger.error(f"Gửi tin nhắn thất bại: {e}")
            return False
    
    async def send_raw(self, data: Dict[str, Any]) -> bool:
        """
        Gửi dữ liệu JSON thô.
        
        Args:
            data: Từ điển dữ liệu cần gửi
            
        Returns:
            True nếu gửi thành công
        """
        if not self.is_connected():
            logger.error("Không thể gửi dữ liệu - chưa kết nối")
            return False
        
        try:
            await self.websocket.send(json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Gửi dữ liệu thô thất bại: {e}")
            return False
    
    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable[[BaseMessage], None]
    ) -> None:
        """
        Đăng ký bộ xử lý cho một loại tin nhắn cụ thể.
        
        Args:
            message_type: Loại tin nhắn cần xử lý
            handler: Hàm xử lý
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        
        self.message_handlers[message_type].append(handler)
        logger.debug(f"Đã đăng ký handler cho {message_type}")
    
    def register_default_handler(self, handler: Callable[[BaseMessage], None]) -> None:
        """
        Đăng ký bộ xử lý mặc định cho các tin nhắn chưa được xử lý.
        
        Args:
            handler: Hàm xử lý mặc định
        """
        self.default_handler = handler
        logger.debug("Đã đăng ký handler mặc định")
    
    def is_connected(self) -> bool:
        """Kiểm tra trạng thái kết nối WebSocket."""
        return (
            self.state == ConnectionState.CONNECTED and
            self.websocket is not None and
            not self.websocket.closed
        )
    
    async def _receive_loop(self) -> None:
        """Nhiệm vụ nền để nhận tin nhắn."""
        logger.info("Bắt đầu nhận tin nhắn")
        
        try:
            while self.running and self.websocket:
                try:
                    raw_message = await self.websocket.recv()
                    await self._handle_message(raw_message)
                    
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("Kết nối bị server đóng")
                    break
                    
                except Exception as e:
                    logger.error(f"Lỗi khi nhận tin nhắn: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Vòng lặp nhận tin nhắn bị hủy")
        
        # Thử kết nối lại nếu không chủ động ngắt
        if self.running:
            await self.reconnect()
    
    async def _handle_message(self, raw_message: str) -> None:
        """
        Xử lý tin nhắn nhận được.
        
        Args:
            raw_message: Chuỗi tin nhắn thô
        """
        try:
            # Phân tích JSON
            data = json.loads(raw_message)
            
            # Chuyển thành tin nhắn đã kiểu hóa
            message = parse_message(data)
            
            logger.debug(f"Nhận được tin nhắn: {message.type}")
            
            # Gửi tới các handler
            handlers = self.message_handlers.get(message.type, [])
            
            if handlers:
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            handler(message)
                    except Exception as e:
                        logger.error(f"Lỗi handler: {e}")
            
            elif self.default_handler:
                if asyncio.iscoroutinefunction(self.default_handler):
                    await self.default_handler(message)
                else:
                    self.default_handler(message)
            
            else:
                logger.warning(f"Không có handler cho loại tin nhắn: {message.type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON không hợp lệ nhận được: {e}")
        except Exception as e:
            logger.error(f"Lỗi xử lý tin nhắn: {e}")
    
    async def _heartbeat_loop(self) -> None:
        """Nhiệm vụ nền gửi heartbeat định kỳ."""
        logger.info("Bắt đầu heartbeat")
        
        try:
            while self.running:
                if self.is_connected():
                    heartbeat = HeartbeatMessage()
                    await self.send_message(heartbeat)
                
                await asyncio.sleep(self.config.ping_interval)
                
        except asyncio.CancelledError:
            logger.info("Vòng lặp heartbeat bị hủy")
    
    def get_state(self) -> ConnectionState:
        """Lấy trạng thái kết nối hiện tại."""
        return self.state
