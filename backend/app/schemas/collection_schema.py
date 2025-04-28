# app/schemas/collection_schema.py
from pydantic import BaseModel
from typing import List, Optional

class CollectionCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    combination_id: Optional[int] = None

class CollectionResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    combination_id: Optional[int] = None

    class Config:
        from_attributes = True 

class CollectionListResponse(BaseModel):
    collections: List[CollectionResponse]

class CollectionDeleteResponse(BaseModel):
    message: str

class CollectionUpdateCombination(BaseModel):
    combination_id: Optional[int] = None
