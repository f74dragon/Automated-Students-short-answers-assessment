# app/models/student.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    pid = Column(String, nullable=False)  # Personal Identifier (email)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    
    # Define relationships
    collection = relationship("Collection", back_populates="students")
    answers = relationship("StudentAnswer", back_populates="student", cascade="all, delete")
