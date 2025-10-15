import cv2                                      # import thư viện OpenCV để xử lý ảnh & video

class MotionDetector:                           # Định nghĩa class MotionDetector theo hướng đối tượng
    def __init__(self, min_area: int = 500, camera_index: int = 0):   # Hàm khởi tạo
        self.min_area = min_area                # Ngưỡng diện tích tối thiểu của vùng chuyển động
        self.camera_index = camera_index        # Chỉ số camera (0 = webcam mặc định)
        self.cap = None                         # Đối tượng VideoCapture
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True) 
        # Bộ trừ nền MOG2: tự học nền, phát hiện chuyển động

    def start_camera(self):                     # Hàm khởi động camera
        self.cap = cv2.VideoCapture(self.camera_index)   # Mở camera
        if not self.cap.isOpened():             # Nếu mở camera thất bại
            raise RuntimeError("Không mở được camera")   # Báo lỗi

    def detect_motion(self):                    # Hàm phát hiện chuyển động
        ret, frame = self.cap.read()            # Đọc khung hình mới từ camera
        if not ret:                             # Nếu không đọc được khung hình
            return None, []                     # Trả về None và danh sách rỗng

        # Áp dụng background subtraction để lấy vùng foreground (chuyển động)
        fgmask = self.fgbg.apply(frame)         

        # Xử lý mask để loại bỏ nhiễu
        blur = cv2.GaussianBlur(fgmask, (5, 5), 0)        # Làm mờ Gaussian
        _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)   # Ngưỡng nhị phân
        dilated = cv2.dilate(thresh, None, iterations=3)  # Dãn ảnh để làm rõ vùng trắng

        # Tìm contours trong mask
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        motion_boxes = []                      # Danh sách lưu bounding boxes
        for contour in contours:               # Duyệt qua các contour
            if cv2.contourArea(contour) < self.min_area:   # Bỏ qua vùng nhỏ (nhiễu)
                continue
            (x, y, w, h) = cv2.boundingRect(contour)       # Tính bounding box
            motion_boxes.append((x, y, w, h))              # Lưu vào danh sách
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)   # Vẽ hình chữ nhật xanh

        if motion_boxes:                       # Nếu phát hiện có chuyển động
            cv2.putText(frame, "Chuyen dong", (10, 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)   # In chữ báo động

        return frame, motion_boxes             # Trả về frame đã vẽ và danh sách box

    def run(self):                             # Hàm chạy vòng lặp chính
        self.start_camera()                    # Mở camera
        while True:                            # Vòng lặp vô hạn
            frame, motion = self.detect_motion()           # Phát hiện chuyển động
            if frame is None:                  # Nếu không đọc được frame
                break                          # Thoát vòng lặp

            cv2.imshow("Phat hien chuyen dong", frame)     # Hiển thị kết quả

            if cv2.waitKey(10) & 0xFF == ord('q'):         # Nhấn phím 'q' để thoát
                break
        self.release()                         # Giải phóng tài nguyên

    def release(self):                         # Hàm giải phóng camera & cửa sổ
        if self.cap:                           # Nếu camera đã mở
            self.cap.release()                 # Giải phóng camera
        cv2.destroyAllWindows()                # Đóng cửa sổ OpenCV


