from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, autoincrement=True)
    school_id = Column(Integer, nullable=False)
    student_name = Column(String, nullable=False)
    
    # Define relationship (one-to-many) with StudentAnswer
    answers = relationship("StudentAnswer", back_populates="student", cascade="all, delete-orphan")
