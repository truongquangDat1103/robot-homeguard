"""
Bộ xử lý và định tuyến tin nhắn WebSocket.
Định tuyến các tin nhắn nhận được tới các bộ xử lý phù hợp.chịu trách nhiệm nhận message từ WebSocket và chuyển đến đúng hàm xử lý tương ứng.
"""
from typing import Optional, Dict, Callable, Any                                                # Khai báo kiểu dữ liệu rõ ràng, giúp code an toàn, dễ đọc và dễ mở rộng.    
from loguru import logger                                                                       # Ghi log

from src.services.websocket.protocols import (
    BaseMessage,
    FrameMessage,
    AudioChunkMessage,
    TextInputMessage,
    ActionCommandMessage,
    ConfigUpdateMessage,
)
from src.utils.constants import MessageType


class MessageHandler:
    """
    Bộ xử lý trung tâm để định tuyến các tin nhắn WebSocket.
    """
    
    def __init__(self):
        """Khởi tạo bộ xử lý tin nhắn."""
        self.processors: Dict[MessageType, Callable] = {}
        self.setup_default_handlers()
        logger.info("Bộ xử lý tin nhắn đã khởi tạo")
    
    def setup_default_handlers(self) -> None:
        """Thiết lập các bộ xử lý tin nhắn mặc định."""
        # Tin nhắn Vision
        self.register_processor(MessageType.FRAME, self.handle_frame)
        
        # Tin nhắn Audio
        self.register_processor(MessageType.AUDIO_CHUNK, self.handle_audio_chunk)
        
        # Tin nhắn NLP
        self.register_processor(MessageType.TEXT_INPUT, self.handle_text_input)
        
        # Tin nhắn điều khiển
        self.register_processor(MessageType.ACTION_COMMAND, self.handle_action_command)
        self.register_processor(MessageType.CONFIG_UPDATE, self.handle_config_update)
        
        logger.info("Các bộ xử lý tin nhắn mặc định đã được đăng ký")
    
    def register_processor(
        self,
        message_type: MessageType,
        processor: Callable[[BaseMessage], None]
    ) -> None:
        """
        Đăng ký bộ xử lý cho một loại tin nhắn.
        
        Args:
            message_type: Loại tin nhắn cần xử lý
            processor: Hàm xử lý
        """
        self.processors[message_type] = processor
        logger.debug(f"Đã đăng ký bộ xử lý cho {message_type}")
    
    async def route_message(self, message: BaseMessage) -> None:
        """
        Định tuyến tin nhắn tới bộ xử lý phù hợp.
        
        Args:
            message: Tin nhắn cần định tuyến
        """
        processor = self.processors.get(message.type)
        
        if processor:
            try:
                if asyncio.iscoroutinefunction(processor):
                    await processor(message)
                else:
                    processor(message)
            except Exception as e:
                logger.error(f"Lỗi xử lý {message.type}: {e}")
        else:
            logger.warning(f"Không có bộ xử lý cho loại tin nhắn: {message.type}")
            await self.handle_unknown(message)
    
    # ==========================================
    # Bộ xử lý tin nhắn
    # ==========================================
    
    async def handle_frame(self, message: FrameMessage) -> None:
        """
        Xử lý khung hình video nhận được.
        
        Args:
            message: Tin nhắn khung hình
        """
        logger.debug(f"Đang xử lý khung hình {message.data.frame_id}")
        
        # TODO: Chuyển tiếp tới dịch vụ camera
        # await camera_service.process_frame(message.data)
    
    async def handle_audio_chunk(self, message: AudioChunkMessage) -> None:
        """
        Xử lý đoạn audio nhận được.
        
        Args:
            message: Tin nhắn đoạn audio
        """
        logger.debug(f"Đang xử lý đoạn audio {message.data.chunk_id}")
        
        # TODO: Chuyển tiếp tới dịch vụ giọng nói
        # await voice_service.process_audio(message.data)
    
    async def handle_text_input(self, message: TextInputMessage) -> None:
        """
        Xử lý nhập liệu văn bản.
        
        Args:
            message: Tin nhắn nhập văn bản
        """
        logger.info(f"Nhận được văn bản: {message.data.text}")
        
        # TODO: Chuyển tiếp tới dịch vụ NLP
        # await llm_service.process_text(message.data.text)
    
    async def handle_action_command(self, message: ActionCommandMessage) -> None:
        """
        Xử lý lệnh hành động.
        
        Args:
            message: Tin nhắn lệnh hành động
        """
        action = message.data.action
        params = message.data.parameters
        
        logger.info(f"Thực hiện hành động: {action} với tham số: {params}")
        
        # TODO: Chuyển tiếp tới engine hành vi
        # await behavior_engine.execute_action(action, params)
    
    async def handle_config_update(self, message: ConfigUpdateMessage) -> None:
        """
        Xử lý cập nhật cấu hình.
        
        Args:
            message: Tin nhắn cập nhật cấu hình
        """
        key = message.data.config_key
        value = message.data.config_value
        
        logger.info(f"Cập nhật cấu hình: {key} = {value}")
        
        # TODO: Cập nhật cấu hình
        # config_manager.update(key, value)
    
    async def handle_unknown(self, message: BaseMessage) -> None:
        """
        Xử lý loại tin nhắn không xác định.
        
        Args:
            message: Tin nhắn không xác định
        """
        logger.warning(f"Nhận được loại tin nhắn không xác định: {message.type}")
        logger.debug(f"Dữ liệu tin nhắn: {message.data}")


# Import asyncio ở cuối để tránh import vòng
import asyncio
