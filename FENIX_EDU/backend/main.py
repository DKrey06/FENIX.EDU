from fastapi import FastAPI, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import uvicorn
import os

from pydantic import BaseModel

from database import engine, get_db, Base
from models import User, Course, Group, UserRole, UserStatus, CourseStructureModel
from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserUpdateStatus,
    UserListResponse,
    CourseCreate,
    GroupCreate,
)
from settings import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    refresh_access_token,
)
from dependencies import (
    get_current_user,
    get_current_user_for_waiting,
    require_admin,
    require_department_head,
    require_teacher,
    require_account_confirmation,
)

security = HTTPBearer()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FENIX.EDU API",
    description="API для образовательной платформы FENIX.EDU",
    version="1.0.0",
)

# ---------- настройки загрузки и статики ----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DEFAULT_COURSE_NAME = "Первый курс"
DEFAULT_COURSE_DESCRIPTION = "Курс создаётся автоматически при первом запуске."

# ---------- Pydantic-схемы для структуры курса ----------


class SubsectionFileSchema(BaseModel):
    id: Optional[int] = None
    name: str
    size: int
    url: Optional[str] = None  # путь до файла, например /uploads/123456.jpg


class SubsectionSchema(BaseModel):
    id: Optional[int] = None
    icon: str
    title: str
    status: str
    statusIcon: str
    files: List[SubsectionFileSchema] = []


class SectionSchema(BaseModel):
    id: Optional[int] = None
    number: int
    title: str
    subsections: List[SubsectionSchema]


class CourseStructureSchema(BaseModel):
    sections: List[SectionSchema]


# хранилище файлов (пока в памяти — только связь subsection_id -> файлы)
subsection_files: Dict[int, List[SubsectionFileSchema]] = {}

# ---------- служебные события ----------


@app.on_event("startup")
def create_first_admin():
    db = next(get_db())
    try:
        admin = db.query(User).filter(User.email == "admin@fenixedu.ru").first()
        if not admin:
            admin_user = User(
                full_name="Администратор системы",
                email="admin@fenixedu.ru",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                confirmed_at=datetime.utcnow(),
            )
            db.add(admin_user)
            db.commit()
            print("✅ Создан первый администратор: admin@fenixedu.ru / admin123")

        course = db.query(Course).filter(Course.name == DEFAULT_COURSE_NAME).first()
        if not course:
            course = Course(
                name=DEFAULT_COURSE_NAME,
                description=DEFAULT_COURSE_DESCRIPTION,
            )
            db.add(course)
            db.commit()
            print(f"✅ Создан стартовый курс: {DEFAULT_COURSE_NAME}")
    finally:
        db.close()



# ---------- auth ----------


@app.post("/api/auth/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if "@" not in user_data.email or "." not in user_data.email.split("@")[-1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный формат email",
        )

    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать минимум 6 символов",
        )

    if user_data.role == UserRole.STUDENT:
        if not user_data.course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для студента необходимо указать курс",
            )
        if not user_data.group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для студента необходимо указать группу",
            )

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        course=user_data.course if user_data.role == UserRole.STUDENT else None,
        group=user_data.group if user_data.role == UserRole.STUDENT else None,
        status=UserStatus.PENDING,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"user_id": user.id, "email": user.email})
    refresh_token = create_refresh_token({"user_id": user.id, "email": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user.to_dict(),
    )


@app.post("/api/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт не подтвержден администратором",
        )

    access_token = create_access_token({"user_id": user.id, "email": user.email})
    refresh_token = create_refresh_token({"user_id": user.id, "email": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user.to_dict(),
    )


@app.post("/api/auth/refresh", response_model=TokenResponse)
def refresh_token_endpoint(data: dict):
    refresh_token_value = data.get("refresh_token")
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token обязателен",
        )

    tokens = refresh_access_token(refresh_token_value)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh token",
        )

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@app.post("/api/auth/logout")
def logout():
    return {"success": True, "message": "Успешный выход из системы"}


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

# ---------- admin users ----------


@app.get("/api/admin/users", response_model=UserListResponse)
def get_all_users(
    status: Optional[UserStatus] = None,
    role: Optional[UserRole] = None,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User)

    if status:
        query = query.filter(User.status == status)
    if role:
        query = query.filter(User.role == role)

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()

    return UserListResponse(
        users=[user.to_dict() for user in users],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
    )


@app.put("/api/admin/users/{user_id}/status")
def update_user_status(
    user_id: int,
    status_data: UserUpdateStatus,
    current_user: User = Depends(require_department_head),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    user.status = status_data.status

    if status_data.status == UserStatus.ACTIVE:
        user.confirmed_at = datetime.utcnow()
        user.confirmed_by = current_user.id

    db.commit()

    return {
        "success": True,
        "message": f"Статус пользователя обновлен на {status_data.status}",
        "user": user.to_dict(),
    }

# ---------- courses & groups ----------


@app.post("/api/courses", response_model=dict)
def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(require_department_head),
    db: Session = Depends(get_db),
):
    course = Course(
        name=course_data.name,
        description=course_data.description,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    return {
        "success": True,
        "message": "Курс создан",
        "course": course.to_dict(),
    }


@app.get("/api/courses", response_model=List[dict])
def get_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_account_confirmation()),
):
    courses = db.query(Course).all()
    return [course.to_dict() for course in courses]


