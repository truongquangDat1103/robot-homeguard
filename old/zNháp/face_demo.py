import cv2
from deepface import DeepFace

# Mở webcam
cap = cv2.VideoCapture(0)

# Tải ảnh mẫu của người muốn nhận diện
target_image = "person.jpg"  # ảnh rõ mặt

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Lưu frame tạm để DeepFace xử lý
    cv2.imwrite("temp.jpg", frame)

    try:
        result = DeepFace.verify(img1_path="temp.jpg", img2_path=target_image, enforce_detection=False)
        if result["verified"]:
            label = "Known"
        else:
            label = "Stranger"
    except:
        label = "No face detected"

    # Vẽ khung + label
    cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("DeepFace Webcam", frame)

    # Nhấn Q để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
