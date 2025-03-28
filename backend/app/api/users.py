from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import crud
from app.schemas.user_schema import UserCreate, UserResponse, UserListResponse, UserDeleteResponse

"""
API Endpoints for Collection Operations
"""

router = APIRouter(prefix="/users", tags=["users"])

# Creates a user and inserts into db
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

# Get a list of all users; only for backend testing
@router.get("/", response_model=UserListResponse)
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db=db)

# Get a specific user; will need to change endpoint when integrating with JWT tokens
# since user_id will be obtainable from token
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_user(db=db, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get delete a specific user; only for backend testing
@router.delete("/{user_id}", response_model=UserDeleteResponse)
def remove_user(user_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

