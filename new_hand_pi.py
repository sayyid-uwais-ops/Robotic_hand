import cv2
import mediapipe as mp
import serial
import time

# Connect to Arduino (update COM port if needed)
arduino = serial.Serial('COM5', 9600)
time.sleep(2)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:


    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror image for correct orientation
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Determine hand type
                hand_type = hand_handedness.classification[0].label  # 'Left' or 'Right'
                hand_char = 'R' if hand_type == 'Right' else 'L'

                lm_list = []
                h, w, _ = frame.shape
                for id, lm in enumerate(hand_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((id, cx, cy))

                if lm_list:
                    fingers = []

                    # Thumb (x-axis for mirrored camera)
                    fingers.append(1 if lm_list[4][1] < lm_list[3][1] else 0)

                    # Other fingers (y-axis comparison)
                    tip_ids = [8, 12, 16, 20]
                    joint_ids = [6, 10, 14, 18]
                    for tip_id, joint_id in zip(tip_ids, joint_ids):
                        fingers.append(1 if lm_list[tip_id][2] < lm_list[joint_id][2] else 0)

                    # Send to Arduino with hand type
                    for i, state in enumerate(fingers):
                        command = f"F{i+1}:{'UP' if state else 'DOWN'}:{hand_char}\n"
                        arduino.write(command.encode())
                        time.sleep(0.01)

        cv2.imshow("Hand Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()