"""
Audio processing utilities for the Voice Agent.
"""
import base64
import io
import logging
import tempfile
import wave
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def convert_wav_to_base64(wav_file_path: str) -> str:
    """Convert a WAV file to base64 encoding"""
    try:
        with open(wav_file_path, "rb") as f:
            audio_data = f.read()
        encoded = base64.b64encode(audio_data).decode("utf-8")
        return encoded
    except Exception as e:
        logger.error(f"Error converting WAV to base64: {e}")
        return ""

def convert_base64_to_wav(base64_data: str, output_path: Optional[str] = None) -> Optional[str]:
    """Convert base64 encoded audio data to a WAV file"""
    try:
        audio_data = base64.b64decode(base64_data)
        
        if not output_path:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name
                
        with open(output_path, "wb") as f:
            f.write(audio_data)
            
        return output_path
    except Exception as e:
        logger.error(f"Error converting base64 to WAV: {e}")
        return None

def get_wav_info(wav_file_path: str) -> Tuple[int, int, int, float]:
    """Get WAV file information (sample rate, channels, sample width, duration)"""
    try:
        with wave.open(wav_file_path, "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            num_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            num_frames = wav_file.getnframes()
            
            # Calculate duration
            duration = num_frames / sample_rate
            
            return sample_rate, num_channels, sample_width, duration
    except Exception as e:
        logger.error(f"Error getting WAV info: {e}")
        return 0, 0, 0, 0.0

def create_silent_wav(duration_ms: int, sample_rate: int = 16000, 
                     num_channels: int = 1, sample_width: int = 2) -> str:
    """Create a silent WAV file of specified duration"""
    try:
        # Calculate number of frames
        num_frames = int((duration_ms / 1000) * sample_rate)
        
        # Create silent audio data (all zeros)
        audio_data = b"\x00" * (num_frames * num_channels * sample_width)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            output_path = tmp_file.name
        
        # Write WAV file
        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
            
        return output_path
    except Exception as e:
        logger.error(f"Error creating silent WAV: {e}")
        return ""
