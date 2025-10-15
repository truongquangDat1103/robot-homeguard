# train_lbph.py
# Duyệt dataset/<ten_nguoi> → gán label → train LBPH → lưu model & labels

import cv2, os
import numpy as np

DATASET_DIR = "dataset"
MODEL_PATH  = "lbph_model.xml"
LABELS_PATH = "labels.txt"

if not os.path.isdir(DATASET_DIR):
    raise SystemExit("Chưa có thư mục 'dataset'. Hãy chạy collect_faces.py trước.")

images, labels = [], []
label_names = []  # index -> name

for idx, person in enumerate(sorted(os.listdir(DATASET_DIR))):
    person_dir = os.path.join(DATASET_DIR, person)
    if not os.path.isdir(person_dir):
        continue
    label_names.append(person)

    for fname in os.listdir(person_dir):
        path = os.path.join(person_dir, fname)
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        if img.shape != (200, 200):
            img = cv2.resize(img, (200, 200))
        images.append(img)
        labels.append(idx)

if not images:
    raise SystemExit("Dataset rỗng. Hãy thu thập ảnh trước.")

images = np.array(images, dtype=np.uint8)
labels = np.array(labels, dtype=np.int32)

# Tạo & train LBPH (chỉ dùng cv2)
recognizer = cv2.face.LBPHFaceRecognizer_create(
    radius=2, neighbors=16, grid_x=8, grid_y=8
)
recognizer.train(images, labels)
recognizer.save(MODEL_PATH)

# Lưu ánh xạ label → tên
with open(LABELS_PATH, "w", encoding="utf-8") as f:
    for idx, name in enumerate(label_names):
        f.write(f"{idx},{name}\n")

print(f"[DONE] Model: {MODEL_PATH}")
print(f"[DONE] Labels: {LABELS_PATH}")
print(f"[INFO] Người học: {', '.join(label_names)}")
