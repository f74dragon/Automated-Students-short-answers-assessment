from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PromptBase(BaseModel):
    name: str
    category: str
    prompt: str

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    prompt: Optional[str] = None

class Prompt(PromptBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CategoryList(BaseModel):
    categories: List[str]
