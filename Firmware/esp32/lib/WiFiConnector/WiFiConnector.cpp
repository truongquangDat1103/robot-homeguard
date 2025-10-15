#include "WiFiConnector.h"

WiFiConnector::WiFiConnector(const char* ssid, const char* password, unsigned long timeout)
    : ssid(ssid), password(password), timeout(timeout), connected(false) {}

void WiFiConnector::connect() {
    Serial.print("🔌 Connecting to WiFi: ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);
    unsigned long startAttemptTime = millis();

    // Đợi kết nối
    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < timeout) {
        Serial.print(".");
        delay(500);
    }

    if (WiFi.status() == WL_CONNECTED) {
        connected = true;
        Serial.println("\n✅ WiFi Connected!");
        printInfo();
    } else {
        connected = false;
        Serial.println("\n❌ Connection Failed!");
    }
}

bool WiFiConnector::isConnected() {
    connected = (WiFi.status() == WL_CONNECTED);
    return connected;
}

void WiFiConnector::printInfo() {
    if (isConnected()) {
        Serial.print("📶 SSID: ");
        Serial.println(WiFi.SSID());
        Serial.print("📡 IP Address: ");
        Serial.println(WiFi.localIP());
        Serial.print("💻 MAC: ");
        Serial.println(WiFi.macAddress());
    } else {
        Serial.println("⚠️ Not connected to any WiFi network!");
    }
}

void WiFiConnector::disconnect() {
    if (isConnected()) {
        WiFi.disconnect(true);
        connected = false;
        Serial.println("🔌 Disconnected from WiFi.");
    }
}
