# app/models/collection.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Collection(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Define relationships
    owner = relationship("User", back_populates="collections")
    students = relationship("Student", back_populates="collection", cascade="all, delete")
    questions = relationship("Question", back_populates="collection", cascade="all, delete")
