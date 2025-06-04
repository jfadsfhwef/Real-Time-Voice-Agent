"""
FastAPI endpoints for the Voice Agent.
"""
import base64
import logging
import os
import asyncio
import tempfile
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from livekit import api
from src.config import get_config, AgentConfig
from src.api.models import (
    TranscriptionRequest, TranscriptionResponse,
    TextToSpeechRequest, TextToSpeechResponse,
    InterviewQuestion, ConversationHistory, RoomInfo
)
from src.services import SpeechToTextService, TextToSpeechService, LanguageModelService
from src.agent import InterviewManager, LiveKitRoomManager

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store for active rooms (in a real app, use Redis or a database)
active_rooms = {}

# Service dependencies
def get_stt_service():
    """Get speech-to-text service"""
    config = get_config()
    service = SpeechToTextService(config)
    return service

def get_tts_service():
    """Get text-to-speech service"""
    config = get_config()
    service = TextToSpeechService(config)
    return service

def get_lm_service():
    """Get language model service"""
    config = get_config()
    service = LanguageModelService(config)
    service.initialize()  # Initialize on creation
    return service

def get_interview_manager():
    """Get interview manager"""
    lm_service = get_lm_service()
    manager = InterviewManager(lm_service)
    return manager

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    request: TranscriptionRequest,
    stt_service: SpeechToTextService = Depends(get_stt_service)
):
    """Transcribe audio to text"""
    try:
        # Initialize STT service if needed
        await stt_service.initialize()
        
        # Decode base64 audio
        audio_data = base64.b64decode(request.audio_data)
        
        # Transcribe
        text = await stt_service.transcribe(audio_data)
        
        return TranscriptionResponse(text=text, confidence=0.9)
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/synthesize", response_model=TextToSpeechResponse)
async def synthesize_speech(
    request: TextToSpeechRequest,
    tts_service: TextToSpeechService = Depends(get_tts_service)
):
    """Synthesize text to speech"""
    try:
        # Test TTS connection
        await tts_service.test_connection()
        
        # Use the requested voice or default
        if request.voice:
            tts_service.config.tts_voice = request.voice
        
        # Synthesize speech
        wav_file = await tts_service.synthesize(request.text)
        
        if not wav_file:
            raise HTTPException(status_code=500, detail="Speech synthesis failed")
            
        # Read wav file and encode to base64
        with open(wav_file, "rb") as f:
            audio_bytes = f.read()
        
        # Clean up temp file
        os.unlink(wav_file)
        
        # Encode to base64
        audio_data = base64.b64encode(audio_bytes).decode("utf-8")
        
        return TextToSpeechResponse(
            audio_data=audio_data,
            sample_rate=24000,
            format="wav"
        )
    except Exception as e:
        logger.error(f"Speech synthesis error: {e}")
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@router.get("/interview/questions", response_model=List[InterviewQuestion])
async def get_interview_questions(
    interview_manager: InterviewManager = Depends(get_interview_manager)
):
    """Get all interview questions"""
    questions = []
    for i, question in enumerate(interview_manager.questions):
        questions.append(InterviewQuestion(
            text=question,
            index=i
        ))
    return questions

@router.post("/interview/generate", response_model=str)
async def generate_interview_response(
    user_input: str,
    interview_manager: InterviewManager = Depends(get_interview_manager)
):
    """Generate an interview response"""
    try:
        response = await interview_manager.generate_response(user_input)
        return response
    except Exception as e:
        logger.error(f"Response generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Response generation failed: {str(e)}")

@router.get("/interview/history", response_model=ConversationHistory)
async def get_conversation_history(
    interview_manager: InterviewManager = Depends(get_interview_manager)
):
    """Get conversation history"""
    history = interview_manager.get_conversation_history()
    messages = []
    
    for msg in history:
        if msg.startswith("Candidate:"):
            role = "user"
            content = msg[len("Candidate:"):].strip()
        elif msg.startswith("Interviewer:"):
            role = "assistant"
            content = msg[len("Interviewer:"):].strip()
        else:
            continue
            
        messages.append({
            "role": role,
            "content": content
        })
    
    return ConversationHistory(
        messages=messages,
        current_question_index=interview_manager.question_count
    )

@router.post("/interview/reset")
async def reset_interview(
    interview_manager: InterviewManager = Depends(get_interview_manager)
):
    """Reset the interview"""
    interview_manager.reset_interview()
    return {"message": "Interview reset successfully"}

@router.post("/room/create", response_model=RoomInfo)
async def create_room(
    background_tasks: BackgroundTasks,
    config: AgentConfig = Depends(get_config)
):
    """Create a new LiveKit room and return connection details"""
    try:
        # Generate a unique room name if not provided
        room_name = config.room_name
        
        # Create LiveKit token
        token = api.AccessToken(
            config.livekit_api_key,
            config.livekit_api_secret
        )
        
        # Add user identity
        user_identity = f"user-{uuid.uuid4().hex[:8]}"
        token.with_identity(user_identity)
        token.with_name("Interview Candidate")
        
        # Add room access
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name
        ))
        
        # Start agent in background
        background_tasks.add_task(start_agent_in_room, room_name)
        
        return RoomInfo(
            room_name=room_name,
            token=token.to_jwt(),
            url=config.livekit_url
        )
    except Exception as e:
        logger.error(f"Room creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Room creation failed: {str(e)}")

async def start_agent_in_room(room_name: str):
    """Start the agent in the specified room"""
    try:
        # Get config
        config = get_config()
        config.room_name = room_name
        
        # Create room manager
        room_manager = LiveKitRoomManager(config)
        
        # Connect to room
        connected = await room_manager.connect()
        
        if connected:
            logger.info(f"✅ Agent connected to room: {room_name}")
            
            # Store room manager for later access
            active_rooms[room_name] = room_manager
            
            # Keep agent running
            while room_manager.is_connected:
                await asyncio.sleep(5)
                
            # Clean up when disconnected
            if room_name in active_rooms:
                del active_rooms[room_name]
        else:
            logger.error(f"Failed to connect agent to room: {room_name}")
    except Exception as e:
        logger.error(f"Agent start error: {e}")

@router.delete("/room/{room_name}")
async def delete_room(room_name: str):
    """Delete a room and disconnect the agent"""
    if room_name in active_rooms:
        room_manager = active_rooms[room_name]
        await room_manager.disconnect()
        del active_rooms[room_name]
        return {"message": f"Room {room_name} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Room {room_name} not found") 