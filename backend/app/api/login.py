from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import crud
from app.schemas.user_schema import UserCreate
from app.schemas.token_schema import TokenResponse
from app.auth.auth import authenticate_user, create_access_token
from datetime import timedelta

router = APIRouter()

# @router.post("/register", response_model=UserCreate)
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     existing_user = db.query(User).filter(User.username == user.username).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Username already taken")

#     hashed_password = get_password_hash(user.password)
#     new_user = User(username=user.username, password_hash=hashed_password)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

@router.post("/login", response_model=TokenResponse)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}