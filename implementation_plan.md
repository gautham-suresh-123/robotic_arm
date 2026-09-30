# Implementation Plan - Refactoring AI Gesture Controlled Robotic Arm

This plan outlines the steps required to resolve the critical scientific, logic, and engineering bugs identified in the project.

---

## User Review Required

> [!WARNING]
> Renaming the `Base_Left` directory to `BASE_LEFT` will occur in the dataset folder to maintain consistency with `BASE_RIGHT` and match the command vocabulary used by the ESP32. If you have custom scripts pointing to `Base_Left`, please note they will need to be updated.

---

## Proposed Changes

We will modify several Python files to correct logic, fix the data leakage bug, add asynchronous network calls, and unify configuration.

### 1. Configuration & Unification

#### [MODIFY] [config.py](file:///c:/Users/GAUTHAM%20SURESH/Downloads/arm/arm/config.py)
* Add `ESP32_IP = "10.75.133.153"` to center the network configuration.

---

### 2. Dataset Collection & UI Fixes

#### [MODIFY] [record_gesture.py](file:///c:/Users/GAUTHAM%20SURESH/Downloads/arm/arm/record_gesture.py)
* Fix the mismatched gesture menu printed to the console so that it displays the actual valid command set accepted by the recorder and ESP32.

#### [RENAME] `dataset/Base_Left` $\rightarrow$ `dataset/BASE_LEFT`
* Standardize the folder name to all-uppercase to match the ESP32 command.

---

### 3. Model Training Improvements

#### [MODIFY] [train_model.py](file:///c:/Users/GAUTHAM%20SURESH/Downloads/arm/arm/train_model.py)
* **Fix Data Leakage**: Implement a class-wise chronological (non-shuffled) train/test split. For each gesture, allocate the first 80% of sequential samples to training and the remaining 20% to the test set.
* **Fix Checkpoint Overwrite**: Remove the final `model.save()` call that overwrites the optimal model saved by the checkpoint callback.
* Use `config.py` values where possible.

---

### 4. Inference & Actuation Improvements

#### [MODIFY] [recognize.py](file:///c:/Users/GAUTHAM%20SURESH/Downloads/arm/arm/recognize.py)
* Import `ESP32_IP` from `config.py` instead of hardcoding it.
* **Asynchronous Network Client**: Implement a multi-threaded execution queue for sending HTTP commands to the ESP32. The main OpenCV camera loop will push commands to a background thread queue, preventing frame drops and UI freezes.

#### [MODIFY] [main.py](file:///c:/Users/GAUTHAM%20SURESH/Downloads/arm/arm/main.py)
* Import `ESP32_IP` from `config.py` instead of hardcoding it.

---

### 5. Cleaning Up Dead Code

#### [DELETE] [hand_utils.py](file:///c:/Users/GAUTHAM%20SURESH/Downloads/arm/arm/utils/hand_utils.py)
* Remove the dead utility file to prevent developers from using the incorrect normalization method.

#### [DELETE] [dataset_manager.py](file:///c:/Users/GAUTHAM%20SURESH/Downloads/arm/arm/utils/dataset_manager.py)
* Remove unused manager file to clean up the repository.

---

## Verification Plan

### Automated Tests
- Run `train_model.py` to verify that training completes successfully, outputs chronological accuracy/loss curves, and saves the best model under `models/gesture_model.keras`.
- Run `recognize.py` to ensure it starts up the camera, performs inference, displays the webcam feed without blocking, and sends network requests to the background thread.

### Manual Verification
- Verify that the terminal printed output in `record_gesture.py` correctly prompts for the supported commands (e.g., `BASE_LEFT`, `BASE_RIGHT`, `STOP`).
