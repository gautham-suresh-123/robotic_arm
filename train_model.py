import os
import json
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATASET_DIR = "dataset"
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)

X = []
y = []

print("=" * 60)
print("AI Gesture Controlled Robotic Arm")
print("Training Model")
print("=" * 60)

for gesture in sorted(os.listdir(DATASET_DIR)):

    folder = os.path.join(DATASET_DIR, gesture)

    if not os.path.isdir(folder):
        continue

    csv_file = os.path.join(folder, "data.csv")

    if not os.path.exists(csv_file):
        continue

    try:
        df = pd.read_csv(csv_file)

        if len(df) == 0:
            continue

        X.extend(df.values)
        y.extend([gesture] * len(df))

        print(f"{gesture:<20} {len(df)} Samples")

    except Exception as e:
        print(f"Skipping {gesture}: {e}")

if len(X) == 0:
    print("\nNo dataset found.")
    exit()

X = np.asarray(X, dtype=np.float32)
y = np.asarray(y)

encoder = LabelEncoder()

y_encoded = encoder.fit_transform(y)

labels = {}

for i, label in enumerate(encoder.classes_):
    labels[int(i)] = label

with open(os.path.join(MODEL_DIR, "labels.json"), "w") as f:
    json.dump(labels, f, indent=4)

num_classes = len(labels)

y_encoded = tf.keras.utils.to_categorical(
    y_encoded,
    num_classes=num_classes
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    shuffle=True,
    random_state=42
)

model = tf.keras.Sequential([

    tf.keras.layers.Input(shape=(X.shape[1],)),

    tf.keras.layers.Dense(256, activation="relu"),

    tf.keras.layers.Dropout(0.30),

    tf.keras.layers.Dense(128, activation="relu"),

    tf.keras.layers.Dropout(0.30),

    tf.keras.layers.Dense(64, activation="relu"),

    tf.keras.layers.Dense(num_classes, activation="softmax")

])

model.compile(

    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),

    loss="categorical_crossentropy",

    metrics=["accuracy"]

)

early_stop = tf.keras.callbacks.EarlyStopping(

    monitor="val_loss",

    patience=25,

    restore_best_weights=True

)

checkpoint = tf.keras.callbacks.ModelCheckpoint(

    os.path.join(MODEL_DIR, "gesture_model.keras"),

    monitor="val_accuracy",

    save_best_only=True

)

print("\nTraining Started...\n")

history = model.fit(

    X_train,

    y_train,

    validation_data=(X_test, y_test),

    epochs=500,

    batch_size=32,

    callbacks=[early_stop, checkpoint],

    verbose=1

)

loss, accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=0
)

print("\n" + "=" * 60)
print(f"Validation Accuracy : {accuracy * 100:.2f}%")
print("=" * 60)

model.save(os.path.join(MODEL_DIR, "gesture_model.keras"))

print("\nSaved Model:")
print(os.path.join(MODEL_DIR, "gesture_model.keras"))

print("Saved Labels:")
print(os.path.join(MODEL_DIR, "labels.json"))

plt.figure(figsize=(10,5))

plt.plot(history.history["accuracy"], label="Training Accuracy")
plt.plot(history.history["val_accuracy"], label="Validation Accuracy")

plt.title("Training Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.grid(True)

plt.figure(figsize=(10,5))

plt.plot(history.history["loss"], label="Training Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")

plt.title("Training Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)

plt.show()