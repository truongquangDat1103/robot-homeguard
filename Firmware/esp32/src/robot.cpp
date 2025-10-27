#include "robot.h"

Robot::Robot()
       :screen(),             // Khởi tạo Player
        wifi("LE HUE", "012345679", 10000), // Thay "Your_SSID" và "Your_PASSWORD" bằng thông tin mạng của bạn
        wsClient("ws://your-server.com", 8080, "robot_001"), // Thay "ws://your-server.com" và 8080 bằng địa chỉ và cổng của server WebSocket
        ultrasonicSensor(ULTRASONIC_TRIG_PIN, ULTRASONIC_ECHO_PIN, "Ultrasonic Sensor"),   // Khởi tạo cảm biến siêu âm
        gasSensor(GAS_SENSOR_PIN,500, "Gas Sensor"),           // Khởi tạo cảm biến khí gas
        dhtSensor(DHT_PIN,DHT11, "DHT Sensor"), // Khởi tạo cảm biến DHT11
        motionSensor(PIR_PIN, 200, "PIR Sensor"), // Khởi tạo cảm biến PIR
        flameSensor(FLAME_PIN, 200, "Flame Sensor"), // Khởi tạo cảm biến lửa
        speaker(SPK_BCLK_PIN, SPK_LRC_PIN, SPK_DIN_PIN, "MAX98357A"), // Khởi tạo loa          
        microphone(I2S_NUM_1, INMP441_BCLK_PIN, INMP441_LRCL_PIN, INMP441_DOUT_PIN, 16000, 512) // Khởi tạo micro thu âm

{
    wsClient.setOnConnect([this]() { this->onWebSocketConnected(); });
    wsClient.setOnActuatorCommand([this](const JsonDocument& doc) { 
      this->handleActuatorCommand(doc); 
    });
}

void Robot::begin() {
    Serial.begin(115200);
    screen.begin();
    wifi.connect(); // Kết nối WiFi
    wsClient.connect();
    ultrasonicSensor.begin();
    gasSensor.begin();
    dhtSensor.begin();
    motionSensor.begin();
    flameSensor.begin();
    speaker.begin();
    microphone.begin();
    Serial.println("Robot initialized.");
    // Serial.println("Playing music...");
    // speaker.playVolume(5, "http://stream.radioparadise.com/rock-128");
}

void Robot::run() {
    //screen.playAll();
    //wsClient.update();
    // ultrasonicSensor.printDistance();
    // gasSensor.printGas();
    // dhtSensor.printValues();
    // motionSensor.printState();
     flameSensor.printState();
    
    //speaker.loop();
    // microphone.record(1); // Ghi âm 5 giây
    // microphone.printBuffer(1000); // In ra 16000 mẫu đầu tiên
    delay(500); // Giãn cách 2 giây
}

void Robot::onWebSocketConnected() {
    Serial.println("WebSocket connected to server.");
    // Gửi dữ liệu cảm biến ban đầu hoặc thực hiện các thao tác khác khi kết nối thành công
}

void Robot::handleActuatorCommand(const JsonDocument& doc) {
    // Serial.println("Received actuator command:");
    // serializeJsonPretty(doc, Serial);

    // if (doc["payload"]["action"] == "play_sound") {
    //     const char* url = doc["payload"]["url"];
    //     int volume = doc["payload"]["volume"] | 5; // Mặc định volume là 5 nếu không có trong payload
    //     speaker.playVolume(volume, url);
    //     Serial.println("Playing sound from URL: " + String(url) + " at volume: " + String(volume));
    // }
}