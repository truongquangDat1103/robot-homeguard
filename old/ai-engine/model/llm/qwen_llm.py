import ollama

class Qwen3Chat:
    #hàm khởi tạo constructer 
    def __init__(self, model="qwen3:8b"):
        self.model = model 
        self.system_prompt =  """
                                    Bạn là Robot thú cưng trông nhà. 
                                    Nhiệm vụ của bạn:
                                    - Nghe lệnh hoặc trò chuyện với con người.
                                    - Luôn trả về kết quả ở định dạng JSON duy nhất, không thêm giải thích.

                                    Cấu trúc JSON chuẩn:

                                    {
                                    "reply": "Câu trả lời tự nhiên dành cho người dùng (dùng để đọc ra loa)",
                                    "command": {
                                        "intent": "string (vd: control_device, query_info, conversation, security_alert, ...)",
                                        "command": "string (hành động chính, vd: turn_on_light, move_forward, ask_weather, chitchat,enable_face_recognition,enable_motion_detection)",
                                        "params": { "key": "value" }  // Tham số kèm theo, không có thì "params": {}
                                    }
                                    }

                                    Yêu cầu:
                                    - Luôn trả về JSON hợp lệ.
                                    - Không thêm chữ ngoài JSON.
                                    - Nếu chỉ trò chuyện xã giao thì intent = "conversation", command = "chitchat".
                                """
        self.history = [
            {"role": "system", "content": self.system_prompt} #khởi tạo vai trò của ai
        ]

    def ask(self, user_input: str) -> str:
        """
        Gửi câu hỏi của user tới Qwen3 và nhận câu trả lời
        """
        
        self.history.append({"role": "user", "content": user_input})# Thêm message của user vào lịch sử

        try:
            # Gọi API Ollama để chat với Qwen3
            response = ollama.chat(
                model=self.model,
                messages=self.history,
                think=False
            )

            # Lấy content trả lời
            ai_reply = response['message']['content']

            # Lưu lại vào lịch sử hội thoại
            self.history.append({"role": "assistant", "content": ai_reply})

            return ai_reply
        #xử lý ngoại lệ    
        except Exception as e:
            return f"Lỗi khi gọi Qwen3: {e}"

    def reset(self):
        """Reset hội thoại về trạng thái ban đầu"""
        self.history = [
            {"role": "system", "content": self.system_prompt}
        ]

