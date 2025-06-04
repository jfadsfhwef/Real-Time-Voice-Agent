"""
Language model service using Google Gemini.
"""
import logging
import google.generativeai as genai
from src.config import AgentConfig

logger = logging.getLogger(__name__)

class LanguageModelService:
    """Handles interaction with language models"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.model = None
    
    def initialize(self) -> bool:
        """Initialize the language model"""
        try:
            genai.configure(api_key=self.config.google_api_key)
            self.model = genai.GenerativeModel(self.config.model_name)
            logger.info(f"✅ {self.config.model_name} initialized")
            return True
            
        except Exception as e:
            logger.error(f"Language model initialization failed: {e}")
            return False
    
    async def generate_response(self, prompt: str) -> str:
        """Generate a response from the language model"""
        if not self.model:
            logger.error("Language model not initialized")
            return "I'm sorry, I'm having trouble thinking right now."
            
        try:
            response_obj = self.model.generate_content(prompt)
            return response_obj.text.strip()
            
        except Exception as e:
            logger.error(f"Language model error: {e}")
            return "I'm having trouble processing that. Let's continue with the interview." 