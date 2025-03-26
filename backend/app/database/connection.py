from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.models.base import Base
import os
import time
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Add retry logic to handle database not being ready immediately
    max_retries = 10
    retry_interval = 3  # seconds
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print(f"Successfully connected to database on attempt {attempt + 1}")
            return  # Exit function if successful
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print("Max retries reached. Could not connect to database.")
                raise  # Re-raise the last exception if all retries fail

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
