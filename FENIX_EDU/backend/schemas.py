from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models import UserRole, UserStatus


class UserBase(BaseModel):
    email: str
    full_name: str
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str
    course: Optional[str] = None
    group: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    course: Optional[str]
    group: Optional[str]
    created_at: datetime
    confirmed_at: Optional[datetime]
    confirmed_by: Optional[int]
    
    class Config:
        from_attributes = True


class UserUpdateStatus(BaseModel):
    status: UserStatus


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    pages: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: Optional[UserResponse] = None


class CourseCreate(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(BaseModel):
    name: str
    course_id: int