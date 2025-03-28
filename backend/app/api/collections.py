from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database import crud
from app.schemas.collection_schema import CollectionCreate, CollectionResponse, CollectionListResponse, CollectionDeleteResponse
from app.schemas.csv_schema import QuestionUploadResponse, AnswerUploadResponse
from app.services.csv_service import CSVService

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

@router.post("/{collection_id}/upload-questions", response_model=QuestionUploadResponse)
async def upload_questions_csv(collection_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a CSV file with questions and model answers to add to a collection.
    
    Expected CSV format:
    question,model_answer
    "What is X?","X is Y"
    
    Args:
        collection_id: ID of the collection to add questions to
        file: CSV file upload
        
    Returns:
        Statistics about the upload process
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        content = await file.read()
        
        result = CSVService.process_questions_csv(db, collection_id, content)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

@router.post("/{collection_id}/upload-answers", response_model=AnswerUploadResponse)
async def upload_answers_csv(collection_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a CSV file with student answers for a collection.
    
    Expected CSV format:
    student_name,student_pid,question,answer
    "John Doe","johndoe@vt.edu","What is X?","X is Z"
    
    Args:
        collection_id: ID of the collection
        file: CSV file upload
        
    Returns:
        Statistics about the upload process
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        content = await file.read()
        
        result = CSVService.process_answers_csv(db, collection_id, content)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")
