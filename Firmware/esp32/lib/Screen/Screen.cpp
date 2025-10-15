#include "Screen.h"
#include "video11.h"
//#include "video10.h"

VideoInfo * const videoList[] = { 
&video11,
//&video10
};
const uint8_t NUM_VIDEOS = sizeof(videoList) / sizeof(videoList[0]);

Screen *globalPlayerInstance = nullptr;

Screen::Screen()
: tft(TFT_eSPI()), videoList(::videoList), numVideos(NUM_VIDEOS) {}

// ✅ Kiểu callback trùng khớp hoàn toàn với TJpg_Decoder
bool Screen::tft_output(int16_t x, int16_t y, uint16_t w, uint16_t h, uint16_t *bitmap) {
    static TFT_eSPI *tftPtr = nullptr;

    if (!tftPtr) {
        extern Screen *globalPlayerInstance;
        if (globalPlayerInstance) {
            tftPtr = &(globalPlayerInstance->tft);
        } else {
            return false;
        }
    }

    if (y >= tftPtr->height()) return false;
    tftPtr->pushImage(x, y, w, h, bitmap);
    return true;
}

void Screen::begin() {
    tft.begin();
    tft.setRotation(4);
    tft.fillScreen(TFT_BLACK);

    extern Screen *globalPlayerInstance;
    globalPlayerInstance = this;

    TJpgDec.setJpgScale(1);
    TJpgDec.setSwapBytes(true);
    TJpgDec.setCallback(tft_output);  // ✅ không còn lỗi
}

void Screen::playVideo(const VideoInfo &video, uint16_t delay_ms, bool loop_forever) {
    do {
        for (uint16_t i = 0; i < video.num_frames; i++) {
            const uint8_t *jpg_data = (const uint8_t *)pgm_read_ptr(&video.frames[i]);
            uint16_t jpg_size = pgm_read_word(&video.frame_sizes[i]);

            if (!TJpgDec.drawJpg(0, 0, jpg_data, jpg_size)) {
                //Serial.printf("❌ Decode failed at frame %u\n", i);
            }
            delay(delay_ms);
        }
    } while (loop_forever);
}

void Screen::playAll() {
    for (uint8_t vi = 0; vi < numVideos; vi++) {
        Serial.printf("▶ Playing video %u / %u\n", vi + 1, numVideos);
        playVideo(*videoList[vi], 30, false);
        delay(500);
    }
    delay(2000);
}
