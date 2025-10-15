#include "MAX98357A.h"

MAX98357A::MAX98357A(int bclk, int lrc, int din, String spkName)
: bclkPin(bclk), lrcPin(lrc), dinPin(din), name(spkName) {}

void MAX98357A::begin() {
    audio.setPinout(bclkPin, lrcPin, dinPin);
    audio.setVolume(15); // mặc định volume
}

void MAX98357A::playURL(const char* url) {
    audio.connecttohost(url);
}

void MAX98357A::loop() {
    audio.loop();
}

void MAX98357A::setVolume(int volume) {
    audio.setVolume(volume);
}

void MAX98357A::playVolume(int volume, const char* url) {
    setVolume(volume);
    playURL(url);
    loop();
}

String MAX98357A::getName() {
    return name;
}

void MAX98357A::displayInfo() {
    Serial.println("MAX98357A Speaker: " + name);
    Serial.printf("BCLK: %d, LRC: %d, DIN: %d\n", bclkPin, lrcPin, dinPin);
}
