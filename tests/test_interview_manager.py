"""
Tests for the interview manager.
"""
import pytest
import asyncio
from src.agent import InterviewManager

def test_interview_questions(interview_manager):
    """Test interview questions are available"""
    assert len(interview_manager.questions) > 0
    assert isinstance(interview_manager.questions, list)
    assert all(isinstance(q, str) for q in interview_manager.questions)

def test_reset_interview(interview_manager):
    """Test interview reset functionality"""
    # Set some state
    interview_manager.question_count = 3
    interview_manager.conversation_history = ["Test message"]
    
    # Reset
    interview_manager.reset_interview()
    
    # Verify reset state
    assert interview_manager.question_count == 0
    assert interview_manager.conversation_history == []

@pytest.mark.asyncio
async def test_first_question(interview_manager):
    """Test getting the first question"""
    response = await interview_manager.generate_response()
    
    # First question should be returned
    assert response == interview_manager.questions[0]
    assert interview_manager.question_count == 1
    
    # History should be updated
    assert len(interview_manager.conversation_history) == 1
    assert interview_manager.conversation_history[0].startswith("Interviewer:")

@pytest.mark.asyncio
async def test_conversation_history(interview_manager):
    """Test conversation history management"""
    # First question
    await interview_manager.generate_response()
    
    # User response
    user_input = "I have 3 years of experience with RESTful APIs."
    await interview_manager.generate_response(user_input)
    
    # Check history has both messages
    assert len(interview_manager.conversation_history) >= 2
    assert any(msg.startswith("Candidate: I have 3 years") for msg in interview_manager.conversation_history)
    
    # Get history
    history = interview_manager.get_conversation_history()
    assert isinstance(history, list)
    assert len(history) >= 2 