import cv2
import time
import math

from hand_detector import HandDetector
from esp32_controller import ESP32Controller


# ============================================================
# CONFIG
# ============================================================

CAMERA_INDEX = 0

ESP32_IP = "YOUR_ESP32_IP_ADDRESS"  # Thay bằng địa chỉ IP của ESP32


# ============================================================
# PINCH
# ============================================================

# Nhỏ hơn giá trị này = đang chụm
PINCH_ON_THRESHOLD = 0.45

# Lớn hơn giá trị này = đã nhả
PINCH_OFF_THRESHOLD = 0.70


# ============================================================
# MULTI-PINCH
# ============================================================

# Khoảng thời gian tối đa giữa 2 lần chụm
SEQUENCE_TIMEOUT = 0.7


# ============================================================
# BLINK
# ============================================================

BLINK_INTERVAL = 0.3


# ============================================================
# CAMERA
# ============================================================

def open_camera(index=0):

    print(f"[CAMERA] Đang mở camera {index}...")

    backends = [
        cv2.CAP_MSMF,
        cv2.CAP_DSHOW,
        cv2.CAP_ANY
    ]

    for backend in backends:

        cap = cv2.VideoCapture(index, backend)

        if not cap.isOpened():
            cap.release()
            continue

        ret, frame = cap.read()

        if ret and frame is not None:

            cap.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                640
            )

            cap.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                480
            )

            print("[CAMERA] Camera hoạt động.")

            return cap

        cap.release()

    print("[CAMERA] Không thể mở camera.")

    return None


# ============================================================
# PINCH RATIO
# ============================================================

