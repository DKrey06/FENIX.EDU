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

class CourseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_group: str

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

class GroupCreate(BaseModel):
    name: str
    course_id: int

class DiscussionCommentCreate(BaseModel):
    course_id: int
    subsection_id: int
    content: str = Field(min_length=1)


class DiscussionReplyCreate(BaseModel):
    content: str = Field(min_length=1)


class DiscussionReplyOut(BaseModel):
    id: int
    author_name: str
    author_role: UserRole
    content: str
    created_at: datetime


class DiscussionCommentOut(BaseModel):
    id: int
    author_name: str
    author_role: UserRole
    content: str
    created_at: datetime
    replies: List[DiscussionReplyOut] = []

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class AssignmentCreate(BaseModel):
    course_id: int
    subsection_id: int
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    
class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None

class AssignmentOut(BaseModel):
    id: int
    course_id: int
    subsection_id: int
    title: str
    description: Optional[str]
    deadline: Optional[datetime]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    content: Optional[str] = None
    file_url: Optional[str] = None

class SubmissionGrade(BaseModel):
    grade: int = Field(ge=0, le=100)
    teacher_comment: Optional[str] = None

class SubmissionOut(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    student_name: str
    content: Optional[str]
    file_url: Optional[str]
    grade: Optional[int]
    teacher_comment: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    teacher_id: int
    content: str = Field(min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    id: int
    thread_id: int
    sender_id: int
    sender_name: str
    sender_role: UserRole
    content: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ThreadResponse(BaseModel):
    id: int
    student_id: int
    teacher_id: int
    student_name: str
    teacher_name: str
    teacher_avatar: str
    partner_name: str  # Имя собеседника (в зависимости от текущего пользователя)
    partner_avatar: str  # Аватар собеседника
    partner_id: int  # ID собеседника
    last_message_at: datetime
    unread_count: int
    is_archived: bool
    last_message: Optional[MessageResponse] = None
    
    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    total_unread: int
    thread_unread_counts: dict[int, int] = {}


class TeacherListResponse(BaseModel):
    teachers: List[UserResponse]
    total: int

from pydantic import BaseModel
from typing import List
from datetime import datetime

class AssignmentAttachmentOut(BaseModel):
    id: int
    assignment_id: int
    name: str
    size: int
    url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
