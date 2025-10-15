🤖 AI-Engine
Advanced AI System for Intelligent Robots with Computer Vision, Audio Processing, and Natural Language Understanding.

🌟 Features
🎥 Computer Vision: Face detection & recognition, motion detection, object detection, pose estimation
🎤 Audio Processing: Speech-to-text, text-to-speech, voice recognition, sound classification
💬 Natural Language Processing: LLM integration, conversation management, intent classification
🧠 Behavior Engine: Emotion simulation, personality traits, intelligent decision making
📊 Real-time Analytics: Sensor analysis, anomaly detection, pattern recognition
🔌 WebSocket Communication: Real-time bidirectional communication with robot hardware
🚀 Quick Start
Prerequisites
Python 3.10+
Poetry (recommended) or pip
CUDA-compatible GPU (optional, for better performance)
Installation
Clone the repository
bash
git clone https://github.com/yourusername/ai-engine.git
cd ai-engine
Install dependencies using Poetry
bash
poetry install
Or using pip:

bash
pip install -r requirements.txt
Setup environment variables
bash
cp .env.example .env
# Edit .env with your configuration
Download AI models (if needed)
bash
python scripts/setup.sh
Running the Application
bash
# Using Poetry
poetry run python main.py

# Or directly
python main.py
📁 Project Structure
Ai-Engine/
├── config/              # Configuration files
│   ├── settings.py      # Pydantic settings
│   ├── logging.yaml     # Logging configuration
│   └── models.yaml      # AI model configs
│
├── src/
│   ├── core/           # Core AI engines
│   │   ├── vision/     # Computer vision
│   │   ├── audio/      # Audio processing
│   │   ├── nlp/        # NLP & LLM
│   │   ├── behavior/   # Robot behavior
│   │   └── analytics/  # Data analytics
│   │
│   ├── services/       # Application services
│   ├── models/         # ML models & data
│   ├── data/          # Data pipelines
│   └── utils/         # Utilities
│
├── tests/             # Test suite
├── scripts/           # Automation scripts
├── docs/             # Documentation
└── main.py           # Entry point
🔧 Configuration
Environment Variables
Key configuration options in .env:

bash
# WebSocket
WEBSOCKET_URL=ws://192.168.1.100:8080/ws

# Camera
CAMERA_INDEX=0
CAMERA_FPS=30
ENABLE_FACE_DETECTION=true

# Audio
AUDIO_SAMPLE_RATE=16000
STT_MODEL=base

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here

# Robot
ROBOT_NAME=Atlas
ROBOT_PERSONALITY=friendly
Feature Flags
Enable/disable features as needed:

bash
ENABLE_FACE_RECOGNITION=true
ENABLE_VOICE_RECOGNITION=true
ENABLE_CONVERSATION=true
ENABLE_BEHAVIOR_ENGINE=true
🧪 Testing
bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test
poetry run pytest tests/unit/test_vision.py
📊 Performance
Face Detection: ~30 FPS on GPU, ~10 FPS on CPU
Speech Recognition: Real-time with Whisper base model
LLM Response Time: 2-5 seconds (depends on provider)
Memory Usage: ~2GB RAM, ~4GB VRAM (with GPU)
🛠️ Development
Code Style
bash
# Format code
poetry run black src/

# Sort imports
poetry run isort src/

# Type checking
poetry run mypy src/
Adding New Features
Create feature branch: git checkout -b feature/new-feature
Implement in appropriate module under src/core/
Add tests in tests/
Update documentation
Submit pull request
🔒 Security
API keys stored in .env (never commit!)
WebSocket authentication supported
Input validation using Pydantic
Secure by default configuration
📈 Monitoring
Structured logging with Loguru
Performance metrics tracking
Health check endpoint (if API enabled)
Optional Sentry integration for error tracking
🐳 Docker Support
bash
# Build image
docker build -t ai-engine .

# Run container
docker-compose up -d

# With GPU support
docker-compose -f docker-compose.gpu.yml up -d
📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🤝 Contributing
Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

📞 Support
Documentation: docs/
Issues: GitHub Issues
Discussions: GitHub Discussions
🙏 Acknowledgments
OpenCV for computer vision
Whisper for speech recognition
Anthropic/OpenAI for LLM capabilities
All open-source contributors
Built with ❤️ for intelligent robotics


--------------------------------------------
🗓️ 2. Roadmap phát triển theo giai đoạn
🧱 Giai đoạn 1 – Foundation (Tuần 1–2)

Mục tiêu: Xây nền tảng & test logging hoạt động.

