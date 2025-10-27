"""
AI-Engine Application Entry Point
Main orchestration và lifecycle management
"""
import asyncio
import signal
import sys
from typing import Optional

from loguru import logger

from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.constants import SystemStatus, BehaviorState, Emotion

# Import services
from src.services.websocket import get_websocket_manager
from src.core.vision import CameraManager
from src.core.audio import AudioCapture, SpeechToText, TextToSpeech
from src.core.nlp import LLMManager, ConversationEngine, IntentClassifier
from src.core.behavior import BehaviorEngine, EmotionModel, DecisionMaker, Personality
from src.core.analytics import SensorAnalyzer


class AIEngine:
    """Main AI Engine application."""
    
    def __init__(self):
        """Khởi tạo AI Engine."""
        self.status = SystemStatus.OFFLINE
        self.running = False
        
        # Core services
        self.websocket_manager = None
        self.camera_manager = None
        self.audio_capture = None
        self.stt = None
        self.tts = None
        self.llm_manager = None
        self.conversation_engine = None
        self.intent_classifier = None
        self.behavior_engine = None
        self.emotion_model = None
        self.decision_maker = None
        self.personality = None
        self.sensor_analyzer = None
        
        logger.info("AI-Engine đã khởi tạo")
        logger.info(f"Environment: {settings.env}")
        logger.info(f"Debug mode: {settings.debug}")
    
    async def initialize(self) -> None:
        """Khởi tạo tất cả services và modules."""
        try:
            logger.info("🚀 Đang khởi tạo AI-Engine...")
            
            # 1. WebSocket
            if settings.features.enable_conversation:
                logger.info("Khởi tạo WebSocket Manager...")
                self.websocket_manager = get_websocket_manager()
                await self.websocket_manager.start()
            
            # 2. Vision
            if settings.features.enable_face_recognition:
                logger.info("Khởi tạo Camera Manager...")
                self.camera_manager = CameraManager(settings.camera)
                # Camera sẽ start khi cần
            
            # 3. Audio
            if settings.features.enable_voice_recognition:
                logger.info("Khởi tạo Audio Services...")
                self.audio_capture = AudioCapture(settings.audio)
                self.stt = SpeechToText(
                    model_size=settings.audio.stt_model,
                    language=settings.audio.stt_language
                )
                self.tts = TextToSpeech(
                    language=settings.audio.tts_language
                )
            
            # 4. NLP
            if settings.features.enable_conversation:
                logger.info("Khởi tạo NLP Services...")
                self.llm_manager = LLMManager(settings.llm)
                self.conversation_engine = ConversationEngine(self.llm_manager)
                self.intent_classifier = IntentClassifier()
            
            # 5. Behavior
            if settings.features.enable_behavior_engine:
                logger.info("Khởi tạo Behavior Engine...")
                self.behavior_engine = BehaviorEngine(
                    initial_state=BehaviorState.IDLE,
                    initial_emotion=Emotion.NEUTRAL
                )
                self.emotion_model = EmotionModel()
                self.decision_maker = DecisionMaker()
                self.personality = Personality(preset=settings.behavior.personality)
            
            # 6. Analytics
            if settings.features.enable_analytics:
                logger.info("Khởi tạo Analytics...")
                self.sensor_analyzer = SensorAnalyzer()
            
            logger.info("✅ Tất cả services đã khởi tạo thành công")
            self.status = SystemStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo: {e}")
            self.status = SystemStatus.UNHEALTHY
            raise
    
    async def start(self) -> None:
        """Khởi động AI Engine."""
        try:
            await self.initialize()
            self.running = True
            
            logger.info("🤖 AI-Engine đang chạy...")
            logger.info(f"Robot Name: {settings.behavior.robot_name}")
            logger.info(f"Personality: {settings.behavior.personality}")
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            # Start main loop
            await self.run()
            
        except KeyboardInterrupt:
            logger.info("Nhận tín hiệu dừng")
        except Exception as e:
            logger.error(f"Lỗi khi khởi động: {e}")
            self.status = SystemStatus.UNHEALTHY
        finally:
            await self.shutdown()
    
    async def run(self) -> None:
        """Main event loop."""
        try:
            while self.running:
                # Main processing loop
                await asyncio.sleep(0.1)
                
                # Update emotion model
                if self.emotion_model:
                    self.emotion_model.update()
                
                # Process events
                if self.behavior_engine:
                    self.behavior_engine.process_events()
                
                # Process decision queue
                if self.decision_maker and self.decision_maker.has_pending_actions():
                    action = self.decision_maker.get_next_action()
                    if action:
                        await self._execute_action(action)
                
                # Send status update (every 10s)
                if self.websocket_manager and hasattr(self, '_last_status_time'):
                    import time
                    if time.time() - self._last_status_time > 10:
                        await self._send_status_update()
                        self._last_status_time = time.time()
                else:
                    import time
                    self._last_status_time = time.time()
                
        except asyncio.CancelledError:
            logger.info("Main loop đã bị hủy")
    
    async def _execute_action(self, action) -> None:
        """
        Thực thi action.
        
        Args:
            action: Action object từ DecisionMaker
        """
        from src.core.behavior.decision_maker import ActionType
        
        logger.info(f"Executing action: {action.action_type.value}")
        
        try:
            if action.action_type == ActionType.SPEAK:
                # Text-to-speech
                if self.tts:
                    text = action.parameters.get('text', '')
                    await self.tts.speak_async(text)
            
            elif action.action_type == ActionType.CONTROL_DEVICE:
                # Send command qua WebSocket
                if self.websocket_manager:
                    device = action.parameters.get('device')
                    device_action = action.parameters.get('action')
                    logger.info(f"Controlling device: {device} - {device_action}")
                    # TODO: Send actual command
            
            # Mark as completed
            self.decision_maker.complete_current_action()
            
        except Exception as e:
            logger.error(f"Lỗi thực thi action: {e}")
    
    async def _send_status_update(self) -> None:
        """Gửi status update qua WebSocket."""
        if not self.websocket_manager:
            return
        
        import psutil
        
        await self.websocket_manager.send_status(
            cpu_usage=psutil.cpu_percent(interval=0.1),
            memory_usage=psutil.virtual_memory().percent,
            active_services=self._get_active_services()
        )
    
    def _get_active_services(self) -> list:
        """Lấy danh sách active services."""
        services = []
        if self.websocket_manager and self.websocket_manager.is_connected():
            services.append("websocket")
        if self.camera_manager:
            services.append("camera")
        if self.audio_capture:
            services.append("audio")
        if self.llm_manager:
            services.append("nlp")
        if self.behavior_engine:
            services.append("behavior")
        return services
    
    async def shutdown(self) -> None:
        """Gracefully shutdown tất cả services."""
        logger.info("🛑 Đang shutdown AI-Engine...")
        self.running = False
        self.status = SystemStatus.OFFLINE
        
        try:
            # Stop camera
            if self.camera_manager and self.camera_manager.is_running():
                await self.camera_manager.stop()
                self.camera_manager.release()
            
            # Stop audio
            if self.audio_capture and self.audio_capture.is_recording():
                self.audio_capture.stop_recording()
                self.audio_capture.release()
            
            # Stop WebSocket
            if self.websocket_manager:
                await self.websocket_manager.stop()
            
            logger.info("✅ AI-Engine đã shutdown hoàn tất")
            
        except Exception as e:
            logger.error(f"Lỗi khi shutdown: {e}")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers cho graceful shutdown."""
        def signal_handler(sig, frame):
            logger.info(f"Nhận signal {sig}")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def handle_signal(self, sig: int) -> None:
        """Handle system signals."""
        logger.info(f"Nhận signal {sig}")
        self.running = False


async def main() -> None:
    """Main entry point."""
    # Setup logging
    setup_logger(level=settings.log_level)
    
    # Print banner
    print_banner()
    
    # Create và start engine
    engine = AIEngine()
    
    # Start the engine
    await engine.start()


def print_banner() -> None:
    """In banner khi khởi động."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                     🤖 AI-ENGINE 🤖                       ║
    ║                                                           ║
    ║         Advanced AI System for Intelligent Robots        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"    Version: 0.1.0")
    print(f"    Environment: {settings.env}")
    print(f"    Python: {sys.version.split()[0]}")
    print(f"    Robot: {settings.behavior.robot_name}")
    print()


def run_api_server() -> None:
    """Chạy API server (FastAPI)."""
    if not settings.api.enabled:
        logger.warning("API server bị disabled trong config")
        return
    
    import uvicorn
    from src.api.routes import app
    
    logger.info(f"🌐 Starting API server on {settings.api.host}:{settings.api.port}")
    
    uvicorn.run(
        app,
        host=settings.api.host,
        port=settings.api.port,
        workers=settings.api.workers,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    try:
        # Kiểm tra nếu cần chạy API server
        if len(sys.argv) > 1 and sys.argv[1] == "--api":
            run_api_server()
        else:
            # Chạy main engine
            asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)