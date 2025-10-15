#pragma once

#include <Arduino.h>
#include "Audio.h"  // Thư viện ESP32 Audio

class MAX98357A {
private:
    int bclkPin, lrcPin, dinPin;
    Audio audio;
    String name;

public:
    MAX98357A(int bclk, int lrc, int din, String spkName);
    void begin();
    void playURL(const char* url);
    void loop();
    void setVolume(int volume);
    void playVolume(int volume, const char* url);
    String getName();
    void displayInfo();
};