File chính	Vai trò
config/settings.py	Quản lý config (Pydantic)
src/utils/logger.py	Hệ thống logging thống nhất
src/utils/constants.py	Định nghĩa hằng số toàn cục
.env.example	Mẫu cấu hình môi trường
main.py	Entry point – test logger và config

Kết quả test:

python main.py
# -> [INFO] AI Engine initialized successfully

🌐 Giai đoạn 2 – WebSocket Core (Tuần 3–4)

Mục tiêu: Kết nối robot hoặc server trung tâm.

File chính	Vai trò
src/services/websocket/client.py	Kết nối & duy trì WS
src/services/websocket/message_handler.py	Xử lý message in/out
src/services/websocket/protocols.py	Định nghĩa message schema

Kết quả test:

Kết nối WebSocket thành công.

Log hiển thị message gửi & nhận.

🎥 Giai đoạn 3 – Vision Pipeline (Tuần 5–6)

Mục tiêu: Nhận luồng camera & hiển thị realtime.

File chính	Vai trò
src/core/vision/camera_manager.py	Quản lý camera
src/data/buffers/video_buffer.py	Bộ nhớ khung hình
src/data/processors/video_processor.py	Tiền xử lý frame
src/services/camera_service.py	Orchestrator cho vision

Kết quả test:

Mở webcam, hiển thị hình ảnh realtime.

😎 Giai đoạn 4 – Face Detection & Recognition (Tuần 7–8)

Mục tiêu: Nhận diện & ghi nhớ khuôn mặt.

File chính	Vai trò
src/core/vision/face_detector.py	Phát hiện khuôn mặt (YOLO/MTCNN)
src/core/vision/face_recognizer.py	Nhận dạng người quen (FaceNet)
scripts/collect_faces.py	Tool thu thập khuôn mặt
src/models/face_recognition/	Database embeddings & metadata

Kết quả test:

Nhận diện người đã lưu trong database.

🎤 Giai đoạn 5 – Audio & NLP (Tuần 9–10)

Mục tiêu: Cho robot nghe & hiểu.

File chính	Vai trò
src/core/audio/audio_capture.py	Thu âm từ mic
src/core/audio/speech_to_text.py	STT (Whisper)
src/core/nlp/llm_manager.py	Kết nối Ollama/OpenAI
src/core/nlp/conversation_engine.py	Quản lý hội thoại
src/services/voice_service.py	Orchestrator âm thanh
src/services/llm_service.py	Tích hợp LLM trả lời

Kết quả test:

Robot nghe & phản hồi text cơ bản.

🤖 Giai đoạn 6 – Behavior & Analytics (Tuần 11–12)

Mục tiêu: Tạo trí tuệ hành vi & phân tích hệ thống.

File chính	Vai trò
src/core/behavior/behavior_engine.py	FSM quản lý trạng thái
src/core/behavior/decision_maker.py	Logic ra quyết định
src/core/analytics/sensor_analyzer.py	Phân tích dữ liệu cảm biến
src/services/health_monitor.py	Theo dõi tình trạng hệ thống
🧱 Giai đoạn 7 – API, Docker & Docs (Tuần 13–14)

Mục tiêu: Hoàn thiện hệ thống & dễ triển khai.

File chính	Vai trò
src/api/routes.py	API test/debug
docker/Dockerfile, docker-compose.yml	Triển khai container
docs/ARCHITECTURE.md, README.md	Tài liệu hệ thống
----------------------------------------
🏗️ Giai đoạn 1: Foundation (Tuần 1-2)
1. Config & Utils (Xây dựng đầu tiên)

config/settings.py - Cấu hình cơ bản
src/utils/logger.py - Logging system
src/utils/constants.py - Các hằng số
.env.example và setup môi trường

Lý do: Đây là nền tảng cho mọi module khác, bạn sẽ dùng logger và config ở khắp nơi.
2. WebSocket Service (Xây dựng thứ hai)

src/services/websocket/client.py
src/services/websocket/message_handler.py
src/services/websocket/protocols.py

Lý do: Đây là kết nối với robot, không có nó thì không nhận/gửi data được.

