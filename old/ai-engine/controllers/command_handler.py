class CommandHandler:
    def __init__(self,robot_assistant):
        self.robot_assistant = robot_assistant
    def handle_command(self,ai_response : dict ):
        """lấy dữ liêuj lệnh từ ai_response"""
        intent = ai_response['command']['intent']
        command = ai_response['command']['command']
        params = ai_response['command'].get('params', {}) # Lấy params nếu có, nếu không có thì trả về dict rỗng
        if intent == "control_device":
            match command:
                case "enable_face_recognition":
                    self.robot_assistant.face_recognizer.recognize_from_camera()
                case "enable_motion_detection":
                    self.robot_assistant.motion_detector.run()
                case _:
                    self.robot_assistant.tts.speak("Xin lỗi, tôi không hiểu lệnh của bạn.")