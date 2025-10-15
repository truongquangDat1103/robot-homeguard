// ==== Driver chọn cho màn hình ====
// Chỉ bật đúng loại driver bạn dùng
#define ST7789_DRIVER

// ==== Kích thước màn hình ==== 
#define TFT_WIDTH  240
#define TFT_HEIGHT 240

// ==== Gán chân kết nối ==== 
// ESP32 DOIT DevKit V1 + ST7789 SPI
#define TFT_MISO  -1     // ST7789 không cần MISO
#define TFT_MOSI  23     // MOSI
#define TFT_SCLK  18     // SCK
#define TFT_CS    5      // Chip Select (CS)
#define TFT_DC    2      // Data/Command (DC)
#define TFT_RST   4      // Reset (RST)

// ==== Tùy chọn hiệu năng ==== 
#define LOAD_GLCD    // Fonts cơ bản
#define LOAD_FONT2
#define LOAD_FONT4
#define LOAD_FONT6
#define LOAD_FONT7
#define LOAD_FONT8
#define LOAD_GFXFF   // FreeFonts

#define SMOOTH_FONT

// ==== Tăng tốc SPI ==== 
#define SPI_FREQUENCY   40000000   // 40 MHz ổn cho ST7789
#define SPI_READ_FREQUENCY  20000000
#define SPI_TOUCH_FREQUENCY 2500000
