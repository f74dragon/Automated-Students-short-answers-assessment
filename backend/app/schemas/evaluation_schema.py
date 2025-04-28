# app/schemas/evaluation_schema.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Combination schemas
class CombinationBase(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    model_name: str

class CombinationCreate(CombinationBase):
    pass

class CombinationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    model_name: Optional[str] = None

class Combination(CombinationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CollectionInCombination(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class CombinationWithCollections(Combination):
    collections: List[CollectionInCombination] = []

# Model schemas for Ollama API
class ModelDetails(BaseModel):
    format: Optional[str] = None
    family: Optional[str] = None
    families: Optional[List[str]] = None
    parameter_size: Optional[str] = None
    quantization_level: Optional[str] = None

class ModelInfo(BaseModel):
    name: str
    modified_at: Optional[str] = None
    size: Optional[int] = None
    digest: Optional[str] = None
    details: Optional[ModelDetails] = None

class ModelList(BaseModel):
    models: List[ModelInfo]
