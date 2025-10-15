# recognize.py (patched)
# Detect face (Haar) + recognize (LBPH). Hiển thị FPS + log chẩn lỗi.

import os, time
import cv2

MODEL_PATH  = "lbph_model.xml"
LABELS_PATH = "labels.txt"
CAMERA_INDEX = 0
BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_MSMF, 0]  # thử lần lượt
WIDTH, HEIGHT = 640, 480
THRESHOLD = 70.0
MIN_FACE = (80, 80)

def load_labels(path):
    if not os.path.exists(path):
        raise SystemExit("❌ Chưa có labels.txt. Hãy chạy train_lbph.py trước.")
    id2name = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            idx, name = line.split(",", 1)
            id2name[int(idx)] = name
    if not id2name:
        raise SystemExit("❌ labels.txt rỗng.")
    return id2name

def load_model(path):
    if not os.path.exists(path):
        raise SystemExit("❌ Chưa có lbph_model.xml. Hãy chạy train_lbph.py trước.")
    rec = cv2.face.LBPHFaceRecognizer_create()
    rec.read(path)
    return rec

def open_cam(idx, backend_list):
    for be in backend_list:
        try:
            cap = cv2.VideoCapture(idx, be) if isinstance(be, int) or be != 0 else cv2.VideoCapture(idx)
            if cap.isOpened():
                # đặt độ phân giải để nhẹ
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
                print(f"✅ Opened camera index {idx} backend={be}")
                return cap
            else:
                cap.release()
        except Exception as e:
            print(f"[WARN] backend {be}: {e}")
    return None

def main():
    print("[INFO] Khởi động nhận diện...")
    id2name = load_labels(LABELS_PATH)
    recognizer = load_model(MODEL_PATH)

    cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        raise SystemExit("❌ Không load được haarcascade_frontalface_default.xml")

    cap = open_cam(CAMERA_INDEX, BACKENDS)
    if cap is None:
        raise SystemExit("❌ Không mở được webcam (thử tắt app khác dùng camera, kiểm tra quyền Camera).")

    print("[INFO] Nhấn 'q' để thoát.")
    frames, t0 = 0, time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            print("[WARN] Không đọc được frame (camera bận? quyền Camera?).")
            # vẫn tạo màn hình trống để bạn thấy cửa sổ
            blank = 255 * (0 * frame if frame is not None else 255)
            cv2.imshow("Face Recognition - LBPH", blank)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=MIN_FACE)

        if len(faces) == 0:
            cv2.putText(frame, "No face", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, (200, 200))
            label_id, conf = recognizer.predict(roi)

            if conf <= THRESHOLD:
                name = id2name.get(label_id, "Unknown")
                text = f"{name} ({conf:.1f})"
                color = (0, 200, 0)
            else:
                text = f"Unknown ({conf:.1f})"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, text, (x, max(30, y-10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        # FPS
        frames += 1
        if frames % 30 == 0:
            t1 = time.time()
            fps = 30.0 / (t1 - t0) if t1 > t0 else 0.0
            t0 = t1
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, HEIGHT - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        cv2.imshow("Face Recognition - LBPH", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
