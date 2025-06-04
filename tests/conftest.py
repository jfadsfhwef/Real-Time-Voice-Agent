"""
Pytest configuration and fixtures for testing.
"""
import os
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from src.config import AgentConfig
from src.main import app
from src.services import (
    SpeechToTextService, 
    TextToSpeechService, 
    LanguageModelService
)
from src.agent import InterviewManager

@pytest.fixture
def test_client() -> Generator:
    """Create a FastAPI test client"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def test_config() -> AgentConfig:
    """Create a test configuration"""
    return AgentConfig(
        livekit_url="wss://example.livekit.io",
        livekit_api_key="test_key",
        livekit_api_secret="test_secret",
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        deepgram_api_key=os.getenv("DEEPGRAM_API_KEY", ""),
        room_name="test-room",
        agent_identity="test-agent",
        agent_name="Test Agent",
        tts_voice="en-US-AriaNeural",
        model_name="gemini-1.5-flash"
    )

@pytest.fixture
def tts_service(test_config) -> TextToSpeechService:
    """Create a text-to-speech service"""
    return TextToSpeechService(test_config)

@pytest.fixture
def lm_service(test_config) -> LanguageModelService:
    """Create a language model service"""
    return LanguageModelService(test_config)

@pytest.fixture
def interview_manager(lm_service) -> InterviewManager:
    """Create an interview manager"""
    return InterviewManager(lm_service)

# Helper for async tests
@pytest.fixture
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 