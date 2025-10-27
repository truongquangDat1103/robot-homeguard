from pprint import pprint
from config.settings import Settings  # Đổi thành đường dẫn đúng tới class Settings của bạn

settings = Settings()

print("\n📦 Cấu hình đã load từ .env:")
print("🌐 WebSocket:")
pprint(settings.websocket.model_dump())

print("\n📷 Camera:")
pprint(settings.camera.model_dump())

print("\n🔊 Audio:")
pprint(settings.audio.model_dump())

print("\n🧠 LLM:")
pprint(settings.llm.model_dump())
