from .base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Increased length for bcrypt hashes

    # Define relationship (one-to-many)
    collections = relationship("Collection", back_populates="owner", cascade="all, delete")