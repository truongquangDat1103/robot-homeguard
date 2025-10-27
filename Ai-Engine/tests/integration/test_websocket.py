"""
Integration tests cho WebSocket.
"""
import pytest
import asyncio

from src.services.websocket import WebSocketManager, get_websocket_manager


@pytest.mark.asyncio
async def test_websocket_manager_start_stop():
    """Test start và stop WebSocket manager."""
    manager = WebSocketManager()
    
    # Mock connection
    with patch.object(manager.client, 'connect', return_value=True):
        success = await manager.start()
        assert success
        assert manager._initialized
    
    await manager.stop()
    assert not manager._initialized


@pytest.mark.asyncio
async def test_send_heartbeat():
    """Test gửi heartbeat."""
    manager = WebSocketManager()
    
    with patch.object(manager.client, 'send_message', return_value=True):
        success = await manager.send_heartbeat()
        assert success