#pragma once

#include <Arduino.h>

class GasSensor {
private:
    int analogPin;      // chân analog đọc giá trị
    String sensorName;  // tên cảm biến
    int threshold;      // ngưỡng cảnh báo

public:
    GasSensor(int pin, int thresholdValue, String name);  // constructor

    void begin();              // khởi tạo (nếu cần)
    int readRaw();             // đọc giá trị thô ADC
    void printGas();        // in giá trị ra Serial
    bool isGasDetected();      // kiểm tra vượt ngưỡng
    String getName() const;    // trả về tên cảm biến
};

