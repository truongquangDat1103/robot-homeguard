#pragma once

#include <Arduino.h>
#include <DHT.h>

class DHTSensor {
  public:
    // Constructor: truyền chân dữ liệu và loại cảm biến (DHT11, DHT22...)
    DHTSensor(uint8_t pin, uint8_t type, String name );

    // Khởi tạo cảm biến, gọi trong setup()
    void begin();

    // Lấy giá trị nhiệt độ (°C)
    float getTemperature();

    // Lấy giá trị độ ẩm (%)
    float getHumidity();

    // In giá trị nhiệt độ và độ ẩm ra Serial
    void printValues();

    String getName() const;
  private:
    uint8_t _pin;
    uint8_t _type;
    DHT _dht;
    String sensorName;
};

