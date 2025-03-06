from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True  # Needed for ORM integration

class UserListResponse(BaseModel):
    users: List[UserResponse]

    class Config:
        from_attributes = True

class UserDeleteResponse(BaseModel):
    message: str