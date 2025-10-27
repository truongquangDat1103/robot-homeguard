import { io, Socket } from 'socket.io-client';
import { WebSocketEvent, SensorType } from '@homeguard/types';

// Test WebSocket connections and message routing
describe('WebSocket Integration Tests', () => {
  let esp32Client: Socket;
  let aiEngineClient: Socket;
  let webClient: Socket;

  const SERVER_URL = 'http://localhost:4000';

  beforeAll((done) => {
    // Connect ESP32 client
    esp32Client = io(SERVER_URL, {
      query: { type: 'esp32', deviceId: 'test-device-1' },
    });

    // Connect AI Engine client
    aiEngineClient = io(SERVER_URL, {
      query: { type: 'ai-engine', engineId: 'test-engine-1' },
    });

    // Connect Web client
    webClient = io(SERVER_URL, {
      query: { type: 'web-client', userId: 'test-user-1' },
    });

    let connectedCount = 0;
    const checkAllConnected = () => {
      connectedCount++;
      if (connectedCount === 3) done();
    };

    esp32Client.on('connect', checkAllConnected);
    aiEngineClient.on('connect', checkAllConnected);
    webClient.on('connect', checkAllConnected);
  });

  afterAll(() => {
    esp32Client.disconnect();
    aiEngineClient.disconnect();
    webClient.disconnect();
  });

  test('ESP32 sends sensor data and web client receives it', (done) => {
    const sensorData = {
      id: 'sensor-1',
      type: SensorType.TEMPERATURE,
      value: 25.5,
      unit: '°C',
      timestamp: new Date(),
      deviceId: 'test-device-1',
    };

    // Web client listens for sensor data
    webClient.once(WebSocketEvent.SENSOR_DATA, (data) => {
      expect(data.deviceId).toBe('test-device-1');
      expect(data.data).toBeDefined();
      done();
    });

    // ESP32 sends sensor data
    esp32Client.emit(WebSocketEvent.SENSOR_DATA, sensorData);
  });

  test('AI Engine sends face detection and web client receives it', (done) => {
    const faceData = {
      faces: [
        {
          name: 'Test Person',
          confidence: 0.95,
          bbox: { x: 100, y: 100, width: 200, height: 200 },
        },
      ],
      timestamp: new Date(),
    };

    webClient.once(WebSocketEvent.FACE_DETECTED, (data) => {
      expect(data.engineId).toBe('test-engine-1');
      expect(data.faces).toHaveLength(1);
      done();
    });

    aiEngineClient.emit(WebSocketEvent.FACE_DETECTED, faceData);
  });

  test('Web client sends robot command and ESP32 receives it', (done) => {
    const command = {
      deviceId: 'test-device-1',
      type: 'movement',
      command: 'forward',
      parameters: { speed: 50 },
    };

    esp32Client.once(WebSocketEvent.ROBOT_COMMAND, (data) => {
      expect(data.command).toBe('forward');
      done();
    });

    webClient.emit(WebSocketEvent.ROBOT_COMMAND, command);
  });

  test('Ping/Pong works', (done) => {
    webClient.once('pong', (data) => {
      expect(data.timestamp).toBeDefined();
      done();
    });

    webClient.emit('ping');
  });
});