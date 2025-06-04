"""
Basic usage example for the Voice Agent.

This example demonstrates:
1. Text-to-speech synthesis
2. Basic interview flow
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from src.config import AgentConfig
from src.services import TextToSpeechService, LanguageModelService
from src.agent import InterviewManager
from src.utils.logging import setup_logging

# Set up logging
logger = setup_logging()

async def main():
    """Run the example"""
    # Load environment variables
    load_dotenv()
    
    # Create config
    config = AgentConfig(
        livekit_url="wss://example.livekit.io",  # Not used in this example
        livekit_api_key="fake_key",              # Not used in this example
        livekit_api_secret="fake_secret",        # Not used in this example
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        deepgram_api_key=os.getenv("DEEPGRAM_API_KEY", ""),  # Not used in this example
    )
    
    # Initialize TTS service
    tts_service = TextToSpeechService(config)
    
    # Test TTS connection
    if not await tts_service.test_connection():
        logger.error("Failed to connect to Edge TTS")
        return
    
    # Initialize language model
    lm_service = LanguageModelService(config)
    if not lm_service.initialize():
        logger.error("Failed to initialize language model")
        return
    
    # Create interview manager
    interview_manager = InterviewManager(lm_service)
    
    # Simulate interview
    logger.info("=== Starting simulated interview ===")
    
    # Get first question
    question = await interview_manager.generate_response()
    logger.info(f"🤖 Agent: {question}")
    
    # Synthesize speech
    wav_file = await tts_service.synthesize(question)
    if wav_file:
        logger.info(f"✅ Synthesized speech to {wav_file}")
        # In a real app, you would play this audio
        os.unlink(wav_file)
    
    # Simulate user responses
    user_responses = [
        "I have 3 years of experience with RESTful APIs, having worked on several microservices projects.",
        "SQL databases ensure ACID properties and are great for structured data, while NoSQL databases offer flexibility and horizontal scaling.",
        "I would implement rate limiting using Redis with token bucket algorithm, tracking per client usage with expiring keys."
    ]
    
    # Process each response
    for user_input in user_responses:
        logger.info(f"👤 User: {user_input}")
        
        # Generate agent response
        response = await interview_manager.generate_response(user_input)
        logger.info(f"🤖 Agent: {response}")
        
        # Synthesize speech
        wav_file = await tts_service.synthesize(response)
        if wav_file:
            logger.info(f"✅ Synthesized speech to {wav_file}")
            # In a real app, you would play this audio
            os.unlink(wav_file)
    
    # Show conversation history
    logger.info("=== Conversation History ===")
    for message in interview_manager.get_conversation_history():
        logger.info(message)

if __name__ == "__main__":
    asyncio.run(main()) 