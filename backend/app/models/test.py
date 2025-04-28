from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Test(Base):
    """Model for storing test configurations."""
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    model_names = Column(JSON, nullable=False)  # Store as JSON array
    prompt_ids = Column(JSON, nullable=False)  # Store as JSON array
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    results = relationship("TestResult", back_populates="test", cascade="all, delete-orphan")
    summaries = relationship("TestSummary", back_populates="test", cascade="all, delete-orphan")


class TestResult(Base):
    """Model for storing individual test results."""
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    model_name = Column(String, nullable=False)
    prompt_id = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    model_answer = Column(Text, nullable=False)
    model_grade = Column(Float, nullable=False)
    extracted_grade = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)
    response_time = Column(Float, nullable=False)
    full_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test = relationship("Test", back_populates="results")


class TestSummary(Base):
    """Model for storing test summary statistics."""
    __tablename__ = "test_summaries"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"), nullable=False)
    model_name = Column(String, nullable=False)
    prompt_id = Column(Integer, nullable=False)
    average_accuracy = Column(Float, nullable=False)
    average_response_time = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test = relationship("Test", back_populates="summaries")
