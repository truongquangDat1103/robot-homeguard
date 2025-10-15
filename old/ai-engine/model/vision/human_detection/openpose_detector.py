import cv2

class HumanDetector:
    def __init__(self, protoFile="pose_deploy_linevec.prototxt", weightsFile="pose_iter_440000.caffemodel"):
        self.net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)
        self.nPoints = 18
        self.POSE_PAIRS = [
            [1, 2], [1, 5], [2, 3], [3, 4],
            [5, 6], [6, 7], [1, 8], [8, 9],
            [9, 10], [1, 11], [11, 12], [12, 13],
            [1, 0], [0, 14], [14, 16], [0, 15], [15, 17]
        ]

    def run(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frameWidth, frameHeight = frame.shape[1], frame.shape[0]
            inHeight = 368
            inWidth = int((inHeight / frameHeight) * frameWidth)

            inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                                            (0, 0, 0), swapRB=False, crop=False)
            self.net.setInput(inpBlob)
            output = self.net.forward()

            H, W = output.shape[2], output.shape[3]
            points = []

            for i in range(self.nPoints):
                probMap = output[0, i, :, :]
                _, prob, _, point = cv2.minMaxLoc(probMap)
                x = int((frameWidth * point[0]) / W)
                y = int((frameHeight * point[1]) / H)

                if prob > 0.1:
                    points.append((x, y))
                    cv2.circle(frame, (x, y), 5, (0, 255, 255), -1)
                else:
                    points.append(None)

            for pair in self.POSE_PAIRS:
                partA, partB = pair
                if points[partA] and points[partB]:
                    cv2.line(frame, points[partA], points[partB], (0, 255, 0), 2)

            cv2.imshow("OpenPose Human Detection", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    detector = HumanDetector()
    detector.run()
