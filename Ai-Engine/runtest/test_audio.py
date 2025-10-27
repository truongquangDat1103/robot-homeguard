"""Test audio functionality (safe version)."""
import asyncio
import sys, os
import warnings

# Ignore annoying sounddevice CFFI async warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="coroutine .* was never awaited")

# Thêm src vào PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.audio import AudioCapture, SpeechToText, TextToSpeech
from config.settings import settings

async def test_microphone(audio_capture, callback):
    print("\n1️⃣ Testing Microphone...")
    if not audio_capture.initialize():
        print("❌ Cannot initialize microphone")
        return

    # Gắn event loop nếu cần
    try:
        loop = asyncio.get_running_loop()
        setattr(audio_capture, "loop", loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        setattr(audio_capture, "loop", loop)

    audio_capture.list_devices()
    print("\n🎙️  Recording 5 seconds... SPEAK NOW!")
    audio_capture.start_recording()

    try:
        await asyncio.sleep(5)
    except KeyboardInterrupt:
        print("🛑 Recording interrupted")

    audio_data = audio_capture.stop_recording()
    if audio_data is not None:
        print(f"✅ Recorded {len(audio_data)} samples")
        await callback(audio_data)

async def test_speech_to_text(audio_data, callback):
    print("\n2️⃣ Testing Speech-to-Text...")
    stt = SpeechToText(model_size="base")
    try:
        result = await stt.transcribe_async(audio_data, settings.audio.sample_rate)
    except Exception as e:
        print(f"❌ STT Error: {e}")
        result = None

    if result:
        print(f"📝 Transcribed: {result.text}")
        print(f"   Language: {result.language}")
        print(f"   Confidence: {result.confidence:.2f}")
    else:
        print("❌ Transcription failed")

    await callback()

async def test_text_to_speech():
    print("\n3️⃣ Testing Text-to-Speech...")
    tts = TextToSpeech(language="vi")
    test_texts = [
        "Xin chào, tôi là robot AI",
        "Hôm nay thời tiết thế nào?",
        "Cảm ơn bạn đã test chức năng của tôi",
    ]
    for text in test_texts:
        print(f"🔊 Speaking: {text}")
        try:
            await tts.speak_async(text, play_audio=True)
        except Exception as e:
            print(f"⚠️ Error speaking: {e}")
        await asyncio.sleep(1)

async def test_audio():
    print("🎤 Testing Audio...")
    audio_capture = AudioCapture(settings.audio)

    await test_microphone(audio_capture, lambda audio_data: test_speech_to_text(audio_data, test_text_to_speech))
    audio_capture.release()
    print("\n✅ Audio test completed (callback mode)")

if __name__ == "__main__":
    try:
        asyncio.run(test_audio())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_audio())
