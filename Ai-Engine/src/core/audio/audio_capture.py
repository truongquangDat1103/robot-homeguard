"""
Audio Capture - Thu âm từ microphone.
Hỗ trợ real-time audio streaming và recording.
"""
import asyncio
import time
from typing import Optional, Callable, List
from enum import Enum
import numpy as np
from loguru import logger

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    logger.warning("⚠️  sounddevice chưa cài đặt")

from config.settings import AudioSettings


class AudioState(Enum):
    """Trạng thái audio capture."""
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    ERROR = "error"
    CLOSED = "closed"


class AudioCapture:
    """
    Quản lý thu âm từ microphone.
    Hỗ trợ real-time streaming và callback.
    """
    
    def __init__(self, config: AudioSettings):
        """
        Khởi tạo audio capture.
        
        Args:
            config: Cấu hình audio
        """
        if not SOUNDDEVICE_AVAILABLE:
            raise ImportError("sounddevice chưa cài đặt. Cài: pip install sounddevice")
        
        self.config = config
        self.state = AudioState.IDLE
        
        # Audio stream
        self.stream: Optional[sd.InputStream] = None
        
        # Audio buffer
        self.audio_buffer: List[np.ndarray] = []
        self.max_buffer_size = config.buffer_duration * config.sample_rate
        
        # Callbacks
        self.audio_callbacks: List[Callable] = []
        
        # Statistics
        self.total_frames = 0
        self.start_time = 0.0
        
        # Async control
        self.running = False
        
        logger.info("Audio capture đã khởi tạo")
    
    def list_devices(self) -> List[dict]:
        """
        Liệt kê các audio devices có sẵn.
        
        Returns:
            List các device info
        """
        devices = sd.query_devices()
        
        logger.info("📋 Audio Devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                logger.info(f"  [{i}] {device['name']} (Input: {device['max_input_channels']} channels)")
        
        return devices
    
    def initialize(self, device_id: Optional[int] = None) -> bool:
        """
        Khởi tạo audio stream.
        
        Args:
            device_id: ID của input device (None = default)
            
        Returns:
            True nếu khởi tạo thành công
        """
        if self.state == AudioState.RECORDING:
            logger.warning("Audio đã đang recording")
            return True
        
        logger.info("Đang khởi tạo audio stream...")
        
        try:
            # Tạo input stream
            self.stream = sd.InputStream(
                device=device_id,
                channels=self.config.channels,
                samplerate=self.config.sample_rate,
                blocksize=self.config.chunk_size,
                callback=self._audio_callback
            )
            
            logger.info("✅ Audio stream đã khởi tạo")
            logger.info(f"   Sample rate: {self.config.sample_rate} Hz")
            logger.info(f"   Channels: {self.config.channels}")
            logger.info(f"   Chunk size: {self.config.chunk_size}")
            
            self.state = AudioState.IDLE
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo audio: {e}")
            self.state = AudioState.ERROR
            return False
    
    def start_recording(self) -> bool:
        """
        Bắt đầu recording.
        
        Returns:
            True nếu bắt đầu thành công
        """
        if self.stream is None:
            if not self.initialize():
                return False
        
        if self.state == AudioState.RECORDING:
            logger.warning("Đã đang recording")
            return True
        
        logger.info("Đang bắt đầu recording...")
        
        try:
            self.stream.start()
            self.running = True
            self.state = AudioState.RECORDING
            self.start_time = time.time()
            self.total_frames = 0
            self.audio_buffer.clear()
            
            logger.info("✅ Recording đã bắt đầu")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi start recording: {e}")
            self.state = AudioState.ERROR
            return False
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """
        Dừng recording và trả về audio data.
        
        Returns:
            Audio data (numpy array) hoặc None
        """
        if self.state != AudioState.RECORDING:
            logger.warning("Không đang recording")
            return None
        
        logger.info("Đang dừng recording...")
        
        try:
            self.stream.stop()
            self.running = False
            self.state = AudioState.IDLE
            
            # Lấy audio data từ buffer
            if self.audio_buffer:
                audio_data = np.concatenate(self.audio_buffer, axis=0)
                duration = len(audio_data) / self.config.sample_rate
                
                logger.info(f"✅ Recording đã dừng (duration: {duration:.2f}s)")
                return audio_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Lỗi stop recording: {e}")
            return None
    
    def pause(self) -> None:
        """Tạm dừng recording."""
        if self.state == AudioState.RECORDING:
            self.stream.stop()
            self.state = AudioState.PAUSED
            logger.info("Recording đã tạm dừng")
    
    def resume(self) -> None:
        """Tiếp tục recording sau khi pause."""
        if self.state == AudioState.PAUSED:
            self.stream.start()
            self.state = AudioState.RECORDING
            logger.info("Recording đã tiếp tục")
    
    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info,
        status
    ) -> None:
        """
        Callback được gọi khi có audio data mới.
        
        Args:
            indata: Audio data
            frames: Số frames
            time_info: Timing info
            status: Stream status
        """
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Copy data để tránh overwrite
        audio_chunk = indata.copy()
        
        # Thêm vào buffer
        self.audio_buffer.append(audio_chunk)
        
        # Giới hạn buffer size
        while len(self.audio_buffer) > 0:
            total_samples = sum(len(chunk) for chunk in self.audio_buffer)
            if total_samples <= self.max_buffer_size:
                break
            self.audio_buffer.pop(0)
        
        self.total_frames += frames
        
        # Gọi callbacks
        asyncio.create_task(self._notify_callbacks(audio_chunk))
    
    async def _notify_callbacks(self, audio_chunk: np.ndarray) -> None:
        """
        Thông báo cho các callbacks.
        
        Args:
            audio_chunk: Audio chunk data
        """
        for callback in self.audio_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(audio_chunk)
                else:
                    callback(audio_chunk)
            except Exception as e:
                logger.error(f"Lỗi trong audio callback: {e}")
    
    def register_callback(self, callback: Callable) -> None:
        """
        Đăng ký callback để nhận audio chunks.
        
        Args:
            callback: Hàm callback nhận (audio_chunk)
        """
        self.audio_callbacks.append(callback)
        logger.debug(f"Đã đăng ký audio callback: {callback.__name__}")
    
    def get_buffer(self) -> Optional[np.ndarray]:
        """
        Lấy audio data từ buffer.
        
        Returns:
            Audio data hoặc None
        """
        if not self.audio_buffer:
            return None
        
        return np.concatenate(self.audio_buffer, axis=0)
    
    def clear_buffer(self) -> None:
        """Xóa buffer."""
        self.audio_buffer.clear()
        logger.debug("Audio buffer đã xóa")
    
    def get_recording_duration(self) -> float:
        """
        Lấy thời gian recording hiện tại.
        
        Returns:
            Duration (giây)
        """
        if self.state == AudioState.RECORDING:
            return time.time() - self.start_time
        return 0.0
    
    def get_volume_level(self) -> float:
        """
        Tính volume level hiện tại (RMS).
        
        Returns:
            Volume level (0.0 - 1.0)
        """
        if not self.audio_buffer:
            return 0.0
        
        # Lấy chunk gần nhất
        latest_chunk = self.audio_buffer[-1]
        
        # Tính RMS (Root Mean Square)
        rms = np.sqrt(np.mean(latest_chunk**2))
        
        return float(rms)
    
    def is_recording(self) -> bool:
        """Kiểm tra có đang recording không."""
        return self.state == AudioState.RECORDING
    
    def get_state(self) -> AudioState:
        """Lấy trạng thái hiện tại."""
        return self.state
    
    def release(self) -> None:
        """Giải phóng audio resources."""
        logger.info("Đang giải phóng audio...")
        
        if self.stream:
            if self.stream.active:
                self.stream.stop()
            self.stream.close()
            self.stream = None
        
        self.audio_buffer.clear()
        self.state = AudioState.CLOSED
        logger.info("Audio đã được giải phóng")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin audio capture.
        
        Returns:
            Dictionary chứa thông tin
        """
        return {
            "state": self.state.value,
            "sample_rate": self.config.sample_rate,
            "channels": self.config.channels,
            "chunk_size": self.config.chunk_size,
            "buffer_duration": self.config.buffer_duration,
            "recording_duration": self.get_recording_duration(),
            "total_frames": self.total_frames,
            "volume_level": self.get_volume_level()
        }
    
    def __del__(self):
        """Destructor."""
        self.release()