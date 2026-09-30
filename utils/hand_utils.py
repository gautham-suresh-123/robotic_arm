import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


class HandTracker:

    def __init__(
        self,
        max_hands=1,
        detection_confidence=0.75,
        tracking_confidence=0.75
    ):

        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

    def process(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb)

        return results

    def draw(self, frame, hand_landmarks):

        mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

    def extract_landmarks(self, hand_landmarks):

        data = []

        for lm in hand_landmarks.landmark:

            data.extend([lm.x, lm.y, lm.z])

        return np.array(data, dtype=np.float32)

    def normalize_landmarks(self, landmarks):

        pts = landmarks.reshape(21, 3)

        wrist = pts[0].copy()

        pts[:, 0] -= wrist[0]
        pts[:, 1] -= wrist[1]
        pts[:, 2] -= wrist[2]

        max_distance = np.max(
            np.linalg.norm(pts[:, :2], axis=1)
        )

        if max_distance > 0:
            pts /= max_distance

        return pts.flatten()

    def get_feature_vector(self, hand_landmarks):

        raw = self.extract_landmarks(hand_landmarks)

        normalized = self.normalize_landmarks(raw)

        return normalized

    def get_hand_center(self, hand_landmarks):

        xs = []
        ys = []

        for lm in hand_landmarks.landmark:

            xs.append(lm.x)
            ys.append(lm.y)

        return (
            np.mean(xs),
            np.mean(ys)
        )

    def get_hand_size(self, hand_landmarks):

        wrist = hand_landmarks.landmark[0]
        middle = hand_landmarks.landmark[12]

        return np.sqrt(
            (middle.x - wrist.x) ** 2 +
            (middle.y - wrist.y) ** 2
        )

    def is_hand_visible(self, hand_landmarks):

        size = self.get_hand_size(hand_landmarks)

        return size > 0.08