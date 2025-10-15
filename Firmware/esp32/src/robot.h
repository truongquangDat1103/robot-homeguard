#pragma once

#include <Arduino.h>
#include "Screen.h"
#include "UltrasonicSensor.h"
#include "GasSensor.h"   
#include "DHTSensor.h"
#include <MotionSensor.h>
#include <FlameSensor.h>
#include "MAX98357A.h"
#include "INMP441.h"
#include "WiFiConnector.h"
#include "WebSocketClient.h"
#include "pins.h"

class Robot {
private:
    Screen screen;          // Quản lý màn hình/video
    WiFiConnector wifi;     // Quản lý kết nối WiFi
    UltrasonicSensor ultrasonicSensor; // Cảm biến siêu âm
    GasSensor gasSensor;         // Cảm biến khí gas MQ-2
    DHTSensor dhtSensor;         // Cảm biến nhiệt độ và độ ẩm DHT11
    MotionSensor motionSensor;   // Cảm biến chuyển động PIR
    FlameSensor flameSensor;     // Cảm biến lửa
    MAX98357A speaker;          // Loa MAX98357A
    INMP441 microphone;         // Micro thu âm
    WebSocketClient wsClient; // Quản lý kết nối WebSocket
    public:
    Robot();                     // Constructor
    void begin();                // Khởi tạo hệ thống
    void run();                  // Chạy robot
    void onWebSocketConnected(); // Xử lý khi kết nối WebSocket thành công
    void handleActuatorCommand(const JsonDocument& doc); // Xử lý lệnh điều
};

