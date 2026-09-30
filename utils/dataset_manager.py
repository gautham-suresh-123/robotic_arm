import os
import csv
from config import DATASET_DIR


class DatasetManager:

    def __init__(self):
        os.makedirs(DATASET_DIR, exist_ok=True)

    def sanitize_name(self, name):
        name = name.strip()
        name = name.replace(" ", "_")
        name = name.replace("-", "_")
        return name

    def create_gesture(self, movement_name):

        movement_name = self.sanitize_name(movement_name)

        folder = os.path.join(DATASET_DIR, movement_name)

        os.makedirs(folder, exist_ok=True)

        csv_path = os.path.join(folder, "data.csv")

        if not os.path.exists(csv_path):

            with open(csv_path, "w", newline="") as file:

                writer = csv.writer(file)

                header = []

                for i in range(21):
                    header.append(f"x{i}")
                    header.append(f"y{i}")
                    header.append(f"z{i}")

                writer.writerow(header)

        return folder, csv_path

    def save_sample(self, csv_path, feature_vector):

        with open(csv_path, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow(feature_vector.tolist())

    def sample_count(self, csv_path):

        if not os.path.exists(csv_path):
            return 0

        with open(csv_path, "r") as file:

            rows = list(csv.reader(file))

        return max(0, len(rows) - 1)

    def get_all_gestures(self):

        gestures = []

        for item in os.listdir(DATASET_DIR):

            path = os.path.join(DATASET_DIR, item)

            if os.path.isdir(path):
                gestures.append(item)

        gestures.sort()

        return gestures

    def dataset_summary(self):

        summary = {}

        for gesture in self.get_all_gestures():

            csv_path = os.path.join(
                DATASET_DIR,
                gesture,
                "data.csv"
            )

            summary[gesture] = self.sample_count(csv_path)

        return summary