import cv2
import mediapipe as mp
import numpy as np
import serial
import time

# Inisialisasi komunikasi serial dengan Arduino (ubah port untuk Ubuntu)
arduino = serial.Serial('/dev/ttyACM0', 9600)  # Sesuaikan dengan port Arduino di Ubuntu
time.sleep(2)  # Tunggu koneksi serial stabil

# Inisialisasi MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Buka webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Posisi saklar virtual
switch_x, switch_y = 500, 300
switch_radius = 40
led_state = False  # Status LED

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror agar lebih intuitif
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Deteksi tangan
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Dapatkan koordinat ujung jari telunjuk
            index_finger_tip = hand_landmarks.landmark[8]
            x, y = int(index_finger_tip.x * 640), int(index_finger_tip.y * 480)

            # Deteksi jika telunjuk menyentuh saklar
            if np.linalg.norm(np.array([x, y]) - np.array([switch_x, switch_y])) < switch_radius:
                led_state = not led_state  # Toggle LED
                arduino.write(f'LED:{int(led_state)}\n'.encode())
                time.sleep(0.3)  # Hindari deteksi berulang

            # Gambar titik pada ujung jari telunjuk
            cv2.circle(frame, (x, y), 10, (255, 0, 0), -1)

    # Gambar saklar virtual
    switch_color = (0, 255, 0) if led_state else (0, 0, 255)
    cv2.circle(frame, (switch_x, switch_y), switch_radius, switch_color, -1)

    # Tampilkan hasil
    cv2.imshow("Hand Tracking & LED Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan resource
cap.release()
cv2.destroyAllWindows()
arduino.close()