def get_pinch_ratio(landmarks):

    # Thumb tip
    thumb_tip = landmarks[4]

    # Index tip
    index_tip = landmarks[8]

    # Index MCP
    index_mcp = landmarks[5]

    # Pinky MCP
    pinky_mcp = landmarks[17]

    # Khoảng cách ngón cái - ngón trỏ
    tip_distance = math.sqrt(
        (thumb_tip.x - index_tip.x) ** 2 +
        (thumb_tip.y - index_tip.y) ** 2
    )

    # Độ rộng lòng bàn tay
    palm_width = math.sqrt(
        (index_mcp.x - pinky_mcp.x) ** 2 +
        (index_mcp.y - pinky_mcp.y) ** 2
    )

    if palm_width == 0:
        return 999

    return tip_distance / palm_width


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # CAMERA
    # --------------------------------------------------------

    cap = open_camera(CAMERA_INDEX)

    if cap is None:
        return


    # --------------------------------------------------------
    # HAND DETECTOR
    # --------------------------------------------------------

    detector = HandDetector(
        max_hands=1,
        detection_confidence=0.7,
        tracking_confidence=0.8
    )


    # --------------------------------------------------------
    # ESP32
    # --------------------------------------------------------

    esp32 = ESP32Controller(
        ip_address=ESP32_IP
    )


    # ========================================================
    # PINCH STATE
    # ========================================================

    # True = đang chụm
    # False = đang nhả
    pinch_active = False


    # Số lần chụm trong chuỗi hiện tại
    pinch_count = 0


    # Thời điểm lần chụm cuối
    last_pinch_time = 0


    # ========================================================
    # LED STATE
    # ========================================================

    # OFF
    # ON
    # BLINK

    led_mode = "OFF"


    # ========================================================
    # FPS
    # ========================================================

    prev_time = time.time()


    # ========================================================
    # START MESSAGE
    # ========================================================

    print()
    print("====================================")
    print("       HAND PINCH LED CONTROL")
    print("====================================")
    print("1 pinch   -> LED OFF")
    print("2 pinches -> LED ON")
    print("3 pinches -> LED BLINK")
    print("====================================")
    print()


    # ========================================================
    # LOOP
    # ========================================================
    
    cv2.namedWindow(
        "Hand Fire Detection",
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        "Hand Fire Detection",
        1280,
        720
    )

    while True:

        ret, frame = cap.read()

        if not ret:

            print("[CAMERA] Không đọc được frame.")

            break


        # Mirror camera
        frame = cv2.flip(frame, 1)


        # ====================================================
        # DETECT HAND
        # ====================================================

        hand_data = detector.detect(frame)

        pinch_ratio = None


        # ====================================================
        # HAND FOUND
        # ====================================================

        if hand_data:

            landmarks = hand_data["landmarks"]


            # ------------------------------------------------
            # DRAW HAND
            # ------------------------------------------------

            frame = detector.draw_landmarks(
                frame,
                hand_data
            )


            # ------------------------------------------------
            # PINCH RATIO
            # ------------------------------------------------

            pinch_ratio = get_pinch_ratio(
                landmarks
            )


            # =================================================
            # PINCH START
            # =================================================

            if not pinch_active:

                # Người dùng bắt đầu chụm
                if pinch_ratio < PINCH_ON_THRESHOLD:

                    pinch_active = True

                    current_time = time.time()


                    # -----------------------------------------
                    # Kiểm tra khoảng cách giữa các lần chụm
                    # -----------------------------------------

                    if (
                        current_time - last_pinch_time
                        > SEQUENCE_TIMEOUT
                    ):

                        # Chuỗi cũ đã hết
                        pinch_count = 0


                    # -----------------------------------------
                    # Tăng số lần chụm
                    # -----------------------------------------

                    pinch_count += 1

                    last_pinch_time = current_time


                    print(
                        f"[PINCH] Lần chụm #{pinch_count}"
                    )


                    # =========================================
                    # 3 LẦN
                    # =========================================

                    if pinch_count >= 3:

                        led_mode = "BLINK"

                        esp32.blink()

                        print("[LED] BLINK")

                        pinch_count = 0
                        last_pinch_time = 0


            # =================================================
            # PINCH RELEASE
            # =================================================

            else:

                # Người dùng đã nhả tay
                if pinch_ratio > PINCH_OFF_THRESHOLD:

                    pinch_active = False


        # ====================================================
        # CONFIRM 1 / 2 PINCH
        # ====================================================

        if pinch_count > 0:

            current_time = time.time()


            # Đã hết thời gian chờ lần tiếp theo
            if (
                current_time - last_pinch_time
                > SEQUENCE_TIMEOUT
            ):

                # --------------------------------------------
                # 1 LẦN
                # --------------------------------------------

                if pinch_count == 1:

                    led_mode = "OFF"

                    blink_state = False

                    esp32.set_led(False)

                    print("[LED] OFF")


                # --------------------------------------------
                # 2 LẦN
                # --------------------------------------------

                elif pinch_count == 2:

                    led_mode = "ON"

                    blink_state = True

                    esp32.set_led(True)

                    print("[LED] ON")


                # --------------------------------------------
                # RESET
                # --------------------------------------------

                pinch_count = 0

                last_pinch_time = 0


        # ====================================================
        # FPS
        # ====================================================

        current_time = time.time()

        fps = 1 / max(
            current_time - prev_time,
            0.001
        )

        prev_time = current_time


        # ====================================================
        # UI
        # ====================================================

        y = 30


        # ----------------------------------------------------
        # PINCH RATIO
        # ----------------------------------------------------

        if pinch_ratio is not None:

            cv2.putText(
                frame,
                f"Pinch ratio: {pinch_ratio:.2f}",
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

            y += 30


        # ----------------------------------------------------
        # PINCH COUNT
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"Pinch count: {pinch_count}",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 0),
            2
        )

        y += 30


        # ----------------------------------------------------
        # LED MODE
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"LED mode: {led_mode}",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2
        )

        y += 30


        # ----------------------------------------------------
        # ESP32
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"ESP32: "
            f"{'CONNECTED' if esp32.connected else 'DISCONNECTED'}",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (
                (0, 255, 0)
                if esp32.connected
                else (0, 0, 255)
            ),
            2
        )

        y += 30


        # ----------------------------------------------------
        # FPS
        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (10, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (200, 200, 200),
            2
        )


        # ====================================================
        # DISPLAY
        # ====================================================

        cv2.imshow(
            "Hand Fire Detection",
            frame
        )


        # ====================================================
        # KEY
        # ====================================================

        key = cv2.waitKey(1) & 0xFF


        if key == ord("q"):

            break


    # ========================================================
    # CLEANUP
    # ========================================================

    esp32.set_led(False)

    esp32.close()

    cap.release()

    cv2.destroyAllWindows()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()