🎯 Giai đoạn 2: Core Modules (Tuần 3-4)
3. Camera Pipeline (Module đầu tiên)
src/core/vision/camera_manager.py  → Nhận video stream
src/data/buffers/video_buffer.py   → Buffer frames
src/data/processors/video_processor.py → Xử lý frames
src/services/camera_service.py     → Orchestrator
```

**Test ngay**: Kết nối camera, hiển thị video realtime.

### 4. **Face Detection** (Tính năng đầu tiên)
- `src/core/vision/face_detector.py` (dùng YOLO hoặc MTCNN)
- Test: Detect faces từ camera stream

---

## 🚀 Giai đoạn 3: AI Features (Tuần 5-8)

### 5. **Face Recognition**
- `src/core/vision/face_recognizer.py`
- `src/models/face_recognition/` - Database embeddings
- `scripts/collect_faces.py` - Tool thu thập dữ liệu

### 6. **Audio Pipeline**
```
src/core/audio/audio_capture.py
src/core/audio/speech_to_text.py (Whisper)
src/services/voice_service.py
```

### 7. **NLP & Conversation**
```
src/core/nlp/llm_manager.py (Ollama)
src/core/nlp/conversation_engine.py
src/services/llm_service.py

📊 Giai đoạn 4: Intelligence (Tuần 9-12)
8. Behavior Engine

src/core/behavior/behavior_engine.py
src/core/behavior/decision_maker.py

9. Analytics & Monitoring

src/services/health_monitor.py
src/core/analytics/sensor_analyzer.py


⚡ Checklist Từng Bước
python# Bước 1: Tạo file đầu tiên
✅ config/settings.py
✅ src/utils/logger.py  
✅ main.py (test logging)

# Bước 2: WebSocket
✅ src/services/websocket/client.py
✅ Test kết nối với robot

# Bước 3: Camera
✅ src/core/vision/camera_manager.py
✅ Test hiển thị video stream

# Bước 4: Face Detection
✅ src/core/vision/face_detector.py
✅ Test detect faces realtime

# Bước 5: Face Recognition
✅ scripts/collect_faces.py
✅ src/core/vision/face_recognizer.py
✅ Test nhận diện người quen

# Tiếp tục...

💡 Chiến lược Recommend
1. Minimum Viable Product (MVP) đầu tiên:

WebSocket ↔ Camera ↔ Face Detection
Chỉ 3-4 files, test ngay được

2. Incremental Development:

Mỗi module test riêng trước khi tích hợp
Viết test ngay từ đầu (tests/unit/)

3. Dùng Docker từ sớm:

Setup docker/Dockerfile từ giai đoạn 2
Tránh "works on my machine" problem
-------------------------------------------------
Giải Thích Chi Tiết Cấu Trúc Dự Án AI-Engine
📁 Root Level Files
README.md

Tài liệu chính của dự án
Giới thiệu tổng quan, hướng dẫn cài đặt, sử dụng
Là nơi đầu tiên người mới xem khi mở project

pyproject.toml

File cấu hình cho Poetry (công cụ quản lý dependencies hiện đại)
Định nghĩa tên project, version, dependencies, scripts
Thay thế cho setup.py truyền thống

poetry.lock

File lock các phiên bản chính xác của dependencies
Đảm bảo môi trường giống nhau trên mọi máy
Được Poetry tự động tạo

requirements.txt

Backup cho pip truyền thống (không dùng Poetry)
List tất cả thư viện cần thiết với version
Dùng: pip install -r requirements.txt

.env.example

Template cho file .env (chứa secrets, API keys)
Người dùng copy thành .env và điền thông tin thật
Ví dụ: OPENAI_API_KEY=your_key_here

.gitignore

Danh sách file/folder không push lên Git
Ví dụ: .env, __pycache__, *.pyc, models weights

.dockerignore

Tương tự .gitignore nhưng cho Docker
Loại bỏ file không cần thiết khi build image

pytest.ini

Cấu hình cho pytest (framework testing)
Định nghĩa test paths, options, markers

mypy.ini

Cấu hình cho mypy (type checker)
Kiểm tra type hints trong code Python


🎯 main.py

Entry point của ứng dụng
Khởi tạo tất cả services, connections
Chạy main event loop

python# Ví dụ cấu trúc
async def main():
    # Kết nối WebSocket
    # Khởi tạo camera, audio services
    # Start AI engines
    # Run forever

⚙️ config/ - Cấu Hình Toàn Hệ Thống
settings.py

Quản lý cấu hình bằng Pydantic (type-safe)
Load từ .env, environment variables

pythonclass Settings(BaseSettings):
    WEBSOCKET_URL: str
    CAMERA_FPS: int = 30
    LLM_MODEL: str = "llama3"
logging.yaml

Cấu hình structured logging
Định nghĩa log levels, formatters, handlers
Output đến console, file, hoặc remote services

models.yaml

Config cho các AI models
Model paths, hyperparameters, thresholds

yamlface_detection:
  model: yolov8n-face
  confidence: 0.5

