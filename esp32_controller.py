import requests


class ESP32Controller:

    def __init__(self, ip_address):
        self.ip_address = ip_address.rstrip("/")

        self.connected = False
        self.led_mode = "OFF"

        self.check_connection()

    # =========================================================
    # CHECK CONNECTION
    # =========================================================

    def check_connection(self):

        try:
            response = requests.get(
                f"{self.ip_address}/status",
                timeout=2
            )

            if response.status_code == 200:

                self.connected = True

                status = response.text.strip().upper()

                if status in ["OFF", "ON", "BLINK"]:
                    self.led_mode = status

                print(
                    f"[ESP32] WiFi kết nối: "
                    f"{self.ip_address}"
                )

                print(
                    f"[ESP32] Status: "
                    f"{self.led_mode}"
                )

                return True

        except requests.RequestException as e:

            print("[ESP32] Không kết nối được:")
            print(e)

        self.connected = False

        return False

    # =========================================================
    # SEND COMMAND
    # =========================================================

    def send_command(self, command):

        try:

            response = requests.get(
                f"{self.ip_address}/{command}",
                timeout=2
            )

            if response.status_code == 200:

                self.connected = True

                result = response.text.strip()

                print(f"[ESP32] → {result}")

                return True

        except requests.RequestException as e:

            self.connected = False

            print(f"[ESP32] Lỗi WiFi: {e}")

        return False

    # =========================================================
    # LED ON / OFF
    # =========================================================

    def set_led(self, state):

        if state:

            # Đã ON thì không cần gửi lại
            if self.led_mode == "ON":
                return True

            if self.send_command("on"):

                self.led_mode = "ON"

                return True

        else:

            # Chỉ bỏ qua nếu thực sự đang OFF
            if self.led_mode == "OFF":
                return True

            if self.send_command("off"):

                self.led_mode = "OFF"

                return True

        return False

    # =========================================================
    # BLINK
    # =========================================================

    def blink(self):

        # Đã BLINK thì không gửi lại
        if self.led_mode == "BLINK":
            return True

        if self.send_command("blink"):

            self.led_mode = "BLINK"

            return True

        return False

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):

        # Luôn gửi OFF khi thoát
        self.send_command("off")

        self.led_mode = "OFF"
        self.connected = False

        print("[ESP32] Đã ngắt kết nối.")