from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    example_answer = Column(Text, nullable=False)

    # Define relationship (many-to-one)
    collection = relationship("Collection", back_populates="questions")
    
    # Define relationship (one-to-many) with StudentAnswer
    student_answers = relationship("StudentAnswer", back_populates="question", cascade="all, delete-orphan")
