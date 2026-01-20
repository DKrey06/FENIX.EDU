from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DEPARTMENT_HEAD = "department_head"
    TEACHER = "teacher"
    STUDENT = "student"


class UserStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.PENDING)

    course = Column(String, nullable=True)
    group = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    confirmations_given = relationship("User", foreign_keys=[confirmed_by])

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "course": self.course,
            "group": self.group,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "confirmed_by": self.confirmed_by,
        }


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "course_id": self.course_id,
            "course_name": self.course.name if self.course else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CourseStructureModel(Base):
    __tablename__ = "course_structures"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), unique=True, index=True, nullable=False)
    data = Column(JSON, nullable=False)

    course = relationship("Course", backref="structure")


class DiscussionComment(Base):
    __tablename__ = "discussion_comments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), index=True, nullable=False)
    subsection_id = Column(Integer, index=True, nullable=False)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User")
    replies = relationship(
        "DiscussionReply",
        back_populates="comment",
        cascade="all, delete-orphan",
        order_by="DiscussionReply.created_at",
    )


class DiscussionReply(Base):
    __tablename__ = "discussion_replies"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("discussion_comments.id"), index=True, nullable=False)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User")
    comment = relationship("DiscussionComment", back_populates="replies")

# Добавить в models.py в конец файла:

class MessageThread(Base):
    __tablename__ = "message_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    unread_count = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    
    # Отношения
    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])
    messages = relationship(
        "Message",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "teacher_id": self.teacher_id,
            "student_name": self.student.full_name if self.student else "",
            "teacher_name": self.teacher.full_name if self.teacher else "",
            "teacher_avatar": get_avatar_initials(self.teacher.full_name if self.teacher else ""),
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "unread_count": self.unread_count,
            "is_archived": self.is_archived
        }


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("message_threads.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    thread = relationship("MessageThread", back_populates="messages")
    sender = relationship("User")
    
    def to_dict(self):
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.full_name if self.sender else "",
            "sender_role": self.sender.role if self.sender else UserRole.STUDENT,
            "content": self.content,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

def get_avatar_initials(name: str) -> str:
    if not name:
        return "👤"
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper() if len(name) >= 2 else name[0].upper() + "?"