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
def create_collection(collection: CollectionCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_collection(db=db, collection=collection)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Get a list of all collections in the db
@router.get("/", response_model=CollectionListResponse)
def get_all_collections(db: Session = Depends(get_db)):
    return crud.get_all_collections(db=db)

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
def get_collection(user_id: int, collection_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_collection(db=db, user_id=user_id, collection_id=collection_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{user_id}/{collection_id}", response_model=CollectionDeleteResponse)
def remove_collection(user_id: int, collection_id: int, db: Session = Depends(get_db)):
    try:
        return crud.delete_collection(db=db, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.patch("/{user_id}/{collection_id}", response_model=CollectionResponse)
def update_collection(user_id: int, collection_id: int, collection: CollectionCreate, db: Session = Depends(get_db)):
    try:
        return crud.update_collection(db=db, user_id=user_id, collection_id=collection_id, new_collection=collection)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))