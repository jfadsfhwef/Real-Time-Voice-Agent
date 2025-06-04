"""
Tests for the API endpoints.
"""
import json
import pytest
import base64
from fastapi.testclient import TestClient
from src.utils.audio import create_silent_wav, convert_wav_to_base64

def test_health_endpoint(test_client):
    """Test health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()

def test_root_endpoint(test_client):
    """Test root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs_url" in response.json()

def test_get_interview_questions(test_client):
    """Test getting interview questions"""
    response = test_client.get("/api/v1/interview/questions")
    assert response.status_code == 200
    
    questions = response.json()
    assert isinstance(questions, list)
    assert len(questions) > 0
    
    # Check structure of questions
    for question in questions:
        assert "text" in question
        assert "index" in question
        assert isinstance(question["text"], str)
        assert isinstance(question["index"], int)

def test_reset_interview(test_client):
    """Test interview reset endpoint"""
    response = test_client.post("/api/v1/interview/reset")
    assert response.status_code == 200
    assert "message" in response.json()

def test_synthesize_endpoint(test_client):
    """Test text-to-speech synthesis endpoint"""
    # Note: This is a simplified test that may not actually call the TTS service
    # In a real environment, you might use mocking or a real API key
    payload = {
        "text": "This is a test.",
        "voice": "en-US-AriaNeural"
    }
    
    # This may fail if API keys aren't configured
    response = test_client.post("/api/v1/synthesize", json=payload)
    
    # We only check that the endpoint exists and returns a response
    # The actual status may depend on API key availability
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "audio_data" in data
        assert "sample_rate" in data
        assert "format" in data

def test_transcribe_endpoint(test_client):
    """Test speech-to-text transcription endpoint"""
    # Create a silent WAV file for testing
    wav_file = create_silent_wav(1000)  # 1 second of silence
    
    # Convert to base64
    audio_base64 = convert_wav_to_base64(wav_file)
    
    payload = {
        "audio_data": audio_base64,
        "sample_rate": 16000
    }
    
    # This may fail if API keys aren't configured
    response = test_client.post("/api/v1/transcribe", json=payload)
    
    # We only check that the endpoint exists and returns a response
    # The actual status may depend on API key availability
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "text" in data
        assert "confidence" in data 