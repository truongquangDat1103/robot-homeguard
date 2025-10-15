import pyttsx3                             
import os                                   
from datetime import datetime               
class Pyttsx3TTS:                                                                          # Định nghĩa class TTS để quản lý việc đọc và lưu giọng nói
    def __init__(self, voice_index: int = 1, rate: int = 150, volume: float = 1.0):
        self.voice_index = voice_index       
        self.rate        = rate             
        self.volume      = volume           

    def speak(self, text: str):
        engine = pyttsx3.init()                                         # Khởi tạo engine TTS mới, engine là đối tượng điều khiển Text-to-Speech (TTS). Nói cách khác, nó là “trái tim” của TTS, nơi bạn ra lệnh để máy nói, thiết lập giọng, tốc độ, âm lượng, hoặc lưu ra file âm thanh.
        voices = engine.getProperty('voices')                           # Lấy danh sách các giọng có sẵn
        engine.setProperty('voice', voices[self.voice_index].id)      # Chọn giọng theo voice_index
        engine.setProperty('rate', self.rate)                          # Thiết lập tốc độ đọc
        engine.setProperty('volume', self.volume)                      # Thiết lập âm lượng
        engine.say(text)                                                # Thêm đoạn text vào hàng đợi để đọc
        engine.runAndWait()                                             # Thực thi việc đọc và chờ cho đến khi hoàn thành
                                                                        # Không cần gọi stop() vì runAndWait() sẽ tự dừng engine khi đọc xong

    def save_to_wav(self, text: str, filename: str = None, save_dir: str = "saveaudio"):
        os.makedirs(save_dir, exist_ok=True)                               # Tạo thư mục lưu file nếu chưa tồn tại
        if not filename:                                                    # Nếu người dùng không cung cấp tên file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")           # Tạo timestamp dựa trên thời gian hiện tại
            filename  = f"recording_{timestamp}.wav"                       # Tạo tên file mặc định theo timestamp
        filepath = os.path.join(save_dir, filename)                         # Tạo đường dẫn đầy đủ đến file
        engine   = pyttsx3.init()                                           # Khởi tạo engine TTS khác cho việc lưu file
        voices   = engine.getProperty('voices')                              
        engine.setProperty('voice', voices[self.voice_index].id)           
        engine.setProperty('rate', self.rate)                                
        engine.setProperty('volume', self.volume)                            
        engine.save_to_file(text, filepath)                                  
        engine.runAndWait()                                                  
        print(f"✅ Đã lưu giọng nói vào file: {filepath}")                   # In thông báo khi lưu thành công
