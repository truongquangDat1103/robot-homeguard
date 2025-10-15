from model.llm.qwen_llm import Qwen3Chat
from speech.stt.whisper_stt import PhoWhisperSTT
from speech.tts.pyttsx3_tts import Pyttsx3TTS
from audio.recorder import Recorder
from model.vision.face_recognizer import FaceRecognizer
from model.vision.motion_detector import MotionDetector
from controllers.command_handler import CommandHandler
from controllers.robot_controller import RobotController


class RobotAssistant:
    """Khởi tạo các module AI và giọng nói cho trợ lý robot."""
    def __init__(self):
        print("🔧 Khởi tạo RobotAssistant...")
        self.ai_chat = Qwen3Chat()
        self.stt = PhoWhisperSTT()
        self.tts = Pyttsx3TTS()
        self.recorder = Recorder()
        self.face_recognizer = FaceRecognizer()
        self.motion_detector = MotionDetector()
        self.command_handler = CommandHandler(self)
        self.robot_controller = RobotController(self)