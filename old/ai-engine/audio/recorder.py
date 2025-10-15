import sounddevice as sd          # Thư viện thu âm từ micro
from scipy.io.wavfile import write # Dùng để ghi dữ liệu âm thanh thành file WAV
import numpy as np                 # Xử lý dữ liệu dạng mảng số học
import os                          # Quản lý đường dẫn, thư mục
from datetime import datetime      # Tạo timestamp (thời gian hiện tại) cho tên file


class Recorder:
    def __init__(self, sample_rate: int = 16000, channels: int = 1, save_dir: str = "recordings"):
        self.sample_rate = sample_rate      # Tần số lấy mẫu (Hz), mặc định 16kHz
        self.channels = channels            # Số kênh: 1 = mono, 2 = stereo
        self.save_dir = save_dir            # Thư mục lưu file âm thanh
        os.makedirs(save_dir, exist_ok=True) # Nếu thư mục chưa có thì tạo mới

    def record(self, duration: int = 5, filename: str = None) -> str:
        """
        Thu âm từ micro và lưu thành file WAV.
        :param duration: thời gian thu âm (giây)
        :param filename: tên file mong muốn (nếu None thì tự sinh theo timestamp)
        :return: đường dẫn file WAV
        """
        print(f"[Recorder] Bắt đầu thu âm {duration} giây...")

        # Thu âm, dữ liệu lưu dạng numpy array (int16)
        recording = sd.rec(int(duration * self.sample_rate),
                           samplerate=self.sample_rate,
                           channels=self.channels,
                           dtype='int16')
        sd.wait()  # Chờ thu âm xong

        # Nếu chưa có tên file thì tự sinh dựa trên thời gian
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 
            filename = f"recording_{timestamp}.wav" 

        filepath = os.path.join(self.save_dir, filename) #lưu filename vào savedir

        # Ghi dữ liệu ra file WAV
        write(filepath, self.sample_rate, recording)

        print(f"[Recorder] Đã lưu file: {filepath}")
        return filepath

    def record_to_array(self, duration: int = 5) -> np.ndarray:
        """
        Thu âm và trả về dữ liệu numpy array (không lưu file).
        Dùng khi muốn xử lý trực tiếp (ví dụ gửi sang AI).
        """
        print(f"[Recorder] Bắt đầu thu âm {duration} giây (array mode)...")
        recording = sd.rec(int(duration * self.sample_rate),
                           samplerate=self.sample_rate,
                           channels=self.channels,
                           dtype='int16')
        sd.wait()
        print("[Recorder] Thu âm xong, trả về numpy array.")
        return recording
