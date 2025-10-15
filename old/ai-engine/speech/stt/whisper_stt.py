import sounddevice as sd
from scipy.io.wavfile import write
from transformers import pipeline

class PhoWhisperSTT:
    #hàm khởi tạo cóntructor
    def __init__(self, model_name="vinai/PhoWhisper-medium", sample_rate=16000):
        """
        Khởi tạo bộ nhận dạng giọng nói PhoWhisper
        :param model_name: Tên model PhoWhisper (small, medium, large)
        :param sample_rate: Tần số lấy mẫu (Hz)
        """
        self.model_name = model_name
        self.sample_rate = sample_rate
        self.transcriber = pipeline(        #khởi tạo một pipeline nhận dạng giọng nói (Speech-to-Text) bằng thư viện Transformers của Hugging Face. Dùng để gọi khi muốn nhận dạng giọng nói
            "automatic-speech-recognition",
            model=self.model_name
        )

    def transcribe(self, filename="recorded.wav"):
        """
        Nhận dạng giọng nói từ file wav
        :param filename: đường dẫn tới file wav
        :return: text (string)
        """
        try:
            result = self.transcriber(filename, generate_kwargs={"language": "vi"}) #chuyển âm thanh thành văn bản rồi lưu vài biến
            text = result["text"]
            return text.strip()
        except Exception as e:
            return f"❌ Lỗi nhận dạng: {e}"
