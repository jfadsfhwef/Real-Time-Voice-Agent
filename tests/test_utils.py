"""
Tests for utility functions.
"""
import os
import tempfile
import base64
from src.utils.audio import (
    convert_wav_to_base64,
    convert_base64_to_wav,
    get_wav_info,
    create_silent_wav
)

def test_create_silent_wav():
    """Test creating a silent WAV file"""
    # Create a 500ms silent WAV
    wav_file = create_silent_wav(500)
    
    # Check file exists and is non-empty
    assert os.path.exists(wav_file)
    assert os.path.getsize(wav_file) > 0
    
    # Check WAV properties
    sample_rate, channels, sample_width, duration = get_wav_info(wav_file)
    assert sample_rate == 16000  # Default sample rate
    assert channels == 1  # Mono
    assert sample_width == 2  # 16-bit
    assert 0.49 < duration < 0.51  # Around 500ms
    
    # Clean up
    os.unlink(wav_file)

def test_wav_to_base64_conversion():
    """Test WAV to base64 conversion"""
    # Create a silent WAV
    wav_file = create_silent_wav(300)
    
    # Convert to base64
    base64_data = convert_wav_to_base64(wav_file)
    assert base64_data
    assert isinstance(base64_data, str)
    
    # Check base64 is valid
    try:
        decoded = base64.b64decode(base64_data)
        assert len(decoded) > 0
    except:
        assert False, "Invalid base64 data"
    
    # Clean up
    os.unlink(wav_file)

def test_base64_to_wav_conversion():
    """Test base64 to WAV conversion"""
    # Create a silent WAV and convert to base64
    wav_file = create_silent_wav(300)
    base64_data = convert_wav_to_base64(wav_file)
    
    # Convert back to WAV
    output_wav = convert_base64_to_wav(base64_data)
    
    # Check file exists
    assert os.path.exists(output_wav)
    assert os.path.getsize(output_wav) > 0
    
    # Validate WAV properties
    sample_rate, channels, sample_width, duration = get_wav_info(output_wav)
    assert sample_rate == 16000  # Default sample rate
    assert channels == 1  # Mono
    assert sample_width == 2  # 16-bit
    
    # Clean up
    os.unlink(wav_file)
    os.unlink(output_wav)

def test_get_wav_info():
    """Test getting WAV file information"""
    # Create a silent WAV with custom parameters
    wav_file = create_silent_wav(
        duration_ms=1000,  # 1 second
        sample_rate=22050,  # Custom sample rate
        num_channels=2,     # Stereo
        sample_width=2      # 16-bit
    )
    
    # Get info
    sample_rate, channels, sample_width, duration = get_wav_info(wav_file)
    
    # Check properties match what we specified
    assert sample_rate == 22050
    assert channels == 2
    assert sample_width == 2
    assert 0.99 < duration < 1.01  # Around 1 second
    
    # Clean up
    os.unlink(wav_file) 