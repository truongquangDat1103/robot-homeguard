# collect_faces.py
# Thu thập ảnh khuôn mặt và lưu vào dataset/<TEN_NGUOI> (grayscale 200x200)

import cv2, os, time

# ======= Cấu hình nhanh =======
NAME = "duc"          # ĐẶT TÊN người cần thu thập (không dấu, không khoảng trắng)
TARGET = 120          # Số ảnh cần thu thập
CAMERA_INDEX = 0      # Chỉ số webcam (0 là mặc định)
MIN_FACE = (80, 80)   # Kích thước mặt tối thiểu để lấy mẫu
# ==============================

SAVE_DIR = os.path.join("dataset", NAME)
os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
if not cap.isOpened():
    raise SystemExit("Không mở được webcam")

cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(cascade_path)
if face_cascade.empty():
    raise SystemExit("Không load được haarcascade_frontalface_default.xml")

count = 0
print(f"[INFO] Bắt đầu thu thập cho '{NAME}'. Nhấn 'q' để thoát. Mục tiêu: {TARGET} ảnh.")

while True:
    ok, frame = cap.read()
    if not ok:
        print("[WARN] Không đọc được frame từ webcam.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Tăng/giảm scaleFactor, minNeighbors nếu cần
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=MIN_FACE)
    for (x, y, w, h) in faces:
        roi = gray[y:y+h, x:x+w]
        roi = cv2.resize(roi, (200, 200))

        filename = os.path.join(SAVE_DIR, f"{int(time.time()*1000)}.png")
        cv2.imwrite(filename, roi)
        count += 1

        # Vẽ khung và hiển thị đếm
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f"{NAME} {count}/{TARGET}", (x, max(30, y-10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Collecting Faces - Press 'q' to quit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if count >= TARGET:
        print("[INFO] Đã đủ ảnh.")
        break

cap.release()
cv2.destroyAllWindows()
print(f"[DONE] Đã lưu {count} ảnh vào: {SAVE_DIR}")
