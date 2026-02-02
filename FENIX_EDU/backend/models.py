import enum
from datetime import datetime

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

from database import Base


# -------- enums --------

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


# -------- users --------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)

    # Для студентов (упрощённо строками, как у тебя в коде)
    course = Column(String, nullable=True)
    group = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # relationships
    confirmed_by_user = relationship("User", remote_side=[id], uselist=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "status": self.status,
            "course": self.course,
            "group": self.group,
            "created_at": self.created_at,
            "confirmed_at": self.confirmed_at,
            "confirmed_by": self.confirmed_by,
        }


# -------- courses/groups --------

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # группа, для которой предназначен курс (используется в /api/courses для студентов)
    target_group = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    groups = relationship("Group", back_populates="course", cascade="all, delete-orphan")
    structures = relationship("CourseStructureModel", back_populates="course", cascade="all, delete-orphan")
    discussions = relationship("DiscussionComment", back_populates="course", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_group": self.target_group,
            "created_at": self.created_at,
        }


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    course = relationship("Course", back_populates="groups")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "course_id": self.course_id,
        }


class CourseStructureModel(Base):
    __tablename__ = "course_structures"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), unique=True, nullable=False)
    data = Column(JSON, default=dict, nullable=False)

    course = relationship("Course", back_populates="structures")


# -------- discussions --------

class DiscussionComment(Base):
    __tablename__ = "discussion_comments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    subsection_id = Column(Integer, nullable=False)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    author = relationship("User")
    course = relationship("Course", back_populates="discussions")
    replies = relationship("DiscussionReply", back_populates="comment", cascade="all, delete-orphan")


class DiscussionReply(Base):
    __tablename__ = "discussion_replies"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("discussion_comments.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    author = relationship("User")
    comment = relationship("DiscussionComment", back_populates="replies")


# -------- assignments --------

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    subsection_id = Column(Integer, nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    course = relationship("Course", back_populates="assignments")
    creator = relationship("User")
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")
    attachments = relationship("AssignmentAttachment", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=True)
    file_url = Column(String, nullable=True)

    grade = Column(Integer, nullable=True)
    teacher_comment = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "student_id": self.student_id,
            "student_name": self.student.full_name if self.student else "",
            "content": self.content,
            "file_url": self.file_url,
            "grade": self.grade,
            "teacher_comment": self.teacher_comment,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class AssignmentAttachment(Base):
    __tablename__ = "assignment_attachments"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)

    name = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    url = Column(String, nullable=False)

    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    assignment = relationship("Assignment", back_populates="attachments")


# -------- messenger --------

class MessageThread(Base):
    __tablename__ = "message_threads"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    last_message_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    unread_count = Column(Integer, default=0, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)

    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])

    def to_dict(self, current_user_id: int) -> dict:
        partner = self.teacher if current_user_id == self.student_id else self.student
        # аватарки пока нет — отдаём пустую строку (чтобы фронт не падал)
        teacher_avatar = ""
        partner_avatar = ""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "teacher_id": self.teacher_id,
            "student_name": self.student.full_name if self.student else "",
            "teacher_name": self.teacher.full_name if self.teacher else "",
            "teacher_avatar": teacher_avatar,
            "partner_name": partner.full_name if partner else "",
            "partner_avatar": partner_avatar,
            "partner_id": partner.id if partner else 0,
            "last_message_at": self.last_message_at,
            "unread_count": self.unread_count,
            "is_archived": self.is_archived,
        }


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("message_threads.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    thread = relationship("MessageThread")
    sender = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.full_name if self.sender else "",
            "sender_role": self.sender.role if self.sender else UserRole.STUDENT,
            "content": self.content,
            "is_read": self.is_read,
            "created_at": self.created_at,
        }