import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(BASE_DIR, "dataset")
MODEL_DIR = os.path.join(BASE_DIR, "models")

CAMERA_ID = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

MAX_HANDS = 1

MIN_DETECTION_CONFIDENCE = 0.75
MIN_TRACKING_CONFIDENCE = 0.75

TRAIN_EPOCHS = 500
BATCH_SIZE = 32

CONFIDENCE_THRESHOLD = 0.90

ESP32_IP = "10.75.133.153"

os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)