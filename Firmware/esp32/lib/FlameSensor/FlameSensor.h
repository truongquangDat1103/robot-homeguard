#ifndef FLAME_SENSOR_H
#define FLAME_SENSOR_H

#include <Arduino.h>

class FlameSensor {
public:
    // Kiểu sensor: DIGITAL đọc digitalRead, ANALOG đọc analogRead và so sánh threshold
    enum Mode { DIGITAL, ANALOG_MODE };

    // Constructor cho digital: pass pin, mode = DIGITAL (mặc định)
    FlameSensor(uint8_t sensorPin, unsigned long debounce , const char* name );

    // Constructor cho analog: pass pin, mode = ANALOG, và threshold (0-1023)
    FlameSensor(uint8_t sensorPin, int analogThreshold, unsigned long debounce , const char* name );

    // Khởi tạo: gọi trong setup()
    void begin();

    // Kiểm tra có vừa phát hiện lửa mới (có debounce)
    // Trả về true nếu vừa có sự kiện phát hiện lửa (một lần)
    bool isFlameDetected();

    // Trả về trạng thái hiện tại (có lửa hay không)
    bool getState() const;

    // Thời điểm last trigger theo millis()
    unsigned long getLastTriggerTime() const;

    // Thay ngưỡng analog (nếu đang ở chế độ analog)
    void setAnalogThreshold(int threshold);

    // In trạng thái (gọi isFlameDetected() trước khi in để cập nhật)
    void printState();

    // Cấu hình mode thủ công
    void setMode(Mode m);

private:
    uint8_t pin;
    Mode mode;
    int threshold;                 // Dùng khi mode == ANALOG (0..1023)
    bool flameState;               // trạng thái hiện tại
    unsigned long lastTriggerTime; // lần kích hoạt cuối
    unsigned long debounceTime;    // ms
    const char* sensorName;

    // helper: đọc giá trị hiện tại (true = phát hiện lửa)
    bool readSensor() const;
};

#endif // FLAME_SENSOR_H
