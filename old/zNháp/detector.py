import cv2

# Mở webcam (0 = webcam mặc định)
cap = cv2.VideoCapture(0)

# Đọc khung hình đầu tiên để làm nền so sánh
ret, frame1 = cap.read()
ret, frame2 = cap.read()

while cap.isOpened():
    # Tính sự khác biệt giữa 2 khung hình
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 500:  # bỏ các vùng quá nhỏ
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame1, "Chuyen dong", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Phat hien chuyen dong", frame1)

    # Cập nhật khung hình
    frame1 = frame2
    ret, frame2 = cap.read()

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
