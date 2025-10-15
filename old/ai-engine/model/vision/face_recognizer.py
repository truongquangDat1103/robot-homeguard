import os                                      #     thư viện xử lý file & thư mục
import cv2                                     #     thư viện OpenCV để xử lý ảnh & video
from deepface import DeepFace                  #     DeepFace: tạo embedding & nhận diện khuôn mặt
import numpy as np                             #     thư viện toán học cho vector, ma trận
import torch                                   #     thư viện PyTorch để kiểm tra GPU


class FaceRecognizer:                          #     định nghĩa class FaceRecognizer theo hướng đối tượng
    def __init__(self, db_path="known_faces", model_name="ArcFace", use_gpu=True):     #     hàm khởi tạo class
        self.db_path = db_path                 #     đường dẫn thư mục chứa ảnh khuôn mặt đã biết
        self.model_name = model_name           #     model dùng để trích xuất đặc trưng (Facenet, VGG-Face,…)
        self.embeddings = []                   #     danh sách chứa embedding (vector đặc trưng) của các khuôn mặt đã biết


        if not os.path.exists(db_path):        #     nếu chưa có thư mục db
            os.makedirs(db_path)               #     tạo thư mục mới
            print(f"⚠️ Thư mục {db_path} chưa có, tạo mới...")     #     in thông báo

        self._load_known_faces()               #     gọi hàm load toàn bộ embedding từ db

        self.face_cascade = cv2.CascadeClassifier(        
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )                                      #     nạp bộ phân loại HaarCascade để phát hiện khuôn mặt

    def _load_known_faces(self):
        """Tạo embedding cho tất cả ảnh trong db"""
        for file in os.listdir(self.db_path):                         #     duyệt qua từng file trong thư mục db
            path = os.path.join(self.db_path, file)                   #     nối đường dẫn thư mục + tên file → path đầy đủ
            if os.path.isfile(path):                                  #     chỉ xử lý nếu path là file (bỏ qua thư mục con)
                try:
                    rep = DeepFace.represent(
                        img_path=path,
                        model_name=self.model_name,
                        enforce_detection=False,
                        detector_backend="opencv",                  #     dùng opencv detector cho nhanh
                        prog_bar=False,
                        backend=self.backend                         #     ép DeepFace dùng GPU nếu có
                    )
                    self.embeddings.append({                
                        "name": os.path.splitext(file)[0],            #     tên file (không đuôi) làm nhãn
                        "embedding": rep[0]["embedding"]              #     vector embedding (128D/512D tuỳ model)
                    })
                except Exception as e:                                #     nếu lỗi
                    print(f"Lỗi khi load {file}: {e}")                #     in ra lỗi

    def _cosine_similarity(self, emb1, emb2):                         #     tính độ tương đồng giữa 2 vector embedding
        emb1, emb2 = np.array(emb1), np.array(emb2)                   #     chuyển list → numpy array
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))     #     công thức tính cosine similarity

    def detect_faces(self, frame):                                    #     phát hiện khuôn mặt trong 1 frame ảnh
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                #     chuyển sang ảnh xám để dễ phát hiện
        faces = self.face_cascade.detectMultiScale(                   #     phát hiện khuôn mặt bằng HaarCascade
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
        )
        return faces                                                  #     trả về danh sách toạ độ (x, y, w, h)

    def recognize_face(self, face_img, threshold=0.7):                #     nhận diện khuôn mặt từ vùng ảnh cắt
        try:
            rep = DeepFace.represent(
                face_img,
                model_name=self.model_name,
                enforce_detection=False,
                detector_backend="opencv",
                prog_bar=False,
                backend=self.backend
            )     #     tạo embedding cho khuôn mặt vừa cắt

            if rep:                                                   #     nếu có embedding
                face_emb = rep[0]["embedding"]                        #     lấy vector embedding
                best_match, best_score = "Unknown", 0                 #     gán mặc định = Unknown

                for item in self.embeddings:                          #     duyệt qua các khuôn mặt trong db
                    score = self._cosine_similarity(face_emb, item["embedding"])     #     tính độ tương đồng
                    if score > best_score:                            #     nếu tốt hơn kết quả trước
                        best_match, best_score = item["name"], score  #     cập nhật tên + độ giống

                if best_score >= threshold:                           #     nếu độ giống lớn hơn ngưỡng
                    return best_match                                 #     nhận diện thành công
                else:
                    return "Unknown"                                  #     không đủ ngưỡng
            else:
                return "No face"                                      #     không phát hiện được khuôn mặt
        except Exception as e:                                        #     nếu lỗi
            return f"Lỗi: {str(e)}"                                   #     trả về lỗi

    def start_camera(self, camera_id=0):                              #     hàm khởi động camera
        cap = cv2.VideoCapture(camera_id)                             #     tạo đối tượng VideoCapture để đọc từ camera có id = camera_id
        if not cap.isOpened():                                        #     kiểm tra nếu camera không mở được
            raise RuntimeError(f"Không thể mở camera {camera_id}")    #     báo lỗi
        print(f"✅ Camera {camera_id} đã sẵn sàng")                   #     in ra thông báo khi mở thành công
        return cap                                                    #     trả về đối tượng camera để sử dụng

    def release_camera(self, cap):                                    #     hàm giải phóng camera
        if cap:                                                       #     nếu cap tồn tại
            cap.release()                                             #     giải phóng camera
        cv2.destroyAllWindows()                                       #     đóng tất cả cửa sổ OpenCV

    def recognize_from_camera(self, camera_id=0, threshold=0.7):      #     nhận diện khuôn mặt trực tiếp từ camera
        cap = self.start_camera(camera_id)                            #     khởi động camera bằng hàm mới

        while True:                                                   #     vòng lặp vô hạn
            ret, frame = cap.read()                                   #     đọc 1 frame từ camera
            if not ret:                                               #     nếu không đọc được
                break                                                 #     thoát vòng lặp

            faces = self.detect_faces(frame)                          #     gọi hàm phát hiện khuôn mặt

            for (x, y, w, h) in faces:                                #     duyệt qua từng khuôn mặt
                face_img = frame[y:y+h, x:x+w]                        #     cắt vùng ảnh khuôn mặt
                name = self.recognize_face(face_img, threshold)       #     gọi hàm nhận diện

                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)     #     vẽ khung chữ nhật quanh mặt
                cv2.putText(frame, name, (x, y - 10),                        #     hiển thị tên trên khung
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            cv2.imshow("Face Recognition", frame)                     #     hiển thị frame ra cửa sổ
            if cv2.waitKey(1) & 0xFF == ord("q"):                     #     nhấn phím q để thoát
                break

        self.release_camera(cap)                                      #     gọi hàm giải phóng camera + đóng cửa sổ