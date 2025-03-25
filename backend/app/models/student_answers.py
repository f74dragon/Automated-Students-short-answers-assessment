from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Student_Answers(Base):
    __tablename__ = "student_answers"
    student_name = Column(String, primary_key=True)
    question = Column(String, ForeignKey("problems.question", ondelete="CASCADE"), nullable=False, primary_key=True)
    answer = Column(String)
    
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)

    # Define relationships
    collection = relationship("Collection", back_populates="student_answers")
    problem = relationship("Problem", back_populates="student_answers", foreign_keys=[collection_id, question])