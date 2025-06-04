"""
Tests for the text-to-speech service.
"""
import os
import pytest
import asyncio
from src.services import TextToSpeechService
from src.utils.audio import get_wav_info

@pytest.mark.asyncio
async def test_tts_connection(tts_service):
    """Test TTS connection"""
    # Check if we can connect to Edge TTS
    result = await tts_service.test_connection()
    assert result is True

@pytest.mark.asyncio
async def test_tts_synthesis(tts_service):
    """Test TTS synthesis"""
    # Synthesize a short text
    text = "This is a test of the text to speech service."
    wav_file = await tts_service.synthesize(text)
    
    # Check if file was created
    assert wav_file is not None
    assert os.path.exists(wav_file)
    
    # Check WAV file properties
    sample_rate, channels, sample_width, duration = get_wav_info(wav_file)
    assert sample_rate > 0
    assert channels > 0
    assert sample_width > 0
    assert duration > 0
    
    # Clean up
    os.unlink(wav_file) 