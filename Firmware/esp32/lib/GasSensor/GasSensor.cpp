#include "GasSensor.h"

GasSensor::GasSensor(int pin, int thresholdValue, String name)
    : analogPin(pin), threshold(thresholdValue), sensorName(name) {}

void GasSensor::begin() {
    // Nếu cảm biến cần chân output, có thể pinMode
    pinMode(analogPin, INPUT);
}

int GasSensor::readRaw() {
    return analogRead(analogPin);  // đọc giá trị ADC 0-4095 với ESP32
}
void GasSensor::printGas() {
    int value = readRaw();
    Serial.print(sensorName);
    Serial.print(" Raw Value: ");
    Serial.println(value);
    delay(100);
}
bool GasSensor::isGasDetected() {
    int value = readRaw();
    return value >= threshold;     // true nếu vượt ngưỡng
}

String GasSensor::getName() const {
    return sensorName;
}
