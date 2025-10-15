import cv2
import mediapipe as mp

class HumanDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.drawer = mp.solutions.drawing_utils

    def run(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.pose.process(rgb)

            if result.pose_landmarks:
                self.drawer.draw_landmarks(frame, result.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            cv2.imshow("MediaPipe Human Detection", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    detector = HumanDetector()
    detector.run()
