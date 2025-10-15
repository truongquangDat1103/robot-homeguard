from pydub import AudioSegment
import serial
import time

# 🔄 Chuyển định dạng WAV
sound = AudioSegment.from_wav("ai_response.wav")
converted = sound.set_channels(2).set_frame_rate(44100).set_sample_width(2)

# Lấy dữ liệu nhị phân từ AudioSegment
raw_data = converted.raw_data

# 🚀 Gửi qua Serial đến ESP32
ser = serial.Serial("COM4", baudrate=115200, timeout=1)

chunk_size = 1024
for i in range(0, len(raw_data), chunk_size):
    chunk = raw_data[i:i+chunk_size]
    ser.write(chunk)
    time.sleep(0.005)  # delay nhẹ tránh tràn UART buffer

ser.close()
