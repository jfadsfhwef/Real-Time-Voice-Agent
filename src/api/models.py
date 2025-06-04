"""
Pydantic models for FastAPI endpoints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class TranscriptionRequest(BaseModel):
    """Request model for transcription API"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    sample_rate: int = Field(16000, description="Audio sample rate in Hz")

class TranscriptionResponse(BaseModel):
    """Response model for transcription API"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(0.0, description="Confidence score from 0 to 1")

class TextToSpeechRequest(BaseModel):
    """Request model for text-to-speech API"""
    text: str = Field(..., description="Text to synthesize")
    voice: Optional[str] = Field("en-US-AriaNeural", description="Voice to use")

class TextToSpeechResponse(BaseModel):
    """Response model for text-to-speech API"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    sample_rate: int = Field(24000, description="Audio sample rate in Hz")
    format: str = Field("wav", description="Audio format")

class InterviewQuestion(BaseModel):
    """Model for an interview question"""
    text: str = Field(..., description="Question text")
    index: int = Field(..., description="Question index")

class ConversationMessage(BaseModel):
    """Model for a conversation message"""
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")

class ConversationHistory(BaseModel):
    """Model for conversation history"""
    messages: List[ConversationMessage] = Field(default_factory=list, description="List of conversation messages")
    current_question_index: int = Field(0, description="Current question index")

class RoomInfo(BaseModel):
    """Model for room information"""
    room_name: str = Field(..., description="Room name")
    token: str = Field(..., description="JWT token for room access")
    url: str = Field(..., description="LiveKit server URL") 