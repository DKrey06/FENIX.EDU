from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from models import UserRole, UserStatus

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT

class UserCreate(UserBase):
    password: str
    course: Optional[str] = None
    group: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return v
    
    @validator('course', 'group')
    def validate_student_fields(cls, v, values):
        if values.get('role') == UserRole.STUDENT and not v:
            field_name = 'курс' if 'course' in values else 'группу'
            raise ValueError(f'Для студента необходимо указать {field_name}')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    status: UserStatus
    course: Optional[str]
    group: Optional[str]
    created_at: datetime
    confirmed_at: Optional[datetime]
    confirmed_by: Optional[int]

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