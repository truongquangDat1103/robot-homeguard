
#include "WebSocketClient.h"

// Static member initialization
WebSocketClient* WebSocketClient::instance = nullptr;

// ============================================
// STATIC CALLBACK WRAPPER
// ============================================

void WebSocketClient::webSocketEventWrapper(WStype_t type, uint8_t* payload, size_t length) {
  if (instance != nullptr) {
    instance->handleWebSocketEvent(type, payload, length);
  }
}

// ============================================
// CONSTRUCTOR & DESTRUCTOR
// ============================================

WebSocketClient::WebSocketClient(const String& server, uint16_t port, const String& robotId)
    : wsServer(server),
      wsPort(port),
      robotId(robotId),
      connectionId(""),
      isConnected(false),
      lastHeartbeat(0),
      lastReconnectAttempt(0),
      reconnectInterval(5000),
      heartbeatInterval(30000) 
{  
  instance = this;
}

WebSocketClient::~WebSocketClient() {
  disconnect();
  instance = nullptr;
}

// ============================================
// CONNECTION MANAGEMENT
// ============================================

void WebSocketClient::connect() {
  if (isConnected) {
    return;
  }
  
  Serial.println("[WebSocket] Initiating connection...");
  // Setup WebSocket with server
    webSocket.begin(wsServer, wsPort, "/");
    webSocket.onEvent(webSocketEventWrapper);
    webSocket.setReconnectInterval(reconnectInterval);
    
    Serial.println("[WebSocket] Client initialized");
}

void WebSocketClient::disconnect() {
  if (isConnected) {
    webSocket.disconnect();
    isConnected = false;
    connectionId = "";
    Serial.println("[WebSocket] Disconnected");
  }
}

void WebSocketClient::update() {
  webSocket.loop();
  
  unsigned long currentTime = millis();
  
  // Send heartbeat
  if (isConnected && (currentTime - lastHeartbeat) > heartbeatInterval) {
    sendHeartbeat();
    lastHeartbeat = currentTime;
  }
}

bool WebSocketClient::isConnectedToServer() const {
  return isConnected;
}

// ============================================
// CALLBACK SETTERS
// ============================================

void WebSocketClient::setOnConnect(OnConnectCallback callback) {
  onConnect = callback;
}

void WebSocketClient::setOnDisconnect(OnDisconnectCallback callback) {
  onDisconnect = callback;
}

void WebSocketClient::setOnMessage(OnMessageCallback callback) {
  onMessage = callback;
}

void WebSocketClient::setOnError(OnErrorCallback callback) {
  onError = callback;
}

void WebSocketClient::setOnActuatorCommand(OnActuatorCommandCallback callback) {
  onActuatorCommand = callback;
}

// ============================================
// CONFIGURATION SETTERS
// ============================================

void WebSocketClient::setReconnectInterval(uint16_t interval) {
  reconnectInterval = interval;
  webSocket.setReconnectInterval(interval);
}

void WebSocketClient::setHeartbeatInterval(uint16_t interval) {
  heartbeatInterval = interval;
}

// ============================================
// MESSAGE SENDING METHODS
// ============================================

void WebSocketClient::sendMessage(MessageType type, const char* target) {
  if (!isConnected) {
    Serial.println("[WebSocket] Not connected, cannot send message");
    return;
  }
  
  StaticJsonDocument<512> doc;
  doc["id"] = generateUUID();
  doc["type"] = messageTypeToString(type);
  doc["source"] = connectionTypeToString(ConnectionType::ESP32_TYPE);
  doc["robotId"] = robotId;
  doc["timestamp"] = getCurrentTimestamp();
  
  if (target != nullptr) {
    doc["target"] = target;
  }
  
  String output;
  serializeJson(doc, output);
  webSocket.sendTXT(output);
}

void WebSocketClient::sendSensorData(const char* sensorType, float value,
                                     const char* unit, AlertLevel alertLevel) {
  if (!isConnected) {
    Serial.println("[WebSocket] Not connected, cannot send sensor data");
    return;
  }
  
  StaticJsonDocument<512> doc;
  doc["id"] = generateUUID();
  doc["type"] = messageTypeToString(MessageType::SENSOR_DATA);
  doc["source"] = connectionTypeToString(ConnectionType::ESP32_TYPE);
  doc["robotId"] = robotId;
  doc["timestamp"] = getCurrentTimestamp();
  doc["requiresAck"] = true;
  
  JsonObject payload = doc.createNestedObject("payload");
  payload["sensorType"] = sensorType;
  payload["sensorName"] = sensorType;
  payload["value"] = value;
  payload["unit"] = unit;
  payload["alertLevel"] = alertLevelToString(alertLevel);
  payload["location"] = "robot_main";
  
  String output;
  serializeJson(doc, output);
  webSocket.sendTXT(output);
  
  Serial.printf("[WebSocket] Sensor data sent: %s = %.2f %s\n", sensorType, value, unit);
}

