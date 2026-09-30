from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np


@dataclass
class RecorderStats:
    accepted: int = 0
    rejected: int = 0
    duplicates: int = 0
    coverage: float = 0.0


class GestureRecorder:

    def __init__(self, dataset_dir: str = "dataset") -> None:

        self.dataset_dir = Path(dataset_dir)
        self.dataset_dir.mkdir(parents=True, exist_ok=True)

        self.stats = RecorderStats()
        self.last_vector: Optional[np.ndarray] = None

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )

        self.drawer = mp.solutions.drawing_utils

    def normalize(self, landmarks):

        pts = np.array(
            [[lm.x, lm.y, lm.z] for lm in landmarks],
            dtype=np.float32,
        )

        pts -= pts[0]

        scale = np.linalg.norm(pts[9]) + 1e-6

        pts /= scale

        return pts.flatten()

    def is_duplicate(self, vector, threshold=0.015):

        if self.last_vector is None:
            self.last_vector = vector
            return False

        distance = np.linalg.norm(vector - self.last_vector)

        if distance < threshold:
            self.stats.duplicates += 1
            return True

        self.last_vector = vector
        return False

    def save(self, gesture: str, vector):

        folder = self.dataset_dir / gesture
        folder.mkdir(parents=True, exist_ok=True)

        csv_path = folder / "data.csv"

        write_header = not csv_path.exists()

        with open(csv_path, "a", newline="") as f:

            writer = csv.writer(f)

            if write_header:
                writer.writerow(
                    [f"f{i}" for i in range(len(vector))]
                )

            writer.writerow(vector.tolist())

        self.stats.accepted += 1

    def start(self):

        commands = [
            "BASE_LEFT",
            "BASE_RIGHT",
            "SHOULDER_UP",
            "SHOULDER_DOWN",
            "ELBOW_UP",
            "ELBOW_DOWN",
            "GRIP_OPEN",
            "GRIP_CLOSE",
            "STOP",
        ]

        print("\n========== ROBOTIC ARM COMMANDS ==========\n")

        for i, command in enumerate(commands, start=1):
            print(f"{i}. {command}")

        while True:

            gesture = input(
                "\nEnter Robotic Arm Command: "
            ).strip().upper()

            if gesture in commands:
                break

            print("Invalid command. Please try again.")

        cap = cv2.VideoCapture(0)

        while True:

            ok, frame = cap.read()

            if not ok:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            result = self.hands.process(rgb)

            if result.multi_hand_landmarks:

                hand = result.multi_hand_landmarks[0]

                self.drawer.draw_landmarks(
                    frame,
                    hand,
                    self.mp_hands.HAND_CONNECTIONS,
                )

                vector = self.normalize(hand.landmark)

                if not self.is_duplicate(vector):
                    self.save(gesture, vector)

            cv2.putText(
                frame,
                f"Command : {gesture}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Saved : {self.stats.accepted}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Duplicates : {self.stats.duplicates}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                "Press Q to Stop Recording",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

            cv2.imshow("Gesture Recorder", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    GestureRecorder().start()