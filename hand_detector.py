import cv2
import mediapipe as mp
import math


class HandDetector:

    def __init__(
        self,
        max_hands=2,
        detection_confidence=0.7,
        tracking_confidence=0.8
    ):

        self.max_hands = max_hands

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )


    # ========================================================
    # DETECT
    # ========================================================

    def detect(self, frame):

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        result = self.hands.process(rgb)

        # Không phát hiện tay
        if not result.multi_hand_landmarks:
            return None

        # Loại duplicate
        valid_hands = self.remove_duplicate_hands(
            result.multi_hand_landmarks
        )

        if not valid_hands:
            return None

        # ====================================================
        # Trả về dictionary để main.py sử dụng
        # ====================================================

        return {
            "landmarks": valid_hands[0].landmark,
            "all_hands": valid_hands
        }


    # ========================================================
    # REMOVE DUPLICATE HANDS
    # ========================================================

    def remove_duplicate_hands(self, hands):

        if len(hands) <= 1:
            return hands

        valid_hands = []

        for hand in hands:

            wrist = hand.landmark[0]

            duplicate = False

            for existing in valid_hands:

                existing_wrist = existing.landmark[0]

                dx = wrist.x - existing_wrist.x
                dy = wrist.y - existing_wrist.y

                distance = math.sqrt(
                    dx * dx +
                    dy * dy
                )

                # Hai wrist quá gần nhau
                if distance < 0.08:

                    duplicate = True

                    break

            if not duplicate:

                valid_hands.append(hand)

        return valid_hands


    # ========================================================
    # DRAW LANDMARKS
    # ========================================================

    def draw_landmarks(self, frame, hand_data):

        if hand_data is None:
            return frame

        hands = hand_data["all_hands"]

        for hand_landmarks in hands:

            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )

        return frame