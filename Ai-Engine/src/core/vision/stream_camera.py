# src/core/vision/stream_camera.py
import cv2
import requests
import numpy as np

class StreamCamera:
    """Đọc video stream từ ESP32-CAM qua HTTP"""
    
    def __init__(self, stream_url: str):
        self.stream_url = stream_url
        self.stream = None
    
    def connect(self):
        """Kết nối đến stream"""
        self.stream = requests.get(
            self.stream_url, 
            stream=True,
            timeout=5
        )
    
    def read_frame(self):
        """Đọc frame từ MJPEG stream"""
        bytes_data = b''
        for chunk in self.stream.iter_content(chunk_size=1024):
            bytes_data += chunk
            # Tìm JPEG boundaries
            a = bytes_data.find(b'\xff\xd8')  # JPEG start
            b = bytes_data.find(b'\xff\xd9')  # JPEG end
            
            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                
                # Decode JPEG
                frame = cv2.imdecode(
                    np.frombuffer(jpg, dtype=np.uint8),
                    cv2.IMREAD_COLOR
                )
                return frame
        return None