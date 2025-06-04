"""
Text-to-speech service using Microsoft Edge TTS.
"""
import os
import logging
import tempfile
import wave
from typing import Optional
import edge_tts
from livekit import rtc
from src.config import AgentConfig

logger = logging.getLogger(__name__)

class TextToSpeechService:
    """Handles text-to-speech synthesis using Edge TTS"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
    
    async def test_connection(self) -> bool:
        """Test Edge TTS connection"""
        try:
            communicate = edge_tts.Communicate("Test", self.config.tts_voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
                    break  # Only test a small segment
            
            if len(audio_data) > 0:
                logger.info("✅ Edge TTS test successful")
                return True
            else:
                logger.error("No audio data received from Edge TTS")
                return False
                
        except Exception as e:
            logger.error(f"Edge TTS test failed: {e}")
            return False
    
    async def synthesize(self, text: str) -> Optional[str]:
        """Synthesize text to speech and return temp file path"""
        try:
            logger.info(f"🔊 Synthesizing: {text[:50]}...")
            
            # Create Edge TTS communicator
            communicate = edge_tts.Communicate(text, self.config.tts_voice)
            
            # Create temporary file to store audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_filename = tmp_file.name
            
            # Save audio to temporary file
            await communicate.save(tmp_filename)
            
            return tmp_filename
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            return None
    
    @staticmethod
    async def play_wav_file(wav_filename: str, audio_source: rtc.AudioSource) -> float:
        """Play WAV file and return duration"""
        try:
            with wave.open(wav_filename, 'rb') as wav_file:
                # Get audio parameters
                sample_rate = wav_file.getframerate()
                num_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                
                logger.info(f"📊 Audio format: {sample_rate}Hz, {num_channels}ch, {sample_width*8}bit")
                
                # Read all audio data
                audio_data = wav_file.readframes(wav_file.getnframes())
                
                # Create audio frame - match LiveKit expected format
                audio_frame = rtc.AudioFrame(
                    data=audio_data,
                    sample_rate=sample_rate,
                    num_channels=num_channels,
                    samples_per_channel=len(audio_data) // (num_channels * sample_width)
                )
                
                # Play audio
                await audio_source.capture_frame(audio_frame)
                
                # Calculate play duration
                duration = len(audio_data) / (sample_rate * num_channels * sample_width)
                return duration
                
        except Exception as e:
            logger.error(f"WAV playback error: {e}")
            return 0.0 