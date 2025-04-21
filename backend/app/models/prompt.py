from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=func.now(), nullable=True)

    # Relationships
    evaluations = relationship("Evaluation", back_populates="prompt")
    combinations = relationship("Combination", back_populates="prompt")
