import asyncio
import cv2
from loguru import logger
from config.settings import CameraSettings
from src.core.vision.camera_manager import CameraManager


async def show_realtime(frame, frame_count):
    """Callback hiển thị video realtime."""
    cv2.imshow("AI Engine Camera", frame)

    # Thoát bằng phím 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        logger.info("Phát hiện phím Q — thoát.")
        raise KeyboardInterrupt


async def main():
    logger.info("🚀 Bắt đầu test CameraManager (Giai đoạn 3)")

    # 1️⃣ Tạo cấu hình camera
    camera_config = CameraSettings(index=0, width=640, height=480, fps=30)

    # 2️⃣ Tạo CameraManager
    camera = CameraManager(config=camera_config)

    # 3️⃣ Đăng ký callback để hiển thị frame
    camera.register_frame_callback(show_realtime)

    # 4️⃣ Bắt đầu camera streaming
    if not await camera.start():
        logger.error("Không thể khởi động camera.")
        return

    try:
        # Chạy cho đến khi nhấn Q hoặc dừng thủ công
        while camera.is_running():
            await asyncio.sleep(0.05)
    except KeyboardInterrupt:
        logger.info("Đang dừng camera...")
    finally:
        await camera.stop()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    asyncio.run(main())