🧠 src/core/ - Trái Tim AI
vision/ - Xử Lý Hình Ảnh
camera_manager.py

Quản lý lifecycle của camera
Mở/đóng camera, streaming video
Xử lý nhiều camera cùng lúc

face_detector.py

Phát hiện khuôn mặt trong frame
Dùng YOLO hoặc MTCNN
Trả về bounding boxes

face_recognizer.py

Nhận diện người dựa trên khuôn mặt
Dùng FaceNet embeddings
So sánh với database embeddings đã lưu

motion_detector.py

Phát hiện chuyển động trong video
Dùng background subtraction (OpenCV)
Trigger khi có người di chuyển

object_detector.py

Nhận diện vật thể (ghế, bàn, cốc...)
Dùng YOLO object detection
Real-time detection

pose_estimator.py

Ước lượng tư thế người (skeleton)
Dùng MediaPipe Pose
Nhận diện cử chỉ: vẫy tay, ngồi, đứng...


audio/ - Xử Lý Âm Thanh
audio_capture.py

Capture âm thanh từ microphone
Quản lý audio streams
Xử lý nhiều mic cùng lúc

speech_to_text.py

Chuyển giọng nói thành text
Dùng Whisper (OpenAI) hoặc Vosk
Real-time transcription

text_to_speech.py

Chuyển text thành giọng nói
Dùng Coqui TTS hoặc gTTS
Tạo giọng nói tự nhiên cho robot

voice_recognition.py

Nhận diện người nói (speaker identification)
Dùng voiceprint embeddings
Phân biệt giọng nói khác nhau

sound_classifier.py

Phân loại âm thanh: tiếng chó sủa, chuông cửa, tiếng khóc...
Dùng audio classification models
Event detection

noise_reducer.py

Giảm nhiễu audio
Noise suppression, echo cancellation
Tăng chất lượng audio input


nlp/ - Xử Lý Ngôn Ngữ
llm_manager.py

Interface với Large Language Models
Kết nối Ollama (local) hoặc OpenAI API
Quản lý prompts, contexts

conversation_engine.py

Quản lý hội thoại đa lượt
Lưu lịch sử chat, context
Dialog state tracking

intent_classifier.py

Phân loại ý định người dùng
Ví dụ: hỏi thời tiết, bật đèn, phát nhạc...
Dùng classification models

entity_extractor.py

Trích xuất thực thể từ câu
Ví dụ: "Bật đèn phòng khách" → {action: "turn_on", device: "light", location: "living_room"}
Named Entity Recognition (NER)

sentiment_analyzer.py

Phân tích cảm xúc trong text
Tích cực, tiêu cực, trung tính
Giúp robot phản ứng phù hợp


behavior/ - Hành Vi Robot
behavior_engine.py

State machine điều khiển hành vi
Chuyển đổi giữa các trạng thái: idle, listening, talking, thinking...
Orchestrates toàn bộ hành vi

emotion_model.py

Mô phỏng cảm xúc robot
Vui, buồn, tò mò, ngạc nhiên...
Ảnh hưởng cách robot phản ứng

decision_maker.py

Quyết định hành động tiếp theo
Dựa trên input từ vision, audio, NLP
Logic: "Nếu nhìn thấy người + nghe tiếng 'hello' → Chào lại"

personality.py

Định nghĩa tính cách robot
Nhiệt tình, lịch sự, hài hước...
Customize robot personality


analytics/ - Phân Tích Dữ Liệu
sensor_analyzer.py

Phân tích dữ liệu cảm biến
Nhiệt độ, độ ẩm, ánh sáng...
Tạo insights từ sensor data

anomaly_detector.py

Phát hiện bất thường
Ví dụ: nhiệt độ cao bất thường, chuyển động lạ...
Machine learning based

pattern_recognizer.py

Nhận dạng patterns trong data
Ví dụ: người dùng thường xem TV lúc 8PM
Học thói quen

predictor.py

Dự đoán tương lai
Ví dụ: dự đoán người dùng sắp về nhà
Predictive analytics


🔌 src/services/ - Dịch Vụ Hạ Tầng
websocket/ - WebSocket Communication
client.py

WebSocket client kết nối đến server
Gửi/nhận messages
Connection lifecycle management

message_handler.py

Parse và route messages
Phân loại message types
Dispatch đến handlers tương ứng

reconnect_manager.py

Tự động kết nối lại khi mất kết nối
Exponential backoff
Retry logic

protocols.py

Định nghĩa message schemas
Pydantic models cho messages
Validation & serialization


