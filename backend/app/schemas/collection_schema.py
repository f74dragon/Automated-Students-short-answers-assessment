# app/schemas/collection_schema.py
from pydantic import BaseModel
from typing import List

class CollectionCreate(BaseModel):
    user_id: int
    name: str
    description: str
    question: str  # Add this field

class CollectionResponse(CollectionCreate):
    id: int

    class Config:
        from_attributes = True 

class CollectionListResponse(BaseModel):
    collections: List[CollectionResponse]

class CollectionDeleteResponse(BaseModel):
    message: str