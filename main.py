import cv2
import mediapipe as mp
import numpy as np

# Inisialisasi MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Buka webcam
cap = cv2.VideoCapture(0)
screen_width, screen_height = 640, 480  # Ukuran layar tampilan
cap.set(3, screen_width)
cap.set(4, screen_height)

# Posisi bola virtual
ball_x, ball_y = 320, 240
ball_radius = 30

# Fungsi untuk menghitung jumlah jari yang terbuka
def count_fingers(hand_landmarks):
    fingers = [False] * 5
    tip_ids = [4, 8, 12, 16, 20]  # Landmark ujung jari

    # Ibu jari (khusus arah horizontal)
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x:
        fingers[0] = True

    # Jari lainnya
    for i in range(1, 5):
        if hand_landmarks.landmark[tip_ids[i]].y < hand_landmarks.landmark[tip_ids[i] - 2].y:
            fingers[i] = True

    return fingers.count(True)

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
            index_finger_tip = hand_landmarks.landmark[8]  # Landmark 8 adalah ujung telunjuk
            x, y = int(index_finger_tip.x * screen_width), int(index_finger_tip.y * screen_height)

            # Tampilkan jumlah jari yang terbuka
            finger_count = count_fingers(hand_landmarks)
            cv2.putText(frame, f"Fingers: {finger_count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Cek apakah telunjuk menyentuh bola (deteksi jarak)
            if np.linalg.norm(np.array([x, y]) - np.array([ball_x, ball_y])) < ball_radius:
                ball_x, ball_y = np.random.randint(50, screen_width - 50), np.random.randint(50, screen_height - 50)

            # Gambar titik pada ujung jari telunjuk
            cv2.circle(frame, (x, y), 10, (255, 0, 0), -1)

    # Gambar bola virtual
    cv2.circle(frame, (ball_x, ball_y), ball_radius, (0, 0, 255), -1)

    # Tampilkan hasil
    cv2.imshow("Hand Tracking & Interaction", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan resource
cap.release()
cv2.destroyAllWindows()

