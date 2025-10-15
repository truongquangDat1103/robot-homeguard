#include "UltrasonicSensor.h"

UltrasonicSensor::UltrasonicSensor(int trig, int echo, String name)
: trigPin(trig), echoPin(echo), sensorName(name) {}

void UltrasonicSensor::begin() {
    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);
}

float UltrasonicSensor::readDistance() {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    long duration = pulseIn(echoPin, HIGH);
    return duration * 0.034 / 2.0;
}

void UltrasonicSensor::printDistance() {
    long distance= readDistance();
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    delay(100);
}
void UltrasonicSensor::checkObstacle() {
    // Đọc khoảng cách
}
String UltrasonicSensor::getName() const {
    return sensorName;
}
