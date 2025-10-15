// sensors/UltrasonicSensor.h
#pragma once
#include <Arduino.h>

class UltrasonicSensor {
public:
    UltrasonicSensor(int trig, int echo, String name);
    void begin();
    float readDistance();
    void checkObstacle();
    void printDistance();
    String getName() const;

private:
    int trigPin, echoPin;
    String sensorName;
};
