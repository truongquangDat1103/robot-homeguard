import sounddevice as sd
from scipy.io.wavfile import write
from transformers import pipeline

# Cấu hình thu âm
fs = 16000  # sample rate
seconds = 5  # thời gian thu âm (có thể thay đổi)

print("Bắt đầu thu âm, nói vào micro...")
myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
sd.wait()
write("recorded.wav", fs, myrecording)
print("Thu âm xong! File lưu: recorded.wav")

# Chuyển đổi giọng nói thành văn bản
transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-medium")
result = transcriber("recorded.wav", generate_kwargs={"language": "vi"})
print("Kết quả nhận dạng:")
print(result["text"])
