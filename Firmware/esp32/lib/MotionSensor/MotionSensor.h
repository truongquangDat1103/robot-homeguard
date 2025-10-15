#pragma once

#include <Arduino.h>

class MotionSensor {
private:
    uint8_t pin;           // Chân gắn cảm biến
    bool motionState;      // Trạng thái chuyển động hiện tại
    unsigned long lastTriggerTime; // Thời gian phát hiện chuyển động gần nhất
    unsigned long debounceTime;    // Thời gian chống rung (ms)
    String sensorName;     // Tên cảm biến

public:
    // Constructor
    MotionSensor(uint8_t sensorPin, unsigned long debounce, String name);

    // Khởi tạo cảm biến (gọi trong setup)
    void begin();

    // Kiểm tra xem có chuyển động không
    bool isMotionDetected();

    // Lấy trạng thái hiện tại
    bool getState() const;

    // Lấy thời gian lần cuối phát hiện chuyển động
    unsigned long getLastTriggerTime() const;

    // In trạng thái cảm biến ra Serial
    void printState();

    String getName() const;
};

