# app/models/question.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)  # The question text
    model_answer = Column(Text, nullable=False)  # The reference/correct answer
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    
    # Define relationships
    collection = relationship("Collection", back_populates="questions")
    student_answers = relationship("StudentAnswer", back_populates="question", cascade="all, delete")
    evaluations = relationship("Evaluation", back_populates="question")
