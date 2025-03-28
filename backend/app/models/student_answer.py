# app/models/student_answer.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base

class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    answer = Column(Text)  # Student's answer to the question
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    
    # Define relationships
    student = relationship("Student", back_populates="answers")
    question = relationship("Question", back_populates="student_answers")
    llm_responses = relationship("LLMResponse", back_populates="student_answer", cascade="all, delete")
