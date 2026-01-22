from fastapi import Body, FastAPI, Depends, HTTPException, status, Request, UploadFile, File
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
from models import MessageThread, Message
from schemas import MessageCreate, ThreadResponse, MessageResponse, UnreadCountResponse, TeacherListResponse
from pydantic import BaseModel

from database import engine, get_db, Base
from models import User, Course, Group, UserRole, UserStatus, CourseStructureModel, DiscussionComment, DiscussionReply
from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserUpdateStatus,
    UserListResponse,
    CourseCreate,
    GroupCreate,
    DiscussionCommentCreate,
    DiscussionReplyCreate,
    DiscussionCommentOut,
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

subsection_files: Dict[int, List[SubsectionFileSchema]] = {}

# ---------- служебные события ----------
@app.on_event("startup")
def create_first_admin():
    db = next(get_db())
    try:
        # --- admin ---
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

        # ---------- helpers ----------
        def build_course_structure(course_id: int, course_key: str) -> dict:
            """
            course_key: 'math' | 'prog' | 'web' | 'eng' | 'db' | 'algo'
            subsection_id делаем уникальным на курс через base = course_id * 1000
            """
            base = course_id * 1000

            if course_key == "math":
                return {
                    "sections": [
                        {
                            "id": base + 1,
                            "number": 1,
                            "title": "Введение в матанализ",
                            "subsections": [
                                {"id": base + 101, "icon": "📌", "title": "О курсе и требования", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 102, "icon": "🧭", "title": "Как сдаём ДЗ и тесты", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 2,
                            "number": 2,
                            "title": "Глава 1: Пределы и непрерывность",
                            "subsections": [
                                {"id": base + 201, "icon": "📚", "title": "Материал: пределы, свойства, непрерывность", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 202, "icon": "📝", "title": "Тест: пределы и непрерывность", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 203, "icon": "🧩", "title": "Задание: вычислить пределы (подборка задач)", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 3,
                            "number": 3,
                            "title": "Глава 2: Производная и применение",
                            "subsections": [
                                {"id": base + 301, "icon": "📚", "title": "Материал: производная, правила, касательная", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 302, "icon": "📝", "title": "Тест: производная и графики", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 303, "icon": "🧩", "title": "Задание: экстремумы и исследование функции", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                    ]
                }

            if course_key == "prog":
                return {
                    "sections": [
                        {
                            "id": base + 1,
                            "number": 1,
                            "title": "Введение в программирование (Python)",
                            "subsections": [
                                {"id": base + 101, "icon": "📌", "title": "О курсе и установка окружения", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 102, "icon": "🧰", "title": "Инструменты: Python, IDE, запуск программ", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 2,
                            "number": 2,
                            "title": "Глава 1: Переменные, типы, ветвления",
                            "subsections": [
                                {"id": base + 201, "icon": "📚", "title": "Материал: типы данных, if/else, ввод/вывод", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 202, "icon": "📝", "title": "Тест: основы синтаксиса и ветвления", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 203, "icon": "🧩", "title": "Задание: мини-задачи на if/else", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 3,
                            "number": 3,
                            "title": "Глава 2: Циклы и функции",
                            "subsections": [
                                {"id": base + 301, "icon": "📚", "title": "Материал: for/while, функции, область видимости", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 302, "icon": "📝", "title": "Тест: циклы и функции", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 303, "icon": "🧩", "title": "Задание: генератор простых задач (практика)", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                    ]
                }

            if course_key == "web":
                return {
                    "sections": [
                        {
                            "id": base + 1,
                            "number": 1,
                            "title": "Введение в веб-дизайн",
                            "subsections": [
                                {"id": base + 101, "icon": "📌", "title": "О курсе и принципы UI/UX", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 102, "icon": "🧭", "title": "Структура проекта и критерии оценки", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 2,
                            "number": 2,
                            "title": "Глава 1: HTML и базовая разметка",
                            "subsections": [
                                {"id": base + 201, "icon": "📚", "title": "Материал: семантика, формы, структура страницы", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 202, "icon": "📝", "title": "Тест: HTML-семантика", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 203, "icon": "🧩", "title": "Задание: сверстать страницу профиля", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 3,
                            "number": 3,
                            "title": "Глава 2: CSS и композиция",
                            "subsections": [
                                {"id": base + 301, "icon": "📚", "title": "Материал: flex/grid, адаптив, типографика", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 302, "icon": "📝", "title": "Тест: Flexbox/Grid и адаптивность", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 303, "icon": "🧩", "title": "Задание: адаптивный лендинг", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                    ]
                }

            if course_key == "db":
                return {
                    "sections": [
                        {
                            "id": base + 1,
                            "number": 1,
                            "title": "Введение в базы данных",
                            "subsections": [
                                {"id": base + 101, "icon": "📌", "title": "О курсе и СУБД", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 102, "icon": "🧰", "title": "Установка PostgreSQL / инструменты", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 2,
                            "number": 2,
                            "title": "Глава 1: SQL основы",
                            "subsections": [
                                {"id": base + 201, "icon": "📚", "title": "Материал: SELECT, WHERE, JOIN", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 202, "icon": "📝", "title": "Тест: базовый SQL", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 203, "icon": "🧩", "title": "Задание: запросы к учебной БД", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 3,
                            "number": 3,
                            "title": "Глава 2: Нормализация и проектирование",
                            "subsections": [
                                {"id": base + 301, "icon": "📚", "title": "Материал: 1НФ–3НФ, связи, ключи", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 302, "icon": "📝", "title": "Тест: нормальные формы", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 303, "icon": "🧩", "title": "Задание: спроектировать схему (ER)", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                    ]
                }

            if course_key == "algo":
                return {
                    "sections": [
                        {
                            "id": base + 1,
                            "number": 1,
                            "title": "Введение в алгоритмы",
                            "subsections": [
                                {"id": base + 101, "icon": "📌", "title": "О курсе и сложность алгоритмов", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 102, "icon": "🧭", "title": "Big-O нотация (база)", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 2,
                            "number": 2,
                            "title": "Глава 1: Массивы, списки, стек, очередь",
                            "subsections": [
                                {"id": base + 201, "icon": "📚", "title": "Материал: структуры данных (обзор)", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 202, "icon": "📝", "title": "Тест: базовые структуры данных", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 203, "icon": "🧩", "title": "Задание: реализовать стек/очередь", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                        {
                            "id": base + 3,
                            "number": 3,
                            "title": "Глава 2: Сортировки и поиск",
                            "subsections": [
                                {"id": base + 301, "icon": "📚", "title": "Материал: сортировки O(n^2) и O(n log n)", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 302, "icon": "📝", "title": "Тест: сортировки", "status": "open", "statusIcon": "✅", "files": []},
                                {"id": base + 303, "icon": "🧩", "title": "Задание: бинарный поиск + сортировка", "status": "open", "statusIcon": "✅", "files": []},
                            ],
                        },
                    ]
                }

            # eng (default)
            return {
                "sections": [
                    {
                        "id": base + 1,
                        "number": 1,
                        "title": "Введение (English for IT)",
                        "subsections": [
                            {"id": base + 101, "icon": "📌", "title": "О курсе и цели обучения", "status": "open", "statusIcon": "✅", "files": []},
                            {"id": base + 102, "icon": "🗂️", "title": "Словарь курса и полезные ресурсы", "status": "open", "statusIcon": "✅", "files": []},
                        ],
                    },
                    {
                        "id": base + 2,
                        "number": 2,
                        "title": "Глава 1: Деловая переписка",
                        "subsections": [
                            {"id": base + 201, "icon": "📚", "title": "Материал: структура письма, tone, etiquette", "status": "open", "statusIcon": "✅", "files": []},
                            {"id": base + 202, "icon": "📝", "title": "Тест: business email basics", "status": "open", "statusIcon": "✅", "files": []},
                            {"id": base + 203, "icon": "✉️", "title": "Задание: написать письмо заказчику (шаблон)", "status": "open", "statusIcon": "✅", "files": []},
                        ],
                    },
                    {
                        "id": base + 3,
                        "number": 3,
                        "title": "Глава 2: Собеседование и презентации",
                        "subsections": [
                            {"id": base + 301, "icon": "📚", "title": "Материал: self-intro, strengths, projects", "status": "open", "statusIcon": "✅", "files": []},
                            {"id": base + 302, "icon": "📝", "title": "Тест: interview questions (B1–B2)", "status": "open", "statusIcon": "✅", "files": []},
                            {"id": base + 303, "icon": "🎤", "title": "Задание: короткая презентация проекта на англ.", "status": "open", "statusIcon": "✅", "files": []},
                        ],
                    },
                ]
            }

        def ensure_course_with_structure(name: str, description: str, course_key: str):
            # 1) курс
            course = db.query(Course).filter(Course.name == name).first()
            if not course:
                course = Course(name=name, description=description)
                db.add(course)
                db.commit()
                db.refresh(course)
                print(f"✅ Создан курс: {name}")

            # 2) структура
            exists_structure = (
                db.query(CourseStructureModel)
                .filter(CourseStructureModel.course_id == course.id)
                .first()
            )
            if not exists_structure:
                cs = CourseStructureModel(
                    course_id=course.id,
                    data=build_course_structure(course.id, course_key),
                )
                db.add(cs)
                db.commit()
                print(f"✅ Создана структура курса: {name}")

        seed_courses = [
            ("Математический анализ", "Основы математического анализа: пределы, производные и их применение.", "math"),
            ("Основы программирования", "Введение в программирование на Python: базовый синтаксис, ветвления, циклы, функции.", "prog"),
            ("Веб-дизайн", "Создание современных веб-интерфейсов: HTML, CSS, адаптивная верстка.", "web"),
            ("Английский язык", "Деловой английский для IT: переписка, интервью и презентации.", "eng"),
            ("Базы данных", "Проектирование и работа с БД: SQL, нормализация, проектирование схем.", "db"),
            ("Алгоритмы и структуры данных", "Базовые структуры данных и алгоритмы: сложность, сортировки, поиск.", "algo"),
        ]

        for name, desc, key in seed_courses:
            ensure_course_with_structure(name, desc, key)

    except Exception as e:

        print("❌ Ошибка на startup (seed/admin):", repr(e))
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

# ---------- discussions ----------
@app.get("/api/discussions", response_model=List[DiscussionCommentOut])
def get_discussions(
    course_id: int,
    subsection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(DiscussionComment)
        .filter(DiscussionComment.course_id == course_id)
        .filter(DiscussionComment.subsection_id == subsection_id)
        .order_by(DiscussionComment.created_at.asc())
        .all()
    )

    result = []
    for c in items:
        replies = []
        for r in c.replies:
            replies.append(
                {
                    "id": r.id,
                    "author_name": r.author.full_name if r.author else "",
                    "author_role": r.author.role if r.author else UserRole.STUDENT,
                    "content": r.content,
                    "created_at": r.created_at,
                }
            )

        result.append(
            {
                "id": c.id,
                "author_name": c.author.full_name if c.author else "",
                "author_role": c.author.role if c.author else UserRole.STUDENT,
                "content": c.content,
                "created_at": c.created_at,
                "replies": replies,
            }
        )

    return result


@app.post("/api/discussions", response_model=DiscussionCommentOut)
def create_discussion_comment(
    payload: DiscussionCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = DiscussionComment(
        course_id=payload.course_id,
        subsection_id=payload.subsection_id,
        author_id=current_user.id,
        content=payload.content.strip(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "author_name": current_user.full_name,
        "author_role": current_user.role,
        "content": comment.content,
        "created_at": comment.created_at,
        "replies": [],
    }


@app.post("/api/discussions/{comment_id}/replies")
def create_discussion_reply(
    comment_id: int,
    payload: DiscussionReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(DiscussionComment).filter(DiscussionComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    reply = DiscussionReply(
        comment_id=comment_id,
        author_id=current_user.id,
        content=payload.content.strip(),
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    return {
        "id": reply.id,
        "author_name": current_user.full_name,
        "author_role": current_user.role,
        "content": reply.content,
        "created_at": reply.created_at,
    }

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

# main.py - добавить в правильное место (после других эндпоинтов)

# ---------- MESSENGER ----------

@app.get("/api/messenger/threads", response_model=List[ThreadResponse])
def get_message_threads(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_account_confirmation()),
):
    """Получить все диалоги текущего пользователя"""
    if current_user.role == UserRole.STUDENT:
        threads = (
            db.query(MessageThread)
            .filter(MessageThread.student_id == current_user.id)
            .filter(MessageThread.is_archived == False)
            .order_by(MessageThread.last_message_at.desc())
            .all()
        )
    else:
        threads = (
            db.query(MessageThread)
            .filter(MessageThread.teacher_id == current_user.id)
            .filter(MessageThread.is_archived == False)
            .order_by(MessageThread.last_message_at.desc())
            .all()
        )
    
    result = []
    for thread in threads:
        thread_dict = thread.to_dict()
        # Получаем последнее сообщение
        last_message = (
            db.query(Message)
            .filter(Message.thread_id == thread.id)
            .order_by(Message.created_at.desc())
            .first()
        )
        if last_message:
            thread_dict["last_message"] = last_message.to_dict()
        result.append(thread_dict)
    
    return result


@app.get("/api/messenger/teachers", response_model=TeacherListResponse)
def get_available_teachers(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_account_confirmation()),
):
    """Получить список всех преподавателей"""
    query = db.query(User).filter(User.role.in_([UserRole.TEACHER, UserRole.DEPARTMENT_HEAD, UserRole.ADMIN]))
    
    if search:
        query = query.filter(User.full_name.ilike(f"%{search}%"))
    
    total = query.count()
    teachers = query.offset((page - 1) * limit).limit(limit).all()
    
    return TeacherListResponse(
        teachers=[teacher.to_dict() for teacher in teachers],
        total=total
    )


@app.get("/api/messenger/threads/{thread_id}/messages", response_model=List[MessageResponse])
def get_thread_messages(
    thread_id: int,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить сообщения диалога"""
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    
    # Проверка доступа
    if current_user.role == UserRole.STUDENT and thread.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому диалогу")
    elif current_user.role != UserRole.STUDENT and thread.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому диалогу")
    
    # Помечаем сообщения как прочитанные
    unread_messages = (
        db.query(Message)
        .filter(Message.thread_id == thread_id)
        .filter(Message.is_read == False)
        .filter(Message.sender_id != current_user.id)
        .all()
    )
    
    for msg in unread_messages:
        msg.is_read = True
    
    # Обновляем счетчик непрочитанных
    thread.unread_count = 0
    db.commit()
    
    # Получаем сообщения
    messages = (
        db.query(Message)
        .filter(Message.thread_id == thread_id)
        .order_by(Message.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    
    return [msg.to_dict() for msg in reversed(messages)]


@app.post("/api/messenger/messages", response_model=MessageResponse)
def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отправить сообщение преподавателю"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только студенты могут начинать диалоги"
        )
    
    # Проверяем, существует ли преподаватель
    teacher = db.query(User).filter(
        User.id == message_data.teacher_id,
        User.role.in_([UserRole.TEACHER, UserRole.DEPARTMENT_HEAD, UserRole.ADMIN])
    ).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    
    # Находим или создаем диалог
    thread = db.query(MessageThread).filter(
        MessageThread.student_id == current_user.id,
        MessageThread.teacher_id == teacher.id
    ).first()
    
    if not thread:
        thread = MessageThread(
            student_id=current_user.id,
            teacher_id=teacher.id
        )
        db.add(thread)
        db.commit()
        db.refresh(thread)
    
    # Создаем сообщение
    message = Message(
        thread_id=thread.id,
        sender_id=current_user.id,
        content=message_data.content.strip()
    )
    db.add(message)
    
    # Обновляем время последнего сообщения и счетчик непрочитанных
    thread.last_message_at = datetime.utcnow()
    thread.unread_count += 1
    
    db.commit()
    db.refresh(message)
    
    return message.to_dict()


@app.post("/api/messenger/messages/{thread_id}/reply", response_model=MessageResponse)
def reply_to_thread(
    thread_id: int,
    request: dict = Body(...),  # Принимаем JSON объект
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ответить в существующем диалоге"""
    
    # Извлекаем content из запроса
    content = request.get("content") if isinstance(request, dict) else None
    
    if not content:
        # Попробуем получить как строку
        content = request if isinstance(request, str) else None
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Сообщение не может быть пустым"
        )
    
    # Проверяем существование диалога
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    
    # Проверка доступа
    if current_user.role == UserRole.STUDENT:
        if thread.student_id != current_user.id:
            raise HTTPException(status_code=403, detail="Нет доступа к этому диалогу")
    else:
        if thread.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Нет доступа к этому диалогу")
    
    # Создаем сообщение
    message = Message(
        thread_id=thread.id,
        sender_id=current_user.id,
        content=content.strip()
    )
    db.add(message)
    
    # Обновляем время последнего сообщения и счетчик непрочитанных
    thread.last_message_at = datetime.utcnow()
    thread.unread_count += 1
    
    db.commit()
    db.refresh(message)
    
    return message.to_dict()


@app.get("/api/messenger/unread-count", response_model=UnreadCountResponse)
def get_unread_message_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить количество непрочитанных сообщений"""
    if current_user.role == UserRole.STUDENT:
        threads = db.query(MessageThread).filter(
            MessageThread.student_id == current_user.id,
            MessageThread.is_archived == False
        ).all()
    else:
        threads = db.query(MessageThread).filter(
            MessageThread.teacher_id == current_user.id,
            MessageThread.is_archived == False
        ).all()
    
    total_unread = sum(thread.unread_count for thread in threads)
    thread_unread_counts = {thread.id: thread.unread_count for thread in threads}
    
    return UnreadCountResponse(
        total_unread=total_unread,
        thread_unread_counts=thread_unread_counts
    )


@app.post("/api/messenger/threads/{thread_id}/read")
def mark_thread_as_read(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Пометить все сообщения в диалоге как прочитанные"""
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    
    # Проверка доступа
    if current_user.role == UserRole.STUDENT and thread.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому диалогу")
    elif current_user.role != UserRole.STUDENT and thread.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому диалогу")
    
    # Помечаем все сообщения как прочитанные
    unread_messages = (
        db.query(Message)
        .filter(Message.thread_id == thread_id)
        .filter(Message.is_read == False)
        .filter(Message.sender_id != current_user.id)
        .all()
    )
    
    for msg in unread_messages:
        msg.is_read = True
    
    # Сбрасываем счетчик непрочитанных
    thread.unread_count = 0
    db.commit()
    
    return {"success": True, "message": "Все сообщения отмечены как прочитанные"}


@app.post("/api/messenger/threads/{thread_id}/archive")
def archive_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Архивировать диалог"""
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    
    # Проверка доступа
    if current_user.role == UserRole.STUDENT and thread.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому диалогу")
    elif current_user.role != UserRole.STUDENT and thread.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому диалогу")
    
    thread.is_archived = True
    db.commit()
    
    return {"success": True, "message": "Диалог архивирован"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
