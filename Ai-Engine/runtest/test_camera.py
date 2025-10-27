"""Test camera functionality."""
import asyncio
import cv2
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.vision import CameraManager, FaceDetector

from config.settings import settings

async def test_camera():
    print("🎥 Testing Camera...")
    
    # 1. Initialize
    camera = CameraManager(settings.camera)
    detector = FaceDetector(method="haar")
    
    if not camera.initialize():
        print("❌ Cannot initialize camera")
        return
    
    # 2. Start camera
    await camera.start()
    print("✅ Camera started")
    
    # 3. Capture and detect for 10 seconds
    print("📸 Capturing frames for 10 seconds...")
    
    start_time = asyncio.get_event_loop().time()
    frame_count = 0
    face_count = 0
    
    while asyncio.get_event_loop().time() - start_time < 10:
        frame = camera.get_frame()
        
        if frame is not None:
            frame_count += 1
            
            # Detect faces
            faces = detector.detect(frame)
            
            if faces:
                face_count += 1
                print(f"👤 Detected {len(faces)} face(s)")
                
                # Draw faces
                frame_with_faces = detector.draw_faces(frame, faces)
                
                # Show
                cv2.imshow('Camera Test', frame_with_faces)
            else:
                cv2.imshow('Camera Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        await asyncio.sleep(0.1)
    
    print(f"\n📊 Results:")
    print(f"   Frames captured: {frame_count}")
    print(f"   Frames with faces: {face_count}")
    print(f"   FPS: {camera.get_fps():.2f}")
    
    # 4. Cleanup
    await camera.stop()
    camera.release()
    cv2.destroyAllWindows()
    
    print("✅ Camera test completed")

if __name__ == "__main__":
    asyncio.run(test_camera())