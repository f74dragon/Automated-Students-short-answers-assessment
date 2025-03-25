from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Problem(Base):
    __tablename__ = "problems"
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    question = Column(String, primary_key=True)
    example_answer = Column(String)
    

    # Define relationships
    collection = relationship("Collection", back_populates="problems")