void WebSocketClient::sendAcknowledgment(const String& messageId) {
  if (!isConnected) {
    return;
  }
  
  StaticJsonDocument<256> doc;
  doc["id"] = generateUUID();
  doc["type"] = messageTypeToString(MessageType::ACK);
  doc["source"] = connectionTypeToString(ConnectionType::ESP32_TYPE);
  doc["robotId"] = robotId;
  doc["timestamp"] = getCurrentTimestamp();
  doc["payload"]["messageId"] = messageId;
  
  String output;
  serializeJson(doc, output);
  webSocket.sendTXT(output);
}

void WebSocketClient::sendError(const String& errorMessage) {
  if (!isConnected) {
    return;
  }
  
  StaticJsonDocument<256> doc;
  doc["id"] = generateUUID();
  doc["type"] = messageTypeToString(MessageType::ERROR_MSG);
  doc["source"] = connectionTypeToString(ConnectionType::ESP32_TYPE);
  doc["robotId"] = robotId;
  doc["timestamp"] = getCurrentTimestamp();
  doc["payload"]["error"] = errorMessage;
  
  String output;
  serializeJson(doc, output);
  webSocket.sendTXT(output);
}

void WebSocketClient::sendHeartbeat() {
  if (!isConnected) {
    return;
  }
  
  StaticJsonDocument<256> doc;
  doc["id"] = generateUUID();
  doc["type"] = messageTypeToString(MessageType::HEARTBEAT);
  doc["source"] = connectionTypeToString(ConnectionType::ESP32_TYPE);
  doc["robotId"] = robotId;
  doc["timestamp"] = getCurrentTimestamp();
  
  String output;
  serializeJson(doc, output);
  webSocket.sendTXT(output);
}

// ============================================
// HELPER METHODS
// ============================================

String WebSocketClient::messageTypeToString(MessageType type) const {
  switch (type) {
    case MessageType::CONNECTION_INIT:
      return "connection_init";
    case MessageType::SENSOR_DATA:
      return "sensor_data";
    case MessageType::SENSOR_ALERT:
      return "sensor_alert";
    case MessageType::VOICE_COMMAND:
      return "voice_command";
    case MessageType::VOICE_TRANSCRIPTION:
      return "voice_transcription";
    case MessageType::AI_RESPONSE:
      return "ai_response";
    case MessageType::ACTUATOR_COMMAND:
      return "actuator_command";
    case MessageType::BEHAVIOR_UPDATE:
      return "behavior_update";
    case MessageType::EMOTION_UPDATE:
      return "emotion_update";
    case MessageType::HEARTBEAT:
      return "heartbeat";
    case MessageType::STATUS_UPDATE:
      return "status_update";
    case MessageType::ERROR_MSG:
      return "error";
    case MessageType::ACK:
      return "ack";
    default:
      return "unknown";
  }
}

MessageType WebSocketClient::stringToMessageType(const char* typeStr) const {
  if (strcmp(typeStr, "actuator_command") == 0) return MessageType::ACTUATOR_COMMAND;
  if (strcmp(typeStr, "ai_response") == 0) return MessageType::AI_RESPONSE;
  if (strcmp(typeStr, "ack") == 0) return MessageType::ACK;
  return MessageType::HEARTBEAT;
}

String WebSocketClient::connectionTypeToString(ConnectionType type) const {
  switch (type) {
    case ConnectionType::ESP32_TYPE:
      return "esp32";
    case ConnectionType::LAPTOP_AI:
      return ""ai_engine";
    case ConnectionType::WEB_CLIENT:
      return "web_client";
    case ConnectionType::MOBILE:
      return "mobile";
    default:
      return "unknown";
  }
}

String WebSocketClient::alertLevelToString(AlertLevel level) const {
  switch (level) {
    case AlertLevel::NORMAL:
      return "normal";
    case AlertLevel::WARNING:
      return "warning";
    case AlertLevel::DANGER:
      return "danger";
    case AlertLevel::CRITICAL:
      return "critical";
    default:
      return "normal";
  }
}

