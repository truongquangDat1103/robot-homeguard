"""
Pytest configuration và shared fixtures.
"""
import pytest
import asyncio


@pytest.fixture
def sample_frame():
    """Tạo sample video frame."""
    import numpy as np
    return np.ones((480, 640, 3), dtype=np.uint8) * 128


@pytest.fixture
def sample_audio():
    """Tạo sample audio data."""
    import numpy as np
    return np.random.randn(16000)  # 1 second at 16kHz


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "text": "Test response",
        "model": "gpt-4",
        "tokens_used": 50
    }


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()