#pragma once
// ======================================================
// 🧭 ESP32 DEVKIT V1 (WROOM-32) PINOUT DEFINITIONS
// ======================================================
//
// Tổng cộng ESP32 có 30–38 chân tùy loại module,
// nhưng không phải chân nào cũng dùng được cho I/O!
// Một số chân có chức năng đặc biệt hoặc bị hạn chế.
//
// ⚠️ Lưu ý:
// - GPIO6–11: dùng cho Flash nội bộ → KHÔNG được sử dụng.
// - GPIO34–39: chỉ INPUT (không xuất tín hiệu OUT được).
// - GPIO0, 2, 15: có vai trò trong quá trình boot, cẩn thận khi dùng.
//
// ======================================================


// ======================================================
// 🧩 CHÂN GPIO CƠ BẢN
// ======================================================
#define GPIO0    0   // Strapping pin (Boot mode), có thể dùng cho button
#define GPIO1    1   // TX0 (UART0)
#define GPIO2    2   // Thường dùng cho LED (có thể ảnh hưởng boot)
#define GPIO3    3   // RX0 (UART0)
#define GPIO4    4
#define GPIO5    5
#define GPIO6    6   // ⚠️ Dùng cho SPI Flash - không dùng!
#define GPIO7    7   // ⚠️ Dùng cho SPI Flash - không dùng!
#define GPIO8    8   // ⚠️ Dùng cho SPI Flash - không dùng!
#define GPIO9    9   // ⚠️ Dùng cho SPI Flash - không dùng!
#define GPIO10   10  // ⚠️ Dùng cho SPI Flash - không dùng!
#define GPIO11   11  // ⚠️ Dùng cho SPI Flash - không dùng!
#define GPIO12   12  // Có thể gây lỗi boot nếu HIGH khi khởi động
#define GPIO13   13
#define GPIO14   14
#define GPIO15   15  // Strapping pin (Boot mode)
#define GPIO16   16
#define GPIO17   17
#define GPIO18   18
#define GPIO19   19
#define GPIO20   20  // Không có trên hầu hết module
#define GPIO21   21  // SDA (I2C)
#define GPIO22   22  // SCL (I2C)
#define GPIO23   23
#define GPIO24   24  // Không có trên module DevKit
#define GPIO25   25
#define GPIO26   26
#define GPIO27   27
#define GPIO28   28  // Không có
#define GPIO29   29  // Không có
#define GPIO30   30  // Không có
#define GPIO31   31  // Không có
#define GPIO32   32  // ADC1_4
#define GPIO33   33  // ADC1_5
#define GPIO34   34  // INPUT only
#define GPIO35   35  // INPUT only
#define GPIO36   36  // INPUT only (VP)
#define GPIO37   37  // INPUT only (VN)
#define GPIO38   38  // INPUT only
#define GPIO39   39  // INPUT only


// ======================================================
// 🧰 CHỨC NĂNG CHUẨN (GỢI Ý SỬ DỤNG)
// ======================================================

// UART
#define TX0_PIN  GPIO1
#define RX0_PIN  GPIO3
#define TX2_PIN  GPIO17
#define RX2_PIN  GPIO16

// I2C
#define SDA_PIN  GPIO21
#define SCL_PIN  GPIO22

// SPI (HSPI / VSPI)
#define SPI_MOSI_PIN  GPIO23
#define SPI_MISO_PIN  GPIO19
#define SPI_SCK_PIN   GPIO18
#define SPI_CS_PIN    GPIO5

// Analog (ADC)
#define ADC1_CH0_PIN  GPIO36
#define ADC1_CH1_PIN  GPIO37
#define ADC1_CH2_PIN  GPIO38
#define ADC1_CH3_PIN  GPIO39
#define ADC1_CH4_PIN  GPIO32
#define ADC1_CH5_PIN  GPIO33
#define ADC1_CH6_PIN  GPIO34
#define ADC1_CH7_PIN  GPIO35

#define ADC2_CH0_PIN  GPIO4
#define ADC2_CH1_PIN  GPIO0
#define ADC2_CH2_PIN  GPIO2
#define ADC2_CH3_PIN  GPIO15
#define ADC2_CH4_PIN  GPIO13
#define ADC2_CH5_PIN  GPIO12
#define ADC2_CH6_PIN  GPIO14
#define ADC2_CH7_PIN  GPIO27
#define ADC2_CH8_PIN  GPIO25
#define ADC2_CH9_PIN  GPIO26

// PWM (LED Control)
#define PWM_DEFAULT_PIN GPIO2

// Default LED (tích hợp sẵn trên board)
#define LED_BUILTIN GPIO2
// ultrasonic sensor pins
#define ULTRASONIC_TRIG_PIN GPIO13
#define ULTRASONIC_ECHO_PIN GPIO14
// gas sensor pin
#define GAS_SENSOR_PIN GPIO34
// DHT sensor pin
#define DHT_PIN GPIO27
// PIR sensor pin
#define PIR_PIN GPIO21
// flame sensor pin
#define FLAME_PIN GPIO32
// Speaker MAX98357A pins
#define SPK_LRC_PIN GPIO25
#define SPK_BCLK_PIN GPIO26
#define SPK_DIN_PIN GPIO22
// INMP441 microphone pins
#define INMP441_BCLK_PIN GPIO18
#define INMP441_LRCL_PIN GPIO19 
#define INMP441_DOUT_PIN GPIO21

// ======================================================
