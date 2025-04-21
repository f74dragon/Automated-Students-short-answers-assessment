from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    student_answer_id = Column(Integer, ForeignKey("student_answers.id"), nullable=True)
    prompt_template = Column(Text, nullable=True)  # Cache of the prompt template used
    model_name = Column(String, nullable=True)     # Cache of the model name used
    metrics = Column(JSON, nullable=False)         # Store evaluation metrics
    combination_id = Column(Integer, ForeignKey("combinations.id"), nullable=True)  # Reference to combination
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=func.now(), nullable=True)
    
    # Relationships
    prompt = relationship("Prompt", back_populates="evaluations")
    model = relationship("Model", back_populates="evaluations")
    question = relationship("Question", back_populates="evaluations")
    student_answer = relationship("StudentAnswer", back_populates="evaluations")
    combination = relationship("Combination", back_populates="evaluations")


class Combination(Base):
    __tablename__ = "combinations"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)   # Additional parameters for this combination
    is_active = Column(Boolean, default=False) # Whether this is the active combination
    prompt_template = Column(Text, nullable=True)  # Cache of the prompt template
    model_name = Column(String, nullable=True)     # Cache of the model name
    average_accuracy = Column(Float, nullable=True)
    average_response_time = Column(Float, nullable=True)
    consistency_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=func.now(), nullable=True)
    
    # Relationships
    prompt = relationship("Prompt", back_populates="combinations")
    model = relationship("Model", back_populates="combinations")
    evaluations = relationship("Evaluation", back_populates="combination")
