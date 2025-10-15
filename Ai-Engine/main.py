"""
AI-Engine Application Entry Point
Main orchestration and lifecycle management
"""
import asyncio
import signal
import sys
from typing import Optional

from loguru import logger

from config.settings import settings
from src.utils.logger import setup_logger
from src.utils.constants import SystemStatus


class AIEngine:
    """Main AI Engine application."""
    
    def __init__(self):
        """Initialize AI Engine."""
        self.status = SystemStatus.OFFLINE
        self.running = False
        
        # Services (to be initialized)
        self.websocket_client = None
        self.camera_service = None
        self.voice_service = None
        self.llm_service = None
        
        logger.info("AI-Engine initialized")
        logger.info(f"Environment: {settings.env}")
        logger.info(f"Debug mode: {settings.debug}")
    
    async def initialize(self) -> None:
        """Initialize all services and modules."""
        try:
            logger.info("🚀 Starting AI-Engine initialization...")
            
            # TODO: Initialize services here
            # self.websocket_client = WebSocketClient(settings.websocket)
            # self.camera_service = CameraService(settings.camera)
            # self.voice_service = VoiceService(settings.audio)
            # self.llm_service = LLMService(settings.llm)
            
            logger.info("✅ All services initialized successfully")
            self.status = SystemStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            self.status = SystemStatus.UNHEALTHY
            raise
    
    async def start(self) -> None:
        """Start the AI Engine."""
        try:
            await self.initialize()
            self.running = True
            
            logger.info("🤖 AI-Engine is now running...")
            logger.info(f"Robot Name: {settings.behavior.robot_name}")
            logger.info(f"Personality: {settings.behavior.personality}")
            
            # TODO: Start services
            # await asyncio.gather(
            #     self.websocket_client.connect(),
            #     self.camera_service.start(),
            #     self.voice_service.start(),
            #     self.llm_service.start()
            # )
            
            # Keep running until stopped
            await self.run()
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Error during startup: {e}")
            self.status = SystemStatus.UNHEALTHY
        finally:
            await self.shutdown()
    
    async def run(self) -> None:
        """Main event loop."""
        try:
            while self.running:
                # Main processing loop
                await asyncio.sleep(0.1)
                
                # TODO: Add main processing logic
                # - Process incoming WebSocket messages
                # - Handle camera frames
                # - Process audio chunks
                # - Update behavior state
                
        except asyncio.CancelledError:
            logger.info("Main loop cancelled")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all services."""
        logger.info("🛑 Shutting down AI-Engine...")
        self.running = False
        self.status = SystemStatus.OFFLINE
        
        try:
            # TODO: Stop all services
            # if self.camera_service:
            #     await self.camera_service.stop()
            # if self.voice_service:
            #     await self.voice_service.stop()
            # if self.websocket_client:
            #     await self.websocket_client.disconnect()
            
            logger.info("✅ AI-Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def handle_signal(self, sig: int) -> None:
        """Handle system signals."""
        logger.info(f"Received signal {sig}")
        self.running = False


def setup_signal_handlers(engine: AIEngine) -> None:
    """Setup signal handlers for graceful shutdown."""
    loop = asyncio.get_event_loop()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: engine.handle_signal(s)
        )


async def main() -> None:
    """Main entry point."""
    # Setup logging
    setup_logger(level=settings.log_level)
    
    # Print banner
    print_banner()
    
    # Create and start engine
    engine = AIEngine()
    
    # Setup signal handlers for Unix systems
    if sys.platform != "win32":
        setup_signal_handlers(engine)
    
    # Start the engine
    await engine.start()


def print_banner() -> None:
    """Print application banner."""
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
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)