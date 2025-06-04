"""
Interview manager for handling conversation flow and interview questions.
"""
import logging
from typing import List
from src.services.language_model import LanguageModelService

logger = logging.getLogger(__name__)

class InterviewManager:
    """Manages interview content and conversation flow"""
    
    def __init__(self, language_model: LanguageModelService):
        self.language_model = language_model
        self.question_count = 0
        self.conversation_history: List[str] = []
        self.is_speaking = False
        
        # Interview questions
        self.questions = [
            "Hello! Welcome to your backend development interview. Can you tell me about your experience with REST APIs?",
            "That's great! What's the difference between SQL and NoSQL databases?", 
            "Interesting! How would you design a rate limiting system?",
            "Excellent! How do you debug slow database queries?",
            "Perfect! How do you ensure data consistency in distributed systems?",
            "Thank you! That concludes our interview. You provided excellent insights!"
        ]
    
    async def generate_response(self, user_input: str = "") -> str:
        """Generate response based on conversation state"""
        try:
            if self.question_count == 0:
                # First question
                response = self.questions[0]
                self.question_count += 1
            elif self.question_count < len(self.questions) - 1:
                # Use language model to generate personalized response
                try:
                    prompt = f"""You are a backend development interviewer. 
                    The candidate just said: "{user_input}"
                    
                    Give a brief (1-2 sentences) acknowledgment of their answer, then ask this question:
                    {self.questions[self.question_count]}
                    
                    Keep the total response under 80 words and conversational."""
                    
                    response = await self.language_model.generate_response(prompt)
                    self.question_count += 1
                except Exception as e:
                    logger.warning(f"Language model error, using fallback: {e}")
                    response = f"That's interesting. {self.questions[self.question_count]}"
                    self.question_count += 1
            else:
                # Final question
                response = self.questions[-1]
            
            # Record conversation
            if user_input and user_input.strip():
                self.conversation_history.append(f"Candidate: {user_input}")
            self.conversation_history.append(f"Interviewer: {response}")
            
            # Keep history length manageable
            if len(self.conversation_history) > 8:
                self.conversation_history = self.conversation_history[-6:]
            
            return response
                
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return "Let me ask you another question about your backend experience."
    
    def get_conversation_history(self) -> List[str]:
        """Get the conversation history"""
        return self.conversation_history
    
    def reset_interview(self) -> None:
        """Reset the interview to start again"""
        self.question_count = 0
        self.conversation_history = [] 