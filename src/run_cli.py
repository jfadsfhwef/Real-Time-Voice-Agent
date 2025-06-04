"""
CLI script to run the Voice Agent directly without the FastAPI server.
"""
import asyncio
import logging
import argparse
from src.config import get_config
from src.agent import LiveKitRoomManager
from src.utils.logging import setup_logging

logger = setup_logging()

async def run_agent(room_name: str = None):
    """Run the agent directly"""
    try:
        # Get config
        config = get_config()
        
        if room_name:
            config.room_name = room_name
            
        logger.info(f"Starting agent in room: {config.room_name}")
        
        # Create room manager
        room_manager = LiveKitRoomManager(config)
        
        # Connect to room
        connected = await room_manager.connect()
        
        if connected:
            logger.info("✅ Edge TTS Agent ready!")
            logger.info("🔊 Using Microsoft Edge TTS (completely free)")
            logger.info(f"🌐 Connect via LiveKit Meet: https://meet.livekit.io/")
            logger.info(f"📋 Room: {config.room_name}")
            logger.info("⏰ Waiting for participants...")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(10)
                    if not room_manager.is_connected:
                        logger.warning("Connection lost, attempting reconnect...")
                        await room_manager.connect()
            except KeyboardInterrupt:
                logger.info("👋 Shutting down...")
            finally:
                await room_manager.disconnect()
        else:
            logger.error("❌ Failed to start agent")
            
    except Exception as e:
        logger.error(f"Error running agent: {e}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Run the Voice Agent CLI")
    parser.add_argument("--room", "-r", help="Room name to join", default=None)
    parser.add_argument("--debug", "-d", help="Enable debug logging", action="store_true")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the agent
    asyncio.run(run_agent(args.room))

if __name__ == "__main__":
    main() 