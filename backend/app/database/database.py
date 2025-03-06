from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

DATABASE_URL = "postgresql://user:password@host.docker.internal:5432/mydatabase"

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
