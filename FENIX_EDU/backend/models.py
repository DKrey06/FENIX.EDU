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

    # Поля для студентов
    course = Column(String, nullable=True)
    group = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Отношения
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
    # храним всю структуру (sections / subsections / files) как JSON
    data = Column(JSON, nullable=False)

    course = relationship("Course", backref="structure")
