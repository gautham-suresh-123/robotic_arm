import cv2
import mediapipe as mp
import numpy as np
import requests

ESP32_IP = "10.75.133.153"

URL = f"http://{ESP32_IP}/servo"

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

base = 90
shoulder = 90
arm = 90
gripper = 90


def map_value(x, in_min, in_max, out_min, out_max):
    x = max(in_min, min(x, in_max))
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    h, w, _ = frame.shape

    if result.multi_hand_landmarks:

        hand = result.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )

        lm = hand.landmark

        wrist = lm[0]
        thumb = lm[4]
        index = lm[8]
        middle = lm[12]
        ring = lm[16]
        pinky = lm[20]

        x = wrist.x
        y = wrist.y
        z = wrist.z

        base = map_value(x, 0.2, 0.8, 0, 180)

        shoulder = map_value(y, 0.8, 0.2, 0, 180)

        arm = map_value(z, -0.25, 0.15, 180, 0)

        fingers = 0

        if thumb.x > lm[3].x:
            fingers += 1

        if index.y < lm[6].y:
            fingers += 1

        if middle.y < lm[10].y:
            fingers += 1

        if ring.y < lm[14].y:
            fingers += 1

        if pinky.y < lm[18].y:
            fingers += 1

        if fingers >= 4:
            gripper = 180
        elif fingers <= 1:
            gripper = 20

        data = {
            "base": base,
            "shoulder": shoulder,
            "arm": arm,
            "gripper": gripper
        }

        try:
            requests.post(URL, json=data, timeout=0.05)
        except:
            pass

        cv2.putText(frame, f"Base : {base}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0),2)

        cv2.putText(frame, f"Shoulder : {shoulder}", (20,70),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

        cv2.putText(frame, f"Arm : {arm}", (20,100),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

        cv2.putText(frame, f"Gripper : {gripper}", (20,130),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

    cv2.imshow("Robot Arm Control", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()