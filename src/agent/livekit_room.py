"""
LiveKit room management module for handling audio connections.
"""
import asyncio
import os
import logging
from livekit import rtc, api
from src.config import AgentConfig
from src.services import SpeechToTextService, TextToSpeechService, LanguageModelService
from src.agent.interview_manager import InterviewManager

logger = logging.getLogger(__name__)

class LiveKitRoomManager:
    """Manages LiveKit room connection and audio processing"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.room = rtc.Room()
        self.audio_source = None
        self.is_connected = False
        
        # Services
        self.stt_service = SpeechToTextService(config)
        self.tts_service = TextToSpeechService(config)
        self.lm_service = LanguageModelService(config)
        self.interview_manager = InterviewManager(self.lm_service)
    
    async def initialize(self) -> bool:
        """Initialize all services"""
        logger.info("Initializing services...")
        
        # Initialize language model
        if not self.lm_service.initialize():
            return False
        
        # Initialize STT
        if not await self.stt_service.initialize():
            return False
        
        # Test TTS
        if not await self.tts_service.test_connection():
            return False
        
        return True
    
    async def connect(self) -> bool:
        """Connect to LiveKit room"""
        try:
            # Initialize services
            if not await self.initialize():
                return False
            
            # Create token
            token = api.AccessToken(
                self.config.livekit_api_key,
                self.config.livekit_api_secret
            )
            token.with_identity(self.config.agent_identity)
            token.with_name(self.config.agent_name)
            token.with_grants(api.VideoGrants(
                room_join=True,
                room=self.config.room_name
            ))
            
            # Set up event handlers
            @self.room.on("participant_connected")
            def on_participant_connected(participant):
                logger.info(f"👤 {participant.identity} joined!")
                asyncio.create_task(self.start_interview())
            
            @self.room.on("track_subscribed")
            def on_track_subscribed(track, publication, participant):
                logger.info(f"🎵 Got {track.kind} track from {participant.identity}")
                if track.kind == rtc.TrackKind.KIND_AUDIO:
                    logger.info("🎤 Starting audio processing...")
                    asyncio.create_task(self.handle_user_audio())
            
            # Connect
            await self.room.connect(
                url=self.config.livekit_url,
                token=token.to_jwt()
            )
            
            # Set up audio track
            await self.setup_audio()
            
            self.is_connected = True
            logger.info("✅ Connected to LiveKit room!")
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def setup_audio(self):
        """Set up audio track"""
        try:
            # Create audio source - use standard sampling rate
            self.audio_source = rtc.AudioSource(
                sample_rate=16000,  # Standard sampling rate
                num_channels=1
            )
            
            # Create audio track
            audio_track = rtc.LocalAudioTrack.create_audio_track(
                "agent-voice",
                self.audio_source
            )
            
            # Publish track
            await self.room.local_participant.publish_track(audio_track)
            logger.info("✅ Audio track published (16kHz)")
            
        except Exception as e:
            logger.error(f"Audio setup failed: {e}")
    
    async def start_interview(self):
        """Start the interview"""
        try:
            await asyncio.sleep(2)  # Wait for connection to stabilize
            
            # Generate welcome message
            welcome = await self.interview_manager.generate_response()
            logger.info(f"🎙️ Starting interview: {welcome}")
            
            # Play welcome message
            if self.audio_source:
                await self.speak(welcome)
            
        except Exception as e:
            logger.error(f"Interview start error: {e}")
    
    async def speak(self, text: str):
        """Synthesize and play speech"""
        try:
            self.interview_manager.is_speaking = True
            
            # Synthesize speech
            wav_file = await self.tts_service.synthesize(text)
            
            if wav_file and self.audio_source:
                # Play WAV file
                duration = await self.tts_service.play_wav_file(wav_file, self.audio_source)
                
                # Wait for audio to finish playing
                await asyncio.sleep(duration)
                
                # Clean up temporary file
                os.unlink(wav_file)
                
            logger.info("✅ Speech completed")
                
        except Exception as e:
            logger.error(f"Speech error: {e}")
            logger.info(f"💬 [TEXT ONLY] Agent says: {text}")
        finally:
            self.interview_manager.is_speaking = False
    
    async def handle_user_audio(self):
        """Handle user audio (simplified version)"""
        # Simulate audio processing - in a real application this would handle real audio
        test_responses = [
            "I have 3 years of experience building REST APIs with Node.js and Python Flask",
            "SQL databases are good for structured data with ACID properties, while NoSQL databases like MongoDB are better for flexible schemas and horizontal scaling",
            "I would implement rate limiting using Redis with a token bucket algorithm, storing counters per user and resetting them periodically",
            "To debug slow queries, I would first check the execution plan, then add appropriate indexes, and optimize the query structure",
            "For data consistency, I use database transactions for ACID operations and implement event sourcing with saga patterns for distributed systems"
        ]
        
        for i, response in enumerate(test_responses):
            # Wait some time to simulate user thinking and speaking
            await asyncio.sleep(8)
            
            if not self.is_connected:
                break
                
            logger.info(f"👤 User: {response}")
            
            # Generate AI response
            ai_response = await self.interview_manager.generate_response(response)
            logger.info(f"🤖 Agent: {ai_response}")
            
            # Play AI response
            if self.audio_source and not self.interview_manager.is_speaking:
                await self.speak(ai_response)
            
            # If last question, end
            if self.interview_manager.question_count >= len(self.interview_manager.questions):
                break
    
    async def disconnect(self):
        """Disconnect from LiveKit room"""
        if self.is_connected:
            await self.room.disconnect()
            self.is_connected = False
            logger.info("✅ Disconnected from LiveKit room") 