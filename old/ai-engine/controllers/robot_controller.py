import json

class RobotController:
    def __init__(self,robot_assistant):
        self.robot_assistant = robot_assistant

    def run(self):
        print("Khởi động Robot Pet HomeGuard AI!")
        while True:
            try:                                                                
                time_seconds = int(input("Nhập thời gian thu âm (giây): "))
            except ValueError:
                print("Vui lòng nhập một số nguyên hợp lệ!")
            except KeyboardInterrupt:
                print("\nĐang thoát chương trình...")
                break
            print("Thu âm lệnh từ người dùng...")
            audio_file = self.robot_assistant.recorder.record(duration=time_seconds)
            user_text = self.robot_assistant.stt.transcribe(audio_file)
            print(f"Bạn nói: {user_text}")
            AI_reply = self.robot_assistant.ai_chat.ask(user_text)
            print("🤖 AI trả về:", AI_reply)
            data = json.loads(AI_reply)                                 # Chuyển chuỗi JSON thành dict, một kiểu dữ liệu rất mạnh mẽ dùng để lưu trữ thông tin dưới dạng cặp khóa–giá trị (key–value).
            self.robot_assistant.tts.speak(data["reply"])
            self.robot_assistant.tts.save_to_wav(data["reply"], "ai_response.wav")
            self.robot_assistant.command_handler.handle_command(data)            # Xử lý lệnh từ AI
            
