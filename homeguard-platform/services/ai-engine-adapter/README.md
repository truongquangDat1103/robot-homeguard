AI Engine Adapter
Adapter service để kết nối AI Engine với HomeGuard backend.

Chức năng
Kết nối WebSocket tới backend API
Gửi kết quả nhận diện khuôn mặt
Gửi kết quả phát hiện chuyển động
Gửi các kết quả AI khác
Heartbeat để duy trì kết nối
Cài đặt
bash
cd services/ai-engine-adapter
pnpm install
cp .env.example .env
Chạy
Development Mode (với mock data)
bash
pnpm dev
Production Mode
bash
pnpm build
pnpm start
Tích hợp với AI Engine thật
Để tích hợp với AI engine thực tế, sửa file src/index.ts:

typescript
// Ví dụ: Nhận kết quả từ AI engine của bạn
yourAIEngine.on('faceDetected', (data) => {
  adapter.processAIResult('face_detection', data);
});

yourAIEngine.on('motionDetected', (data) => {
  adapter.processAIResult('motion_detection', data);
});
Environment Variables
API_URL: URL của backend API (mặc định: http://localhost:4000)
ENGINE_ID: ID duy nhất của AI engine
MOCK_MODE: true để chạy với dữ liệu giả (cho testing)
