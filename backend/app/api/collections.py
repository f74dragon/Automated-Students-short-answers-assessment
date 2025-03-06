from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import crud
from app.schemas.collection_schema import CollectionCreate, CollectionResponse, CollectionListResponse, CollectionDeleteResponse

"""
API Endpoints for Collection Operations
"""

router = APIRouter(prefix="/collections", tags=["collections"])

# Creates a collection and inserts into db
@router.post("/", response_model=CollectionResponse)
def create_user(collection: CollectionCreate, db: Session = Depends(get_db)):
    return crud.create_collection(db=db, collection=collection)

# Get a list of all collections for a given user; will need to change endpoint when integrating with JWT tokens
# since user_id will be obtainable from token
@router.get("/{user_id}", response_model=CollectionListResponse)
def get_collections(user_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_collections(db=db, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get a specific collection for a given user; will need to change endpoint when integrating with JWT tokens
# since user_id will be obtainable from token
@router.get("/{user_id}/{collection_id}", response_model=CollectionResponse)
def get_user(user_id: int, collection_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_collection(db=db, user_id=user_id, collection_id=collection_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# @router.delete("/users/{user_id}", response_model=UserDeleteResponse)
# def remove_user(user_id: int, db: Session = Depends(get_db)):
#     try:
#         return crud.delete_user(db, user_id)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))