camera_service.py

Orchestrator cho toàn bộ camera pipeline
Kết nối camera → detection → recognition → send results
High-level service

voice_service.py

Orchestrator cho voice pipeline
Audio capture → STT → NLP → TTS → output
Quản lý conversation flow

llm_service.py

Orchestrator cho LLM processing
Manage prompts, contexts, responses
Rate limiting, caching

notification_service.py

Gửi alerts và notifications
Email, push notifications, webhooks
Event-driven notifications

health_monitor.py

Giám sát sức khỏe hệ thống
CPU, RAM, GPU usage
Service status checks


🤖 src/models/ - Machine Learning Models
base.py

Base class cho tất cả models
Interface chung: load(), predict(), save()
Abstraction layer

face_recognition/

embeddings.pkl: Database vector embeddings của khuôn mặt
metadata.json: Thông tin: tên người, timestamp, model version

voice/

speaker_models.pkl: Voice embeddings
voiceprints.json: Metadata giọng nói

behavior/

state_models.pkl: Pre-trained behavior models


📊 src/data/ - Data Pipelines
buffers/ - Bộ Đệm Dữ Liệu
video_buffer.py

Ring buffer lưu video frames gần nhất
Fixed size, FIFO
Efficient memory usage

audio_buffer.py

Ring buffer cho audio chunks
Realtime audio streaming

sensor_buffer.py

Time-series buffer cho sensor data
Sliding window


processors/ - Xử Lý Dữ Liệu
video_processor.py

Preprocessing video frames
Resize, normalize, augmentation

audio_processor.py

Preprocessing audio
Resampling, filtering, feature extraction

batch_processor.py

Batch processing utilities
Process nhiều items cùng lúc


storage/
cache_manager.py

In-memory cache (Redis hoặc local dict)
Cache embeddings, results
LRU eviction

database.py

Database interface (SQLite, PostgreSQL...)
Lưu lịch sử, logs, user data


🌐 src/api/ - Internal API
routes.py

FastAPI routes cho debugging
REST endpoints: GET /status, POST /process_image
Web UI cho monitoring

schemas.py

Pydantic models cho API requests/responses
Validation & documentation


🛠️ src/utils/ - Tiện Ích
logger.py

Setup structured logging
Custom formatters, handlers
Centralized logging

decorators.py

Performance decorators: @timing, @retry, @cache
Code reusability

validators.py

Input validation functions
Check file types, formats, ranges

converters.py

Format converters: image↔bytes, audio formats...
Data transformation

metrics.py

Performance metrics tracking
FPS, latency, throughput

constants.py

Global constants: MODEL_PATHS, THRESHOLDS, CONFIGS
Single source of truth


🧪 tests/ - Testing
conftest.py

Pytest fixtures (reusable test components)
Setup/teardown logic

unit/

Test từng component riêng lẻ
Mock dependencies
Fast, isolated

integration/

Test nhiều components cùng nhau
End-to-end workflows
Real connections

fixtures/

Sample data cho testing
Videos, audios, configs


🚀 scripts/ - Automation
setup.sh

Script tự động setup môi trường
Install dependencies, download models
One-command setup

train_model.py

Training script cho custom models
Face recognition, voice recognition

benchmark.py

Performance benchmarking
Test speed, accuracy

collect_faces.py

Tool thu thập dữ liệu khuôn mặt
Build face database


🐳 docker/ - Containerization
Dockerfile

Build Docker image (CPU version)
Multi-stage build

Dockerfile.gpu

GPU-enabled version
CUDA support

docker-compose.yml

Orchestrate multiple containers
Services: app, redis, database


📚 docs/ - Documentation

API.md: API documentation
ARCHITECTURE.md: System architecture
MODELS.md: Model documentation
DEPLOYMENT.md: Deployment guide
CONTRIBUTING.md: Contribution guidelines


📓 notebooks/ - Research & Development

Jupyter notebooks cho thử nghiệm
Prototype models
Data analysis
Không dùng trong production


🎯 Workflow Tổng Quan

main.py khởi động → Load config/settings.py
Kết nối WebSocket qua services/websocket/client.py
Camera stream → core/vision/camera_manager.py
Detect faces → core/vision/face_detector.py
Recognize → core/vision/face_recognizer.py (dùng models/face_recognition/)
Audio → core/audio/speech_to_text.py
NLP → core/nlp/llm_manager.py
Decision → core/behavior/decision_maker.py
Response → core/audio/text_to_speech.py
Gửi kết quả qua WebSocket → services/websocket/message_handler.py