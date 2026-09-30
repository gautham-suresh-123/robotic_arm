
import json
import time

import cv2
import mediapipe as mp
import numpy as np
import requests
import tensorflow as tf

ESP32_IP = "10.75.133.153"
GESTURE_URL = f"http://{ESP32_IP}/gesture"
MODE_URL = f"http://{ESP32_IP}/mode"

CONFIDENCE_THRESHOLD = 0.55
SEND_INTERVAL = 0.30

print("Loading model...")
model = tf.keras.models.load_model("models/gesture_model.keras")

with open("models/labels.json","r") as f:
    labels = {int(k):v for k,v in json.load(f).items()}

print("Switching ESP32 to gesture mode...")
try:
    r = requests.post(MODE_URL, json={"mode":"gesture"}, timeout=2)
    print("Mode:", r.status_code, r.text)
except Exception as e:
    print("Mode request failed:", e)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)
drawer = mp.solutions.drawing_utils

def normalize(landmarks):
    pts = np.array([[lm.x,lm.y,lm.z] for lm in landmarks], dtype=np.float32)
    pts -= pts[0]
    scale = np.linalg.norm(pts[9])
    if scale < 1e-6:
        scale = 1.0
    pts /= scale
    return pts.flatten()

last_command = ""
last_sent = 0

cap = cv2.VideoCapture(0)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    command = "No Hand"
    confidence = 0.0

    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        drawer.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        features = normalize(hand.landmark)
        pred = model.predict(np.expand_dims(features,0), verbose=0)[0]

        idx = int(np.argmax(pred))
        confidence = float(pred[idx])
        command = labels[idx]

        if confidence >= CONFIDENCE_THRESHOLD:
            now = time.time()
            if command != last_command or now-last_sent > SEND_INTERVAL:
                try:
                    resp = requests.post(
                        GESTURE_URL,
                        json={"command":command},
                        timeout=2
                    )
                    print(f"{command} | {confidence:.2f} | {resp.status_code} | {resp.text}")
                    last_command = command
                    last_sent = now
                except Exception as e:
                    print("ESP32:", e)

    cv2.putText(frame,f"Command: {command}",(10,30),
                cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
    cv2.putText(frame,f"Confidence: {confidence:.2f}",(10,65),
                cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2)

    cv2.imshow("AI Gesture Recognition",frame)

    if (cv2.waitKey(1)&0xFF)==ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
