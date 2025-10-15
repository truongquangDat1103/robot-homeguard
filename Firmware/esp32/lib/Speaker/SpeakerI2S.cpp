// #include "SpeakerI2S.h"

// SpeakerI2S::SpeakerI2S(i2s_port_t port) : i2s_num(port) {}

// void SpeakerI2S::begin(int bclk, int lrc, int din) {
//     i2s_config_t config = {
//         .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
//         .sample_rate = 16000,
//         .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
//         .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
//         .communication_format = I2S_COMM_FORMAT_STAND_I2S,
//         .intr_alloc_flags = 0,
//         .dma_buf_count = 4,
//         .dma_buf_len = 1024,
//         .use_apll = false
//     };
//     i2s_pin_config_t pinConfig = {
//         .bck_io_num = bclk,
//         .ws_io_num = lrc,
//         .data_out_num = din,
//         .data_in_num = I2S_PIN_NO_CHANGE
//     };
//     i2s_driver_install(i2s_num, &config, 0, NULL);
//     i2s_set_pin(i2s_num, &pinConfig);
// }

// void SpeakerI2S::playBuffer(int16_t *buffer, size_t samples) {
//     size_t bytesWritten;
//     i2s_write(i2s_num, buffer, samples * sizeof(int16_t), &bytesWritten, portMAX_DELAY);
// }
