"""
Configuration management for the Voice Agent system.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AgentConfig:
    """Configuration for the voice agent"""
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    room_name: str = "voice-interview-room"
    agent_identity: str = "edge-tts-agent"
    agent_name: str = "Edge TTS Interview Agent"
    google_api_key: str = ""
    deepgram_api_key: str = ""
    tts_voice: str = "en-US-AriaNeural"
    model_name: str = "gemini-1.5-flash"
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Create config from environment variables"""
        return cls(
            livekit_url=os.getenv("LIVEKIT_URL", ""),
            livekit_api_key=os.getenv("LIVEKIT_API_KEY", ""),
            livekit_api_secret=os.getenv("LIVEKIT_API_SECRET", ""),
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            deepgram_api_key=os.getenv("DEEPGRAM_API_KEY", ""),
            room_name=os.getenv("ROOM_NAME", "voice-interview-room")
        )
    
    def validate(self) -> bool:
        """Validate required configuration is present"""
        required_fields = ["livekit_url", "livekit_api_key", "livekit_api_secret", 
                          "google_api_key", "deepgram_api_key"]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field)
        
        if missing_fields:
            return False
        
        return True

# Singleton instance for global access
_config: Optional[AgentConfig] = None

def get_config() -> AgentConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = AgentConfig.from_env()
    return _config 