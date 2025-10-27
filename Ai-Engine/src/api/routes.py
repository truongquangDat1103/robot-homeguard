"""
API Routes - FastAPI REST endpoints.
Cung cấp HTTP API để tương tác với AI-Engine.
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import psutil
from loguru import logger

from config.settings import settings
from src.api.schemas import (
    HealthResponse,
    StatusResponse,
    TextInputRequest,
    TextInputResponse,
    SensorDataRequest,
    SensorDataResponse
)


# Khởi tạo FastAPI app
app = FastAPI(
    title="AI-Engine API",
    description="REST API cho AI-Engine Robot System",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# CORS middleware
if settings.security.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ==========================================
# Health & Status Endpoints
# ==========================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "name": "AI-Engine API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Kiểm tra tình trạng hệ thống.
    """
    return HealthResponse(
        status="healthy",
        timestamp=str(logger._core.clock.now()),
        version="0.1.0"
    )


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Lấy trạng thái hệ thống chi tiết.
    """
    # CPU & Memory
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    # TODO: Lấy từ các services thực tế
    active_services = ["websocket", "camera", "audio", "nlp"]
    
    return StatusResponse(
        cpu_usage=cpu_percent,
        memory_usage=memory.percent,
        active_services=active_services,
        uptime=0.0  # TODO: Tính uptime thực tế
    )


# ==========================================
# NLP Endpoints
# ==========================================

@app.post("/nlp/process", response_model=TextInputResponse)
async def process_text(request: TextInputRequest):
    """
    Xử lý text input từ user.
    
    Args:
        request: Text input request
        
    Returns:
        Response từ LLM
    """
    try:
        # TODO: Tích hợp với ConversationEngine
        logger.info(f"Processing text: {request.text}")
        
        # Mock response
        response_text = f"Đã nhận: {request.text}"
        
        return TextInputResponse(
            response=response_text,
            intent="unknown",
            confidence=0.8,
            processing_time=100.0
        )
        
    except Exception as e:
        logger.error(f"Lỗi xử lý text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Sensor Endpoints
# ==========================================

@app.post("/sensors/data", response_model=SensorDataResponse)
async def add_sensor_data(request: SensorDataRequest):
    """
    Thêm sensor data.
    
    Args:
        request: Sensor data request
        
    Returns:
        Confirmation response
    """
    try:
        # TODO: Tích hợp với SensorAnalyzer
        logger.info(f"Received sensor data: {request.sensor_id} = {request.value}")
        
        return SensorDataResponse(
            success=True,
            message="Sensor data đã được lưu"
        )
        
    except Exception as e:
        logger.error(f"Lỗi lưu sensor data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensors/{sensor_id}/stats")
async def get_sensor_stats(sensor_id: str):
    """
    Lấy statistics của sensor.
    
    Args:
        sensor_id: ID của sensor
        
    Returns:
        Statistics dictionary
    """
    try:
        # TODO: Tích hợp với SensorAnalyzer
        return {
            "sensor_id": sensor_id,
            "count": 100,
            "mean": 25.5,
            "std": 2.1,
            "min": 20.0,
            "max": 30.0
        }
        
    except Exception as e:
        logger.error(f"Lỗi lấy sensor stats: {e}")
        raise HTTPException(status_code=404, detail="Sensor not found")


# ==========================================
# Behavior Endpoints
# ==========================================

@app.get("/behavior/state")
async def get_behavior_state():
    """Lấy behavior state hiện tại."""
    try:
        # TODO: Tích hợp với BehaviorEngine
        return {
            "current_state": "idle",
            "current_emotion": "neutral",
            "is_busy": False
        }
        
    except Exception as e:
        logger.error(f"Lỗi lấy behavior state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/behavior/emotion")
async def set_emotion(emotion: str, intensity: float = 0.5):
    """
    Set emotion cho robot.
    
    Args:
        emotion: Emotion name
        intensity: Cường độ (0.0 - 1.0)
    """
    try:
        # TODO: Tích hợp với EmotionModel
        logger.info(f"Setting emotion: {emotion} (intensity: {intensity})")
        
        return {
            "success": True,
            "emotion": emotion,
            "intensity": intensity
        }
        
    except Exception as e:
        logger.error(f"Lỗi set emotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# WebSocket Endpoint
# ==========================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint cho real-time communication.
    """
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        while True:
            # Nhận data từ client
            data = await websocket.receive_json()
            logger.debug(f"Received WS data: {data}")
            
            # Xử lý và gửi response
            response = {
                "type": "ack",
                "message": "Received",
                "data": data
            }
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# ==========================================
# Metrics Endpoint (Prometheus-compatible)
# ==========================================

@app.get("/metrics")
async def metrics():
    """
    Metrics endpoint (Prometheus format).
    """
    # TODO: Implement proper Prometheus metrics
    metrics_text = """
# HELP ai_engine_requests_total Total requests
# TYPE ai_engine_requests_total counter
ai_engine_requests_total 0

# HELP ai_engine_cpu_usage CPU usage percentage
# TYPE ai_engine_cpu_usage gauge
ai_engine_cpu_usage {cpu_percent}

# HELP ai_engine_memory_usage Memory usage percentage
# TYPE ai_engine_memory_usage gauge
ai_engine_memory_usage {memory_percent}
    """.format(
        cpu_percent=psutil.cpu_percent(),
        memory_percent=psutil.virtual_memory().percent
    )
    
    return metrics_text


# ==========================================
# Startup & Shutdown Events
# ==========================================

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("🚀 API Server starting...")
    # TODO: Khởi tạo các services


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("🛑 API Server shutting down...")
    # TODO: Cleanup các services