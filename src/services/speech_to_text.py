"""
Speech-to-text service using Deepgram.
"""
import logging
from livekit.plugins import deepgram
from src.config import AgentConfig

logger = logging.getLogger(__name__)

class SpeechToTextService:
    """Handles speech transcription"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.stt = None
    
    async def initialize(self) -> bool:
        """Initialize the STT service"""
        try:
            self.stt = deepgram.STT(
                model="nova-2-general",
                language="en-US", 
                api_key=self.config.deepgram_api_key,
            )
            logger.info("✅ Deepgram STT initialized")
            return True
            
        except Exception as e:
            logger.error(f"STT initialization failed: {e}")
            return False
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text"""
        if not self.stt:
            logger.error("STT service not initialized")
            return ""
            
        try:
            transcript = await self.stt.recognize(audio_data)
            return transcript.strip()
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return "" 