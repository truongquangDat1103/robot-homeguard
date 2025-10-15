#include "FlameSensor.h"

FlameSensor::FlameSensor(uint8_t sensorPin, unsigned long debounce, const char* name)
: pin(sensorPin), mode(DIGITAL), threshold(0), flameState(false),
  lastTriggerTime(0), debounceTime( ), sensorName(name)
{
}

FlameSensor::FlameSensor(uint8_t sensorPin, int analogThreshold, unsigned long debounce, const char* name)
: pin(sensorPin), mode(ANALOG_MODE), threshold(analogThreshold), flameState(false),
  lastTriggerTime(0), debounceTime(debounce), sensorName(name)
{
}

void FlameSensor::begin() {
    if (mode == DIGITAL) {
        pinMode(pin, INPUT);
    } else { // ANALOG_MODE: no pinMode required for analog input, but if it's an analog pin used as digital ensure nothing else
        // nothing to do; analogRead works without pinMode
    }
}

bool FlameSensor::readSensor() const {
    if (mode == DIGITAL) {
        int v = digitalRead(pin);
        // Một số module flame dùng LOW = phát hiện, một số dùng HIGH = phát hiện.
        // Mặc định ở đây ta coi HIGH = phát hiện. Nếu bạn dùng module khác, hãy đảo logic ở code gọi hoặc thay đổi ở đây.
        return (v == LOW) ? true : false;
    } else { // ANALOG_MODE
        int val = analogRead(pin);
        return (val >= threshold);
    }
}

bool FlameSensor::isFlameDetected() {
    bool current = readSensor();

    // Nếu vừa chuyển từ không có -> có thì kiểm tra debounce
    if (current && !flameState) {
        unsigned long now = millis();
        if (now - lastTriggerTime >= debounceTime) {
            flameState = true;
            lastTriggerTime = now;
            return true;
        }
    } else if (!current) {
        // Nếu hiện tại không có lửa thì đặt lại trạng thái
        flameState = false;
    }

    return false;
}

bool FlameSensor::getState() const {
    return flameState;
}

unsigned long FlameSensor::getLastTriggerTime() const {
    return lastTriggerTime;
}

void FlameSensor::setAnalogThreshold(int t) {
    threshold = t;
}

void FlameSensor::printState() {
    // Cập nhật trạng thái mới trước khi in
    bool justDetected = isFlameDetected();

    Serial.print(sensorName);
    Serial.print(" - Flame: ");
    if (justDetected) {
        Serial.print("YES (New event)");
    } else {
        Serial.print(flameState ? "YES" : "NO");
    }

    Serial.print(" | mode=");
    Serial.print(mode == DIGITAL ? "DIGITAL" : "ANALOG");

    if (mode == ANALOG_MODE) {
        Serial.print(" thresh=");
        Serial.print(threshold);
    }

    Serial.print(" | last=");
    Serial.println(lastTriggerTime);
}

void FlameSensor::setMode(Mode m) {
    mode = m;
}