@app.post("/api/courses/{course_id}/structure", response_model=dict)
def create_course_structure(
    course_id: int,
    structure: CourseStructureSchema,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    existing = (
        db.query(CourseStructureModel)
        .filter(CourseStructureModel.course_id == course_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Структура для этого курса уже создана",
        )

    data = jsonable_encoder(structure)
    cs = CourseStructureModel(course_id=course_id, data=data)
    db.add(cs)
    db.commit()

    return {"success": True}


@app.put("/api/courses/{course_id}/structure", response_model=dict)
def update_course_structure(
    course_id: int,
    structure: CourseStructureSchema,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    cs = (
        db.query(CourseStructureModel)
        .filter(CourseStructureModel.course_id == course_id)
        .first()
    )
    if not cs:
        cs = CourseStructureModel(course_id=course_id, data={})
        db.add(cs)
        db.flush()

    # подставляем уже загруженные файлы по subsection_id
    for section in structure.sections:
        for subsection in section.subsections:
            if subsection.id is not None and subsection.id in subsection_files:
                subsection.files = subsection_files[subsection.id]

    cs.data = jsonable_encoder(structure)
    db.commit()

    return {"success": True}


@app.get("/api/courses/{course_id}/structure", response_model=CourseStructureSchema)
def get_course_structure(
    course_id: int,
    current_user: User = Depends(require_account_confirmation()),
    db: Session = Depends(get_db),
):
    cs = (
        db.query(CourseStructureModel)
        .filter(CourseStructureModel.course_id == course_id)
        .first()
    )
    if not cs:
        return CourseStructureSchema(sections=[])

    return CourseStructureSchema(**cs.data)


@app.post("/api/groups", response_model=dict)
def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(require_department_head),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == group_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Курс не найден",
        )

    group = Group(
        name=group_data.name,
        course_id=group_data.course_id,
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    return {
        "success": True,
        "message": "Группа создана",
        "group": group.to_dict(),
    }


@app.get("/api/groups", response_model=List[dict])
def get_groups(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_account_confirmation()),
):
    query = db.query(Group)

    if course_id:
        query = query.filter(Group.course_id == course_id)

    groups = query.all()
    return [group.to_dict() for group in groups]

# ---------- файлы подразделов ----------


@app.post(
    "/api/subsections/{subsection_id}/files",
    response_model=List[SubsectionFileSchema],
)
async def upload_subsection_files(
    subsection_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_teacher),
):
    saved_files: List[SubsectionFileSchema] = []

    for f in files:
        file_id = int(datetime.utcnow().timestamp() * 1000)
        ext = os.path.splitext(f.filename)[1]
        safe_name = f"{file_id}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        content = await f.read()
        with open(file_path, "wb") as out:
            out.write(content)

        size = len(content)

        file_schema = SubsectionFileSchema(
            id=file_id,
            name=f.filename,
            size=size,
            url=f"/uploads/{safe_name}",
        )
        saved_files.append(file_schema)

    if subsection_id not in subsection_files:
        subsection_files[subsection_id] = []
    subsection_files[subsection_id].extend(saved_files)

    return saved_files


@app.delete(
    "/api/subsections/{subsection_id}/files/{file_id}",
    response_model=dict,
)
def delete_subsection_file(
    subsection_id: int,
    file_id: int,
    current_user: User = Depends(require_teacher),
):
    if subsection_id not in subsection_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файлы для данного подраздела не найдены",
        )

    files = subsection_files[subsection_id]
    new_files = [f for f in files if f.id != file_id]
    if len(new_files) == len(files):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден",
        )

    subsection_files[subsection_id] = new_files
    return {"success": True}

# ---------- прочее ----------


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.get("/api/admin/pending-users", response_model=UserListResponse)
def get_pending_users(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User).filter(User.status == UserStatus.PENDING)

    total = query.count()
    users = query.offset((page - 1) * limit).limit(limit).all()

    return UserListResponse(
        users=[user.to_dict() for user in users],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
    )


@app.post("/api/admin/users/{user_id}/approve")
def approve_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь уже имеет статус: {user.status}",
        )

    user.status = UserStatus.ACTIVE
    user.confirmed_at = datetime.utcnow()
    user.confirmed_by = current_user.id

    db.commit()

    return {
        "success": True,
        "message": f"Пользователь {user.email} подтвержден",
        "user": user.to_dict(),
    }


@app.post("/api/admin/users/{user_id}/reject")
def reject_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь уже имеет статус: {user.status}",
        )

    user.status = UserStatus.REJECTED
    user.confirmed_by = current_user.id

    db.commit()

    return {
        "success": True,
        "message": f"Пользователь {user.email} отклонен",
        "user": user.to_dict(),
    }


@app.get("/api/auth/check-status")
def check_account_status(
    current_user: User = Depends(get_current_user_for_waiting),
):
    return {
        "status": current_user.status,
        "message": get_status_message(current_user.status),
        "user": current_user.to_dict(),
    }


def get_status_message(status: UserStatus) -> str:
    messages = {
        UserStatus.PENDING: "Ваш аккаунт ожидает подтверждения администратором.",
        UserStatus.ACTIVE: "Ваш аккаунт активен.",
        UserStatus.REJECTED: "Ваш аккаунт был отклонен администратором.",
        UserStatus.BLOCKED: "Ваш аккаунт заблокирован.",
    }
    return messages.get(status, "Неизвестный статус.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
