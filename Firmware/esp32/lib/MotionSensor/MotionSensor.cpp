#include "MotionSensor.h"

MotionSensor::MotionSensor(uint8_t sensorPin, unsigned long debounce, String name)
: pin(sensorPin), motionState(false), lastTriggerTime(0), debounceTime(debounce), sensorName(name)
{
}

void MotionSensor::begin() {
    pinMode(pin, INPUT);
}

bool MotionSensor::isMotionDetected() {
    bool currentState = digitalRead(pin);

    // Chống rung: chỉ trả về true nếu đủ thời gian debounce
    if (currentState && !motionState) {
        unsigned long now = millis();
        if (now - lastTriggerTime >= debounceTime) {
            motionState = true;
            lastTriggerTime = now;
            return true;
        }
    } else if (!currentState) {
        motionState = false;
    }

    return false;
}

bool MotionSensor::getState() const {
    return motionState;
}

unsigned long MotionSensor::getLastTriggerTime() const {
    return lastTriggerTime;
}

void MotionSensor::printState() {
    bool currentDetected = isMotionDetected();

    Serial.print(sensorName);
    Serial.print(" - Motion Detected: ");
    Serial.println(currentDetected ? "YES" : "NO");
}


String MotionSensor::getName() const {
    return sensorName;
}