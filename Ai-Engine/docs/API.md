📡 AI-Engine API Documentation
Base URL
http://localhost:8000
Authentication
Hiện tại API không yêu cầu authentication trong development mode. Trong production, sử dụng API Key:

bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/status
🏥 Health & Status
GET /
Root endpoint

Response:

json
{
  "name": "AI-Engine API",
  "version": "0.1.0",
  "status": "running"
}
GET /health
Health check endpoint

Response:

json
{
  "status": "healthy",
  "timestamp": "2025-10-19T10:30:00",
  "version": "0.1.0"
}
GET /status
Detailed system status

Response:

json
{
  "cpu_usage": 45.2,
  "memory_usage": 62.8,
  "active_services": ["websocket", "camera", "audio", "nlp"],
  "uptime": 3600.5
}
💬 NLP Endpoints
POST /nlp/process
Xử lý text input từ user

Request Body:

json
{
  "text": "Bật đèn phòng khách",
  "conversation_id": "user_123",
  "user_name": "John"
}
Response:

json
{
  "response": "Đã bật đèn phòng khách",
  "intent": "command",
  "confidence": 0.92,
  "processing_time": 150.5
}
cURL Example:

bash
curl -X POST http://localhost:8000/nlp/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Xin chào robot", "user_name": "John"}'
📊 Sensor Endpoints
POST /sensors/data
Thêm sensor data mới

Request Body:

json
{
  "sensor_id": "temperature_living_room",
  "value": 25.5,
  "unit": "°C",
  "timestamp": 1697712000.0
}
Response:

json
{
  "success": true,
  "message": "Sensor data đã được lưu"
}
GET /sensors/{sensor_id}/stats
Lấy statistics của sensor

Parameters:

sensor_id (path): ID của sensor
Response:

json
{
  "sensor_id": "temperature_living_room",
  "count": 100,
  "mean": 25.5,
  "std": 2.1,
  "min": 20.0,
  "max": 30.0
}
cURL Example:

bash
curl http://localhost:8000/sensors/temperature_living_room/stats
🤖 Behavior Endpoints
GET /behavior/state
Lấy behavior state hiện tại

Response:

json
{
  "current_state": "idle",
  "current_emotion": "neutral",
  "is_busy": false
}
POST /behavior/emotion
Set emotion cho robot

Query Parameters:

emotion (required): Emotion name
intensity (optional): Cường độ (0.0-1.0), default: 0.5
Response:

json
{
  "success": true,
  "emotion": "happy",
  "intensity": 0.8
}
cURL Example:

bash
curl -X POST "http://localhost:8000/behavior/emotion?emotion=happy&intensity=0.8"
🔌 WebSocket Endpoint
WS /ws
WebSocket endpoint cho real-time communication

Connection:

javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
  
  // Send message
  ws.send(JSON.stringify({
    type: 'text_input',
    data: { text: 'Hello robot' }
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
Message Format:

json
{
  "type": "message_type",
  "timestamp": "2025-10-19T10:30:00",
  "data": { }
}
Message Types:

text_input: Text từ user
speech_transcribed: Kết quả STT
face_detected: Phát hiện khuôn mặt
motion_detected: Phát hiện chuyển động
emotion_changed: Cảm xúc thay đổi
llm_response: Response từ LLM
📈 Metrics Endpoint
GET /metrics
Prometheus-compatible metrics

Response:

# HELP ai_engine_requests_total Total requests
# TYPE ai_engine_requests_total counter
ai_engine_requests_total 1234

# HELP ai_engine_cpu_usage CPU usage percentage
# TYPE ai_engine_cpu_usage gauge
ai_engine_cpu_usage 45.2

# HELP ai_engine_memory_usage Memory usage percentage
# TYPE ai_engine_memory_usage gauge
ai_engine_memory_usage 62.8
📸 Vision Endpoints (Planned)
POST /vision/detect-faces
Phát hiện khuôn mặt trong ảnh

Request Body:

json
{
  "image_base64": "base64_encoded_image",
  "detect_landmarks": true
}
POST /vision/recognize-face
Nhận diện khuôn mặt

Request Body:

json
{
  "image_base64": "base64_encoded_image"
}
🎤 Audio Endpoints (Planned)
POST /audio/speech-to-text
Chuyển giọng nói thành text

Request Body:

json
{
  "audio_base64": "base64_encoded_audio",
  "language": "auto"
}
POST /audio/text-to-speech
Chuyển text thành giọng nói

Request Body:

json
{
  "text": "Xin chào",
  "language": "vi",
  "slow": false
}
❌ Error Responses
Standard Error Format
json
{
  "detail": "Error message description"
}
HTTP Status Codes
200: Success
400: Bad Request (invalid input)
404: Not Found
500: Internal Server Error
503: Service Unavailable
Example Error Response
json
{
  "detail": "Sensor not found"
}
📊 Rate Limiting
Limits:

100 requests/minute per IP (development)
1000 requests/minute per API key (production)
Headers:

X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1697712060
🔧 API Versioning
Current version: v0.1.0

Future versions sẽ được prefix trong URL:

http://localhost:8000/v1/nlp/process
http://localhost:8000/v2/nlp/process
📚 Interactive Documentation
Khi chạy ở development mode, truy cập:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
🐍 Python Client Example
python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Send text to NLP
response = requests.post(
    f"{BASE_URL}/nlp/process",
    json={
        "text": "Bật đèn phòng khách",
        "user_name": "John"
    }
)

result = response.json()
print(f"Response: {result['response']}")
print(f"Intent: {result['intent']}")

# Get sensor stats
response = requests.get(
    f"{BASE_URL}/sensors/temperature_living_room/stats"
)

stats = response.json()
print(f"Temperature mean: {stats['mean']}°C")
📱 JavaScript Client Example
javascript
// Fetch API
async function processText(text) {
  const response = await fetch('http://localhost:8000/nlp/process', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      user_name: 'John'
    })
  });
  
  const result = await response.json();
  console.log('Response:', result.response);
  console.log('Intent:', result.intent);
}

processText('Xin chào robot');
🔒 Security Best Practices
HTTPS: Luôn dùng HTTPS trong production
API Keys: Không hardcode API keys
Input Validation: Validate tất cả inputs
Rate Limiting: Implement rate limiting
CORS: Cấu hình CORS đúng
Logging: Log tất cả requests (không log sensitive data)
