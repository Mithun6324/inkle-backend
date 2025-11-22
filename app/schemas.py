from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    user = "user"
    admin = "admin"
    owner = "owner"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Role
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class PostCreate(BaseModel):
    content: str

class PostOut(BaseModel):
    id: int
    content: str
    owner_id: int
    created_at: datetime
    deleted: bool

    class Config:
        orm_mode = True

class ActivityOut(BaseModel):
    id: int
    actor_id: Optional[int]
    verb: str
    target_user_id: Optional[int]
    target_post_id: Optional[int]
    created_at: datetime
    extra: Optional[str]

    class Config:
        orm_mode = True
