#include "INMP441.h"

INMP441::INMP441(i2s_port_t port, int bclk, int lrcl, int dout, int rate, int bufSize)
    : i2sPort(port), pinBCLK(bclk), pinLRCL(lrcl), pinDOUT(dout), sampleRate(rate), bufferSize(bufSize) {}

void INMP441::begin() {
    // Cấu hình I2S
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX), // ESP32 làm master, nhận dữ liệu
        .sample_rate = sampleRate,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,        // INMP441 xuất dữ liệu 32-bit
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,         // Chỉ 1 kênh (mono)
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = bufferSize,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = pinBCLK,
        .ws_io_num = pinLRCL,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = pinDOUT
    };

    // Khởi động driver I2S
    i2s_driver_install(i2sPort, &i2s_config, 0, NULL);
    i2s_set_pin(i2sPort, &pin_config);
    i2s_set_clk(i2sPort, sampleRate, I2S_BITS_PER_SAMPLE_32BIT, I2S_CHANNEL_MONO);

    Serial.println("[INMP441] Initialized successfully.");
}

void INMP441::read(int16_t *samples, size_t count) {
    int32_t sample32;
    size_t bytesRead;

    for (size_t i = 0; i < count; i++) {
        i2s_read(i2sPort, &sample32, sizeof(sample32), &bytesRead, portMAX_DELAY);
        samples[i] = (int16_t)(sample32 >> 14); // chuyển 32-bit → 16-bit (giảm độ lớn)
    }
}

int16_t INMP441::readSample() {
    int32_t sample32 = 0;
    size_t bytesRead;
    i2s_read(i2sPort, &sample32, sizeof(sample32), &bytesRead, portMAX_DELAY);
    return (int16_t)(sample32 >> 14);
}

void INMP441::stop() {
    i2s_driver_uninstall(i2sPort);
    Serial.println("[INMP441] I2S stopped and resources freed.");
}
