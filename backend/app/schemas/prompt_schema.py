from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class PromptBase(BaseModel):
    template: str
    name: str
    description: Optional[str] = None


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    template: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class Prompt(PromptBase):
    id: int
    is_active: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class PromptWithMetrics(Prompt):
    metrics: Optional[Dict] = None
