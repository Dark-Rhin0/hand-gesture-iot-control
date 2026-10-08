# Hand Gesture ESP32 Control

A real-time hand gesture recognition system that uses a webcam and MediaPipe to detect hand gestures and control an LED connected to an ESP32 over Wi-Fi.

## Overview

This project combines computer vision and IoT to control an external LED using hand gestures.

The computer uses a webcam to detect the user's hand and track its landmarks with MediaPipe Hands. The system analyzes the distance between the thumb and index finger to detect a pinch gesture.

The number of consecutive pinch gestures determines the LED state:

| Gesture | Action |
|---|---|
| 1 pinch | LED OFF |
| 2 pinches | LED ON |
| 3 pinches | LED BLINK |

The command is sent from the computer to the ESP32 through HTTP over a local Wi-Fi network.

## System Architecture

```text
                 USB Webcam
                     |
                     v
              +--------------+
              |    OpenCV    |
              | Camera/Input |
              +------+-------+
                     |
                     v
              +--------------+
              |   MediaPipe  |
              |  Hands Model |
              +------+-------+
                     |
                     v
             21 Hand Landmarks
                     |
                     v
          +---------------------+
          | Gesture Recognition |
          |   Pinch Detection   |
          +----------+----------+
                     |
                     | HTTP / Wi-Fi
                     v
              +--------------+
              |    ESP32     |
              | HTTP Server  |
              +------+-------+
                     |
                   GPIO33
                     |
                     v
                    LED