AlertLevel WebSocketClient::getAlertLevel(const char* sensorType, float value) const {
  if (strcmp(sensorType, "temperature") == 0) {
    if (value > 40) return AlertLevel::CRITICAL;
    if (value > 35) return AlertLevel::DANGER;
    if (value < 15) return AlertLevel::WARNING;
  } else if (strcmp(sensorType, "humidity") == 0) {
    if (value > 85 || value < 20) return AlertLevel::WARNING;
  } else if (strcmp(sensorType, "gas") == 0) {
    if (value > 300) return AlertLevel::CRITICAL;
    if (value > 200) return AlertLevel::DANGER;
    if (value > 100) return AlertLevel::WARNING;
  }
  return AlertLevel::NORMAL;
}

String WebSocketClient::generateUUID() const {
  char uuid[37];
  sprintf(uuid, "%08x-%04x-%04x-%04x-%012x",
    random(0xFFFFFFFF),
    random(0xFFFF),
    (random(0xFFFF) & 0x0FFF) | 0x4000,
    (random(0xFFFF) & 0x3FFF) | 0x8000,
    random(0xFFFFFFFF));
  return String(uuid);
}

unsigned long WebSocketClient::getCurrentTimestamp() const {
  return millis();
}

// ============================================
// MESSAGE HANDLERS
// ============================================

void WebSocketClient::handleConnectionAck(const JsonDocument& doc) {
  if (doc["payload"]["connectionId"]) {
    connectionId = doc["payload"]["connectionId"].as<String>();
    isConnected = true;
    Serial.println("[WebSocket] Connection established with ID: " + connectionId);
    
    if (onConnect) {
      onConnect();
    }
  }
}

void WebSocketClient::handleActuatorCommandMessage(const JsonDocument& doc) {
  Serial.println("[WebSocket] Actuator command received");
  
  if (onActuatorCommand) {
    onActuatorCommand(const_cast<JsonDocument&>(doc));
  }
  
  // Send acknowledgment
  if (doc["id"]) {
    sendAcknowledgment(doc["id"].as<String>());
  }
}

void WebSocketClient::handleAIResponse(const JsonDocument& doc) {
  Serial.println("[WebSocket] AI response received");
  
  if (onMessage) {
    onMessage(const_cast<JsonDocument&>(doc));
  }
}

// ============================================
// WEBSOCKET EVENT HANDLER
// ============================================

void WebSocketClient::handleWebSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED: {
      isConnected = false;
      connectionId = "";
      Serial.println("[WebSocket] Disconnected from server");
      
      if (onDisconnect) {
        onDisconnect();
      }
      break;
    }
    
    case WStype_CONNECTED: {
      Serial.println("[WebSocket] Connected to server");
      
      // Send connection initialization
      StaticJsonDocument<512> doc;
      doc["id"] = generateUUID();
      doc["type"] = messageTypeToString(MessageType::CONNECTION_INIT);
      doc["source"] = connectionTypeToString(ConnectionType::ESP32_TYPE);
      doc["robotId"] = robotId;
      doc["timestamp"] = getCurrentTimestamp();
      
      JsonObject payloadObj = doc.createNestedObject("payload");
      payloadObj["userId"] = nullptr;
      payloadObj["ipAddress"] = "0.0.0.0"; // Can be enhanced with actual IP
      
      String output;
      serializeJson(doc, output);
      webSocket.sendTXT(output);
      
      lastHeartbeat = millis();
      break;
    }
    
    case WStype_TEXT: {
      String message = String((char*)payload).substring(0, length);
      Serial.println("[WebSocket] Message received: " + message);
      
      StaticJsonDocument<1024> doc;
      DeserializationError error = deserializeJson(doc, message);
      
      if (error) {
        Serial.println("[WebSocket] JSON parse failed");
        if (onError) {
          onError("JSON parse error");
        }
        break;
      }
      
      const char* msgType = doc["type"];
      
      // Handle different message types
      if (strcmp(msgType, "ack") == 0) {
        handleConnectionAck(doc);
      } else if (strcmp(msgType, "actuator_command") == 0) {
        handleActuatorCommandMessage(doc);
      } else if (strcmp(msgType, "ai_response") == 0) {
        handleAIResponse(doc);
      } else {
        if (onMessage) {
          onMessage(doc);
        }
      }
      break;
    }
    
    case WStype_ERROR: {
      Serial.println("[WebSocket] Error occurred");
      if (onError) {
        onError("WebSocket error");
      }
      break;
    }
    
    default:
      break;
  }
}

// ============================================
// GETTERS
// ============================================

String WebSocketClient::getConnectionId() const {
  return connectionId;
}

String WebSocketClient::getRobotId() const {
  return robotId;
}