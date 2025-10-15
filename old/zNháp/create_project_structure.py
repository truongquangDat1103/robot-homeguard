import os

# Định nghĩa cấu trúc dự án
project_structure = {
    "robot_pet_homeguard": {
        "esp32_firmware": {
            "main.cpp": "",
            "config.h": "",
            "sensors": {
                "Camera.h": "",
                "Camera.cpp": "",
                "MotionSensor.h": "",
                "MotionSensor.cpp": "",
                "Microphone.h": "",
                "Microphone.cpp": "",
            },
            "actuators": {
                "Motor.h": "",
                "Motor.cpp": "",
                "Servo.h": "",
                "Servo.cpp": "",
            },
        },
        "laptop_ai": {
            "main.py": "",
            "config.py": "",
            "model": {
                "detector.py": "",
                "behavior.py": "",
                "qwen_ai.py": "",
            },
            "speech": {
                "stt_whisper.py": "",
                "tts_pyttsx3.py": "",
                "voice_assistant.py": "",
            },
            "communication": {
                "mqtt_client.py": "",
                "websocket_client.py": "",
            },
            "utils": {
                "logger.py": "",
                "video_stream.py": "",
            },
        },
        "database": {
            "schema.sql": "",
            "migrations": {},
        },
        "docs": {
            "architecture.md": "",
            "setup_guide.md": "",
        },
        "requirements.txt": "",
        "README.md": "# Robot Pet HomeGuard\n\nDự án Robot thú cưng trông nhà kết hợp ESP32 + Laptop AI",
    }
}

def create_structure(base_path, structure):
    """
    Hàm đệ quy tạo thư mục & file theo cấu trúc định nghĩa
    """
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):  # Nếu là folder
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:  # Nếu là file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    base_dir = "."  # Thư mục hiện tại
    create_structure(base_dir, project_structure)
    print("✅ Cấu trúc dự án đã được tạo thành công!")
