import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

# Start webcam
cap = cv2.VideoCapture(0)

# Timing variables
last_trigger_time = 0
cooldown_duration = 1.0  # seconds between gestures (change if needed)

# Define landmark indices
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20
THUMB_TIP = 4

def detect_gesture(hand_landmarks):
    """Detects whether the gesture means 'next', 'previous', or 'none'."""
    landmarks = hand_landmarks.landmark

    # Get fingertip coordinates (normalized)
    index_y = landmarks[INDEX_TIP].y
    middle_y = landmarks[MIDDLE_TIP].y
    ring_y = landmarks[RING_TIP].y
    pinky_y = landmarks[PINKY_TIP].y
    thumb_y = landmarks[THUMB_TIP].y

    # Simple gesture detection based on finger openness
    fingers_up = [index_y < landmarks[INDEX_TIP - 2].y,
                  middle_y < landmarks[MIDDLE_TIP - 2].y,
                  ring_y < landmarks[RING_TIP - 2].y,
                  pinky_y < landmarks[PINKY_TIP - 2].y,
                  thumb_y < landmarks[THUMB_TIP - 2].y]

    # Count how many fingers are up
    count = fingers_up.count(True)

    # Define your gestures
    if count == 5:  # Open palm
        return "next"
    elif count == 0:  # Closed fist
        return "previous"
    else:
        return None


prev_gesture = None

print("🖐 Gesture control started — show your hand in front of the camera.")

while True:
    success, frame = cap.read()
    if not success:
        break

    # Flip image for mirror effect
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Detect gesture type
            gesture = detect_gesture(hand_landmarks)

            # Trigger gesture once per cooldown
            if gesture and time.time() - last_trigger_time > cooldown_duration:
                if gesture == "next":
                    pyautogui.hotkey('ctrl', 'tab')
                    print("➡️ Switched to next tab")
                elif gesture == "previous":
                    pyautogui.hotkey('ctrl', 'shift', 'tab')
                    print("⬅️ Switched to previous tab")

                last_trigger_time = time.time()
                prev_gesture = gesture

    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
