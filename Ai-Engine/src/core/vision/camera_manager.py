"""
Camera Manager - Quản lý camera và video streaming.
Hỗ trợ camera local (USB/webcam) và streaming từ WebSocket.
"""
import asyncio                                                                                  # Sử dụng asyncio để quản lý các tác vụ bất đồng bộ
import time                                                                                     # Thư viện time để đo thời gian và tính FPS                                         
from typing import Optional, Callable                                                           # Kiểu dữ liệu tùy chọn và callable                        
from enum import Enum                                                                           # Enum để định nghĩa các trạng thái và loại camera                 
import cv2                                                                                      # OpenCV để xử lý video và camera              
import numpy as np                                                                              # NumPy để xử lý mảng hình ảnh                         
from loguru import  logger                                                                      # Loguru để logging           

from config.settings import CameraSettings


class CameraSource(Enum):
    """Nguồn camera."""
    LOCAL = "local"  # Camera USB/webcam
    WEBSOCKET = "websocket"  # Stream từ WebSocket
    RTSP = "rtsp"  # RTSP stream
    FILE = "file"  # Video file


class CameraState(Enum):
    """Trạng thái camera."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    CLOSED = "closed"


class CameraManager:
    """
    Quản lý camera và video streaming.
    Hỗ trợ nhiều nguồn camera khác nhau.
    """
    
    def __init__(self, config: CameraSettings):
        """
        Khởi tạo camera manager.
        
        Args:
            config: Cấu hình camera
        """
        self.config = config
        self.state = CameraState.IDLE
        
        # Camera capture object
        self.cap: Optional[cv2.VideoCapture] = None
        self.source = CameraSource.LOCAL
        
        # Frame info
        self.current_frame: Optional[np.ndarray] = None
        self.frame_count = 0
        self.fps = 0.0
        self.last_frame_time = 0.0
        
        # Callbacks
        self.frame_callbacks: list[Callable] = []
        
        # Async control
        self.running = False
        self.capture_task: Optional[asyncio.Task] = None
        
        logger.info("Camera manager đã khởi tạo")
    
    def initialize(self) -> bool:
        """
        Khởi tạo camera.
        
        Returns:
            True nếu khởi tạo thành công
        """
        if self.state == CameraState.RUNNING:
            logger.warning("Camera đã đang chạy")
            return True
        
        self.state = CameraState.INITIALIZING
        logger.info(f"Đang khởi tạo camera (index: {self.config.index})...")
        
        try:
            # Mở camera
            self.cap = cv2.VideoCapture(self.config.index)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Không thể mở camera index {self.config.index}")
            
            # Cấu hình camera
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            # Kiểm tra resolution thực tế
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"✅ Camera đã khởi tạo:")
            logger.info(f"   Resolution: {actual_width}x{actual_height}")
            logger.info(f"   FPS: {actual_fps}")
            
            self.state = CameraState.IDLE
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo camera: {e}")
            self.state = CameraState.ERROR
            return False
    
    async def start(self) -> bool:
        """
        Bắt đầu capture frames từ camera.
        
        Returns:
            True nếu bắt đầu thành công
        """
        if self.state == CameraState.RUNNING:
            logger.warning("Camera đã đang chạy")
            return True
        
        if self.cap is None or not self.cap.isOpened():
            if not self.initialize():
                return False
        
        logger.info("Đang khởi động camera streaming...")
        
        self.running = True
        self.state = CameraState.RUNNING
        self.frame_count = 0
        self.last_frame_time = time.time()
        
        # Bắt đầu capture task
        self.capture_task = asyncio.create_task(self._capture_loop())
        
        logger.info("✅ Camera streaming đã bắt đầu")
        return True
    
    async def stop(self) -> None:
        """Dừng camera streaming."""
        logger.info("Đang dừng camera...")
        
        self.running = False
        
        # Hủy capture task
        if self.capture_task:
            self.capture_task.cancel()
            try:
                await self.capture_task
            except asyncio.CancelledError:
                pass
        
        self.state = CameraState.IDLE
        logger.info("Camera đã dừng")
    
    def release(self) -> None:
        """Giải phóng camera resource."""
        logger.info("Đang giải phóng camera...")
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.state = CameraState.CLOSED
        logger.info("Camera đã được giải phóng")
    
    async def _capture_loop(self) -> None:
        """
        Vòng lặp chính để capture frames.
        Chạy trong background task.
        """
        logger.info("Capture loop đã bắt đầu")
        
        try:
            while self.running:
                # Đọc frame
                success = await self._capture_frame()
                
                if not success:
                    logger.error("Lỗi đọc frame từ camera")
                    await asyncio.sleep(0.1)
                    continue
                
                # Tính FPS
                current_time = time.time()
                if self.last_frame_time > 0:
                    self.fps = 1.0 / (current_time - self.last_frame_time)
                self.last_frame_time = current_time
                
                # Gọi callbacks
                await self._notify_callbacks()
                
                # Control FPS
                await asyncio.sleep(1.0 / self.config.fps)
                
        except asyncio.CancelledError:
            logger.info("Capture loop đã bị hủy")
        except Exception as e:
            logger.error(f"Lỗi trong capture loop: {e}")
            self.state = CameraState.ERROR
    
    async def _capture_frame(self) -> bool:
        """
        Capture một frame từ camera.
        
        Returns:
            True nếu capture thành công
        """
        if not self.cap or not self.cap.isOpened():
            return False
        
        # Đọc frame trong thread pool để không block event loop
        loop = asyncio.get_event_loop()
        ret, frame = await loop.run_in_executor(None, self.cap.read)
        
        if not ret or frame is None:
            return False
        
        self.current_frame = frame
        self.frame_count += 1
        
        return True
    
    async def _notify_callbacks(self) -> None:
        """Gọi tất cả frame callbacks."""
        if not self.frame_callbacks or self.current_frame is None:
            return
        
        for callback in self.frame_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.current_frame.copy(), self.frame_count)
                else:
                    callback(self.current_frame.copy(), self.frame_count)
            except Exception as e:
                logger.error(f"Lỗi trong frame callback: {e}")
    
    def register_frame_callback(self, callback: Callable) -> None:
        """
        Đăng ký callback để nhận frames.
        
        Args:
            callback: Hàm callback nhận (frame, frame_count)
        """
        self.frame_callbacks.append(callback)
        logger.debug(f"Đã đăng ký frame callback: {callback.__name__}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Lấy frame hiện tại.
        
        Returns:
            Frame hiện tại hoặc None
        """
        if self.current_frame is not None:
            return self.current_frame.copy()
        return None
    
    def get_frame_size(self) -> tuple[int, int]:
        """
        Lấy kích thước frame.
        
        Returns:
            (width, height)
        """
        if self.cap and self.cap.isOpened():
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        return (self.config.width, self.config.height)
    
    def get_fps(self) -> float:
        """
        Lấy FPS hiện tại.
        
        Returns:
            FPS
        """
        return self.fps
    
    def is_running(self) -> bool:
        """Kiểm tra camera có đang chạy không."""
        return self.state == CameraState.RUNNING and self.running
    
    def get_state(self) -> CameraState:
        """Lấy trạng thái hiện tại."""
        return self.state
    
    def pause(self) -> None:
        """Tạm dừng camera."""
        if self.state == CameraState.RUNNING:
            self.running = False
            self.state = CameraState.PAUSED
            logger.info("Camera đã tạm dừng")
    
    def resume(self) -> None:
        """Tiếp tục camera sau khi pause."""
        if self.state == CameraState.PAUSED:
            self.running = True
            self.state = CameraState.RUNNING
            logger.info("Camera đã tiếp tục")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin camera.
        
        Returns:
            Dictionary chứa thông tin camera
        """
        width, height = self.get_frame_size()
        
        return {
            "state": self.state.value,
            "source": self.source.value,
            "width": width,
            "height": height,
            "fps": self.fps,
            "frame_count": self.frame_count,
            "is_running": self.is_running()
        }