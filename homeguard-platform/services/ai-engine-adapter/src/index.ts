import 'dotenv/config';
import { WebSocketClient } from './websocket-client';
import {
  parseFaceDetection,
  parseMotionDetection,
  validateFaceDetection,
  validateMotionDetection,
} from './message-parser';

const SERVER_URL = process.env.API_URL || 'http://localhost:4000';
const ENGINE_ID = process.env.ENGINE_ID || 'ai-engine-1';

class AIEngineAdapter {
  private wsClient: WebSocketClient;
  private heartbeatInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.wsClient = new WebSocketClient(SERVER_URL, ENGINE_ID);
  }

  async start() {
    console.log('🤖 Starting AI Engine Adapter...');
    console.log(`Server: ${SERVER_URL}`);
    console.log(`Engine ID: ${ENGINE_ID}`);

    // Connect to WebSocket server
    this.wsClient.connect();

    // Start heartbeat
    this.startHeartbeat();

    // Simulate AI processing (for testing)
    if (process.env.MOCK_MODE === 'true') {
      this.startMockAIProcessing();
    }

    // Graceful shutdown
    process.on('SIGINT', () => this.shutdown());
    process.on('SIGTERM', () => this.shutdown());
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.wsClient.isConnected()) {
        this.wsClient.sendHeartbeat();
      }
    }, 30000); // Every 30 seconds
  }

  private startMockAIProcessing() {
    console.log('🎭 Mock mode enabled - generating test data');

    // Mock face detection every 10 seconds
    setInterval(() => {
      if (!this.wsClient.isConnected()) return;

      const mockFaceData = {
        detections: [
          {
            id: 'person-1',
            label: Math.random() > 0.5 ? 'John Doe' : 'unknown',
            confidence: 0.85 + Math.random() * 0.15,
            bbox: [100, 100, 200, 200],
          },
        ],
        timestamp: Date.now(),
      };

      const parsed = parseFaceDetection(mockFaceData);
      if (validateFaceDetection(parsed)) {
        this.wsClient.sendFaceDetection(parsed);
      }
    }, 10000);

    // Mock motion detection every 5 seconds
    setInterval(() => {
      if (!this.wsClient.isConnected()) return;

      const mockMotionData = {
        motion_detected: Math.random() > 0.7,
        confidence: 0.8 + Math.random() * 0.2,
        regions: [
          {
            x: Math.floor(Math.random() * 500),
            y: Math.floor(Math.random() * 500),
            width: 100,
            height: 100,
          },
        ],
        timestamp: Date.now(),
      };

      const parsed = parseMotionDetection(mockMotionData);
      if (validateMotionDetection(parsed)) {
        this.wsClient.sendMotionDetection(parsed);
      }
    }, 5000);
  }

  // Process real AI results (integrate with your AI engine)
  processAIResult(type: string, data: any) {
    switch (type) {
      case 'face_detection':
        const faceData = parseFaceDetection(data);
        if (validateFaceDetection(faceData)) {
          this.wsClient.sendFaceDetection(faceData);
        }
        break;

      case 'motion_detection':
        const motionData = parseMotionDetection(data);
        if (validateMotionDetection(motionData)) {
          this.wsClient.sendMotionDetection(motionData);
        }
        break;

      default:
        this.wsClient.sendAIResult({ type, result: data });
    }
  }

  private shutdown() {
    console.log('\n🛑 Shutting down AI Engine Adapter...');

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    this.wsClient.disconnect();
    process.exit(0);
  }
}

// Start the adapter
const adapter = new AIEngineAdapter();
adapter.start().catch((error) => {
  console.error('Failed to start AI Engine Adapter:', error);
  process.exit(1);
});