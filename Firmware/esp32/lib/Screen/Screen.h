#pragma once

#include <Arduino.h>
#include <TFT_eSPI.h>
#include <TJpg_Decoder.h>

struct VideoInfo {
    const uint8_t * const * frames;
    const uint16_t * frame_sizes;
    uint16_t num_frames;
};

class Screen {
public:
    Screen();
    void begin();
    void playVideo(const VideoInfo &video, uint16_t delay_ms = 40, bool loop_forever = false);
    void playAll();
    
private:
    // ⚙️ callback phải đúng với định nghĩa của TJpg_Decoder
    static bool tft_output(int16_t x, int16_t y, uint16_t w, uint16_t h, uint16_t *bitmap);

private:
    TFT_eSPI tft;
    VideoInfo * const * videoList;
    uint8_t numVideos;
};

extern VideoInfo * const videoList[];
extern const uint8_t NUM_VIDEOS;


