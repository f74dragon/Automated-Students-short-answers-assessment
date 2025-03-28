# app/models/llm_response.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import relationship
import datetime
from .base import Base

class LLMResponse(Base):
    __tablename__ = "llm_responses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_response = Column(Text)  # Full LLM response text
    grade = Column(Float)  # Extracted numerical grade (0.0-1.0)
    feedback = Column(Text)  # Optional extracted feedback
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    student_answer_id = Column(Integer, ForeignKey("student_answers.id", ondelete="CASCADE"), nullable=False)
    
    # Define relationship
    student_answer = relationship("StudentAnswer", back_populates="llm_responses")
