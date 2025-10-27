"""
Noise Reducer - Giảm nhiễu trong audio.
Preprocessing audio trước khi xử lý STT hoặc voice recognition.
"""
import numpy as np
from loguru import logger

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("⚠️  librosa chưa cài đặt")

try:
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("⚠️  scipy chưa cài đặt")


class NoiseReducer:
    """
    Giảm nhiễu audio sử dụng spectral subtraction và filtering.
    """
    
    def __init__(
        self,
        noise_reduce_amount: float = 0.5,
        noise_floor: float = 0.01
    ):
        """
        Khởi tạo noise reducer.
        
        Args:
            noise_reduce_amount: Mức độ giảm nhiễu (0.0 - 1.0)
            noise_floor: Ngưỡng nhiễu tối thiểu
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("librosa chưa cài đặt. Cài: pip install librosa")
        
        self.noise_reduce_amount = noise_reduce_amount
        self.noise_floor = noise_floor
        
        logger.info("Noise reducer đã khởi tạo")
    
    def reduce_noise(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        method: str = "spectral"
    ) -> np.ndarray:
        """
        Giảm nhiễu trong audio.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            method: Phương pháp ("spectral", "filter", "gate")
            
        Returns:
            Audio data đã giảm nhiễu
        """
        if audio_data is None or audio_data.size == 0:
            return audio_data
        
        try:
            # Chuẩn bị audio
            audio = self._prepare_audio(audio_data)
            
            # Áp dụng phương pháp giảm nhiễu
            if method == "spectral":
                audio_clean = self._spectral_subtraction(audio, sample_rate)
            elif method == "filter":
                audio_clean = self._apply_filter(audio, sample_rate)
            elif method == "gate":
                audio_clean = self._noise_gate(audio)
            else:
                logger.warning(f"Phương pháp không hợp lệ: {method}")
                return audio_data
            
            logger.debug(f"Đã giảm nhiễu (method: {method})")
            return audio_clean
            
        except Exception as e:
            logger.error(f"Lỗi reduce noise: {e}")
            return audio_data
    
    def _prepare_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Chuẩn bị audio data.
        
        Args:
            audio_data: Audio data
            
        Returns:
            Audio data đã chuẩn bị
        """
        # Convert sang mono nếu stereo
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
        
        # Flatten
        audio_data = audio_data.flatten()
        
        # Normalize
        max_val = np.abs(audio_data).max()
        if max_val > 0:
            audio_data = audio_data / max_val
        
        return audio_data
    
    def _spectral_subtraction(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> np.ndarray:
        """
        Giảm nhiễu bằng spectral subtraction.
        
        Args:
            audio: Audio data
            sample_rate: Sample rate
            
        Returns:
            Audio đã giảm nhiễu
        """
        # Compute STFT
        stft = librosa.stft(audio)
        magnitude, phase = np.abs(stft), np.angle(stft)
        
        # Estimate noise từ các frame đầu (giả sử đầu file là noise)
        noise_frames = 10
        noise_estimate = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
        
        # Subtract noise
        magnitude_clean = magnitude - (self.noise_reduce_amount * noise_estimate)
        
        # Clipping để không âm
        magnitude_clean = np.maximum(magnitude_clean, self.noise_floor)
        
        # Reconstruct
        stft_clean = magnitude_clean * np.exp(1j * phase)
        audio_clean = librosa.istft(stft_clean)
        
        return audio_clean
    
    def _apply_filter(
        self,
        audio: np.ndarray,
        sample_rate: int
    ) -> np.ndarray:
        """
        Áp dụng bandpass filter để loại nhiễu.
        
        Args:
            audio: Audio data
            sample_rate: Sample rate
            
        Returns:
            Audio đã filter
        """
        if not SCIPY_AVAILABLE:
            logger.warning("scipy không có, không thể filter")
            return audio
        
        # Bandpass filter (300Hz - 3400Hz cho voice)
        lowcut = 300.0
        highcut = 3400.0
        
        nyquist = sample_rate / 2.0
        low = lowcut / nyquist
        high = highcut / nyquist
        
        # Butterworth filter
        b, a = signal.butter(4, [low, high], btype='band')
        audio_filtered = signal.filtfilt(b, a, audio)
        
        return audio_filtered
    
    def _noise_gate(
        self,
        audio: np.ndarray,
        threshold: float = 0.01
    ) -> np.ndarray:
        """
        Noise gate - mute các phần audio dưới threshold.
        
        Args:
            audio: Audio data
            threshold: Ngưỡng gate
            
        Returns:
            Audio đã gate
        """
        # Tính envelope (RMS)
        frame_length = 2048
        hop_length = 512
        
        rms = librosa.feature.rms(
            y=audio,
            frame_length=frame_length,
            hop_length=hop_length
        )[0]
        
        # Upsample RMS về kích thước audio gốc
        rms_upsampled = np.repeat(rms, hop_length)
        
        # Pad nếu cần
        if len(rms_upsampled) < len(audio):
            rms_upsampled = np.pad(
                rms_upsampled,
                (0, len(audio) - len(rms_upsampled)),
                mode='edge'
            )
        else:
            rms_upsampled = rms_upsampled[:len(audio)]
        
        # Apply gate
        mask = rms_upsampled > threshold
        audio_gated = audio * mask
        
        return audio_gated
    
    def normalize(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio về [-1, 1].
        
        Args:
            audio_data: Audio data
            
        Returns:
            Audio đã normalize
        """
        max_val = np.abs(audio_data).max()
        
        if max_val > 0:
            return audio_data / max_val
        
        return audio_data
    
    def trim_silence(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        top_db: int = 30
    ) -> np.ndarray:
        """
        Cắt bỏ silence ở đầu và cuối audio.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            top_db: Ngưỡng dB để coi là silence
            
        Returns:
            Audio đã trim
        """
        try:
            audio = self._prepare_audio(audio_data)
            
            # Trim silence
            audio_trimmed, _ = librosa.effects.trim(
                audio,
                top_db=top_db
            )
            
            logger.debug(f"Đã trim silence (top_db: {top_db})")
            return audio_trimmed
            
        except Exception as e:
            logger.error(f"Lỗi trim silence: {e}")
            return audio_data
    
    def apply_gain(
        self,
        audio_data: np.ndarray,
        gain_db: float
    ) -> np.ndarray:
        """
        Áp dụng gain (tăng/giảm âm lượng).
        
        Args:
            audio_data: Audio data
            gain_db: Gain (dB)
            
        Returns:
            Audio với gain
        """
        # Convert dB sang linear
        gain_linear = 10 ** (gain_db / 20.0)
        
        audio_gained = audio_data * gain_linear
        
        # Clip để tránh overflow
        audio_gained = np.clip(audio_gained, -1.0, 1.0)
        
        return audio_gained
    
    def remove_dc_offset(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Loại bỏ DC offset (dịch chuyển trung tâm về 0).
        
        Args:
            audio_data: Audio data
            
        Returns:
            Audio đã remove DC offset
        """
        mean = np.mean(audio_data)
        return audio_data - mean
    
    def preprocess(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000,
        trim_silence: bool = True,
        reduce_noise: bool = True,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Preprocessing pipeline đầy đủ.
        
        Args:
            audio_data: Audio data
            sample_rate: Sample rate
            trim_silence: Có trim silence không
            reduce_noise: Có giảm nhiễu không
            normalize: Có normalize không
            
        Returns:
            Audio đã preprocess
        """
        audio = audio_data.copy()
        
        # Remove DC offset
        audio = self.remove_dc_offset(audio)
        
        # Trim silence
        if trim_silence:
            audio = self.trim_silence(audio, sample_rate)
        
        # Reduce noise
        if reduce_noise:
            audio = self.reduce_noise(audio, sample_rate)
        
        # Normalize
        if normalize:
            audio = self.normalize(audio)
        
        logger.debug("Audio preprocessing hoàn tất")
        return audio
    
    def get_info(self) -> dict:
        """
        Lấy thông tin noise reducer.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "noise_reduce_amount": self.noise_reduce_amount,
            "noise_floor": self.noise_floor,
            "librosa_available": LIBROSA_AVAILABLE,
            "scipy_available": SCIPY_AVAILABLE
        }