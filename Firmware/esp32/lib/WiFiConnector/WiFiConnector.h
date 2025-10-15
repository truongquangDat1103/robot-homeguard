#pragma once

#include <WiFi.h>

class WiFiConnector {
private:
    const char* ssid;         // Tên mạng WiFi
    const char* password;     // Mật khẩu WiFi
    unsigned long timeout;    // Thời gian chờ kết nối (ms)
    bool connected;           // Trạng thái kết nối

public:
    // Hàm khởi tạo
    WiFiConnector(const char* ssid, const char* password, unsigned long timeout = 10000);

    // Hàm bắt đầu kết nối
    void connect();

    // Kiểm tra trạng thái
    bool isConnected();

    // In thông tin mạng ra Serial
    void printInfo();

    // Ngắt kết nối
    void disconnect();
};


