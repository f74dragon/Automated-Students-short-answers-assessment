from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=True)  # Store model parameters as JSON
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=None, onupdate=func.now(), nullable=True)

    # Relationships
    evaluations = relationship("Evaluation", back_populates="model")
    combinations = relationship("Combination", back_populates="model")
