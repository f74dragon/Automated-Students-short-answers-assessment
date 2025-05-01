from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
import os
from pathlib import Path
from dotenv import load_dotenv

# Calculate the project root dynamically
project_root = Path(__file__).resolve().parents[3] # Adjust index based on actual structure if needed

# Load appropriate .env file based on DOCKERIZED environment variable
if os.getenv("DOCKERIZED") == "true":
    load_dotenv(project_root / ".env.docker")
else:
    load_dotenv(project_root / ".env.local")


DATABASE_URL = os.getenv("DATABASE_URL")
print("Using DATABASE_URL:", DATABASE_URL)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
