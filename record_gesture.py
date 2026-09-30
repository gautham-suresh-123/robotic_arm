from utils.recorder import GestureRecorder


def main():
    print("=" * 50)
    print("AI Gesture Controlled IoT Robotic Arm")
    print("Gesture Dataset Recorder")
    print("=" * 50)

    print("\nSupported Gestures:")
    print("1. FRONT")
    print("2. LEFT")
    print("3. RIGHT")
    print("4. UP")
    print("5. DOWN")
    print("6. NEAR")
    print("7. FAR")

    recorder = GestureRecorder()
    recorder.start()

    print("\nRecording completed successfully.")
    print("Dataset saved inside the dataset folder.")


if __name__ == "__main__":
    main()