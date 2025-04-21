from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class Model(ModelBase):
    id: int
    is_active: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ModelInfo(BaseModel):
    name: str
    modified_at: Optional[str] = None
    size: Optional[int] = None
    digest: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ModelList(BaseModel):
    models: List[ModelInfo]
