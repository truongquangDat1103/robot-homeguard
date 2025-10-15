# quick_test.py
# Test phát hiện khuôn mặt bằng Haar (để chắc webcam + cascade hoạt động)

import cv2, os

CAMERA_INDEX = 0
MIN_FACE = (80, 80)

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
if not cap.isOpened():
    raise SystemExit("Không mở được webcam")

cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(cascade_path)
if face_cascade.empty():
    raise SystemExit("Không load được haarcascade_frontalface_default.xml")

print("Nhấn 'q' để thoát.")
while True:
    ok, frame = cap.read()
    if not ok:
        print("[WARN] Không đọc được frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=MIN_FACE)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Webcam Face Detect (Haar)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
