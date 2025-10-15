#include "DHTSensor.h"

DHTSensor::DHTSensor(uint8_t pin, uint8_t type, String name )
: _pin(pin), _type(type), _dht(pin, type), sensorName(name) {
    // Constructor khởi tạo DHT với pin và loại
}

void DHTSensor::begin() {
    _dht.begin();
}

float DHTSensor::getTemperature() {
    float temp = _dht.readTemperature();
    if (isnan(temp)) {
        Serial.println("Lỗi đọc nhiệt độ!");
        return -999; // giá trị lỗi
    }
    return temp;
}

float DHTSensor::getHumidity() {
    float hum = _dht.readHumidity();
    if (isnan(hum)) {
        Serial.println("Lỗi đọc độ ẩm!");
        return -999; // giá trị lỗi
    }
    return hum;
}

void DHTSensor::printValues() {
    float temp = getTemperature();
    float hum = getHumidity();
    if (temp != -999 && hum != -999) {
        Serial.print("Nhiệt độ: "); Serial.print(temp); Serial.print(" °C, ");
        Serial.print("Độ ẩm: "); Serial.print(hum); Serial.println(" %");
    }
}
String DHTSensor::getName() const {
    return sensorName;
}
