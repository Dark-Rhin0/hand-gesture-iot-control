#include <WiFi.h>
#include <WebServer.h>


// =====================================================
// WIFI
// =====================================================

const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";


// =====================================================
// LED
// =====================================================

#define LED_PIN 33


// =====================================================
// SERVER
// =====================================================

WebServer server(80);


// =====================================================
// LED STATE
// =====================================================

bool ledState = false;

bool blinkMode = false;

unsigned long previousMillis = 0;

const unsigned long blinkInterval = 300;


// =====================================================
// LED OFF
// =====================================================

void handleOff()
{
    blinkMode = false;

    ledState = false;

    digitalWrite(
        LED_PIN,
        LOW
    );

    server.send(
        200,
        "text/plain",
        "LED OFF"
    );

    Serial.println("LED OFF");
}


// =====================================================
// LED ON
// =====================================================

void handleOn()
{
    blinkMode = false;

    ledState = true;

    digitalWrite(
        LED_PIN,
        HIGH
    );

    server.send(
        200,
        "text/plain",
        "LED ON"
    );

    Serial.println("LED ON");
}


// =====================================================
// LED BLINK
// =====================================================

void handleBlink()
{
    blinkMode = true;

    server.send(
        200,
        "text/plain",
        "LED BLINK"
    );

    Serial.println("LED BLINK");
}


// =====================================================
// STATUS
// =====================================================

void handleStatus()
{
    String status;

    if (blinkMode)
    {
        status = "BLINK";
    }
    else if (ledState)
    {
        status = "ON";
    }
    else
    {
        status = "OFF";
    }

    server.send(
        200,
        "text/plain",
        status
    );
}


// =====================================================
// SETUP
// =====================================================

void setup()
{
    pinMode(
        LED_PIN,
        OUTPUT
    );

    digitalWrite(
        LED_PIN,
        LOW
    );


    Serial.begin(115200);


    // =================================================
    // CONNECT WIFI
    // =================================================

    WiFi.begin(
        WIFI_SSID,
        WIFI_PASSWORD
    );

    Serial.print("Connecting WiFi");

    while (
        WiFi.status() != WL_CONNECTED
    )
    {
        delay(500);

        Serial.print(".");
    }


    Serial.println();

    Serial.println(
        "WiFi connected!"
    );


    Serial.print(
        "ESP32 IP: "
    );

    Serial.println(
        WiFi.localIP()
    );


    // =================================================
    // HTTP ROUTES
    // =================================================

    server.on(
        "/on",
        handleOn
    );

    server.on(
        "/off",
        handleOff
    );

    server.on(
        "/blink",
        handleBlink
    );

    server.on(
        "/status",
        handleStatus
    );


    server.begin();

    Serial.println(
        "HTTP server started"
    );
}


// =====================================================
// LOOP
// =====================================================

void loop()
{
    server.handleClient();


    // =================================================
    // BLINK
    // =================================================

    if (blinkMode)
    {
        unsigned long currentMillis =
            millis();


        if (
            currentMillis - previousMillis
            >= blinkInterval
        )
        {
            previousMillis =
                currentMillis;


            ledState =
                !ledState;


            digitalWrite(
                LED_PIN,
                ledState
                    ? HIGH
                    : LOW
            );
        }
    }
}