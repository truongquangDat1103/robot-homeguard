#pragma once
#include <Arduino.h>
#include <driver/i2s.h>

class INMP441 {
private:
    i2s_port_t i2sPort;
    int pinBCLK;
    int pinLRCL;
    int pinDOUT;
    int sampleRate;
    int bufferSize;

public:
    INMP441(i2s_port_t port,int bclk,int lrcl,int dout,int rate,int bufSize);

    void begin();                              // Khởi tạo I2S cho micro
    void read(int16_t *samples, size_t count); // Đọc nhiều mẫu âm thanh (16-bit)
    int16_t readSample();                      // Đọc 1 mẫu duy nhất (16-bit)
    void stop();                               // Dừng và giải phóng I2S
};

