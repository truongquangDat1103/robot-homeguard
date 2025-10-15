"""
Điểm khởi động ứng dụng AI-Engine
Quản lý vòng đời và điều phối chính của hệ thống
"""
import asyncio                                                  # Thư viện chuẩn để làm việc với các tác vụ bất đồng bộ
import signal                                                   # Thư viện chuẩn để xử lý tín hiệu hệ thống
import sys                                                      # Thư viện chuẩn để tương tác với hệ thống                                                   
from typing import Optional                                     # Thư viện chuẩn để hỗ trợ chú thích kiểu dữ liệu                  

from loguru import logger                                       # Thư viện ghi log nâng cao                                           

from config.settings import settings                            # Cấu hình ứng dụng                                         
from src.utils.logger import setup_logger                       # Hàm thiết lập cấu hình ghi log                                    
from src.utils.constants import SystemStatus                    # Các hằng số và enum dùng trong hệ thống                               


class AIEngine:
    """Lớp chính của ứng dụng AI Engine."""
    
    def __init__(self):
        """Khởi tạo AI Engine."""
        self.status = SystemStatus.OFFLINE
        self.running = False
        
        # Các dịch vụ (sẽ được khởi tạo sau)
        self.websocket_client = None
        self.camera_service = None
        self.voice_service = None
        self.llm_service = None
        
        logger.info("AI-Engine đã được khởi tạo")
        logger.info(f"Môi trường: {settings.env}")
        logger.info(f"Chế độ gỡ lỗi: {settings.debug}")
    
    async def initialize(self) -> None:
        """Khởi tạo tất cả các dịch vụ và module."""
        try:
            logger.info("🚀 Bắt đầu khởi tạo AI-Engine...")
            
            # TODO: Khởi tạo các dịch vụ tại đây
            # self.websocket_client = WebSocketClient(settings.websocket)
            # self.camera_service = CameraService(settings.camera)
            # self.voice_service = VoiceService(settings.audio)
            # self.llm_service = LLMService(settings.llm)
            
            logger.info("✅ Tất cả dịch vụ đã khởi tạo thành công")
            self.status = SystemStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"❌ Khởi tạo thất bại: {e}")
            self.status = SystemStatus.UNHEALTHY
            raise
    
    async def start(self) -> None:
        """Bắt đầu chạy AI Engine."""
        try:
            await self.initialize()
            self.running = True
            
            logger.info("🤖 AI-Engine đang chạy...")
            logger.info(f"Tên robot: {settings.behavior.robot_name}")
            logger.info(f"Tính cách: {settings.behavior.personality}")
            
            # TODO: Khởi chạy các dịch vụ
            # await asyncio.gather(
            #     self.websocket_client.connect(),
            #     self.camera_service.start(),
            #     self.voice_service.start(),
            #     self.llm_service.start()
            # )
            
            # Tiếp tục chạy cho đến khi dừng lại
            await self.run()
            
        except KeyboardInterrupt:
            logger.info("Nhận tín hiệu dừng hệ thống")
        except Exception as e:
            logger.error(f"Lỗi trong quá trình khởi động: {e}")
            self.status = SystemStatus.UNHEALTHY
        finally:
            await self.shutdown()
    
    async def run(self) -> None:
        """Vòng lặp sự kiện chính."""
        try:
            while self.running:
                # Vòng lặp xử lý chính
                await asyncio.sleep(0.1)
                
                # TODO: Thêm logic xử lý chính
                # - Xử lý tin nhắn WebSocket đến
                # - Xử lý khung hình từ camera
                # - Xử lý âm thanh ghi lại
                # - Cập nhật trạng thái hành vi của robot
                
        except asyncio.CancelledError:
            logger.info("Vòng lặp chính đã bị hủy")
    
    async def shutdown(self) -> None:
        """Tắt hệ thống và dừng toàn bộ dịch vụ một cách an toàn."""
        logger.info("🛑 Đang tắt AI-Engine...")
        self.running = False
        self.status = SystemStatus.OFFLINE
        
        try:
            # TODO: Dừng toàn bộ dịch vụ
            # if self.camera_service:
            #     await self.camera_service.stop()
            # if self.voice_service:
            #     await self.voice_service.stop()
            # if self.websocket_client:
            #     await self.websocket_client.disconnect()
            
            logger.info("✅ AI-Engine đã tắt hoàn toàn")
            
        except Exception as e:
            logger.error(f"Lỗi trong quá trình tắt hệ thống: {e}")
    
    def handle_signal(self, sig: int) -> None:
        """Xử lý tín hiệu hệ thống (ví dụ: Ctrl+C, SIGTERM)."""
        logger.info(f"Nhận tín hiệu hệ thống: {sig}")
        self.running = False


def setup_signal_handlers(engine: AIEngine) -> None:
    """Thiết lập trình xử lý tín hiệu để dừng hệ thống an toàn."""
    loop = asyncio.get_event_loop()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: engine.handle_signal(s)
        )


async def main() -> None:
    """Điểm khởi đầu chính của ứng dụng."""
    # Thiết lập cấu hình ghi log
    setup_logger(level=settings.log_level)
    
    # Hiển thị banner
    print_banner()
    
    # Tạo và khởi chạy engine
    engine = AIEngine()
    
    # Thiết lập xử lý tín hiệu (chỉ áp dụng cho hệ thống Unix)
    if sys.platform != "win32":
        setup_signal_handlers(engine)
    
    # Khởi động engine
    await engine.start()


def print_banner() -> None:
    """Hiển thị banner thông tin ứng dụng."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                     🤖 AI-ENGINE 🤖                       ║
    ║                                                           ║
    ║         Advanced AI System for Intelligent Robots        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"    Phiên bản: 0.1.0")
    print(f"    Môi trường: {settings.env}")
    print(f"    Python: {sys.version.split()[0]}")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Ứng dụng đã được dừng bởi người dùng")
    except Exception as e:
        logger.error(f"Lỗi ứng dụng: {e}")
        sys.exit(1)
