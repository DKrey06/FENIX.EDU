from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uvicorn

from database import engine, get_db, Base
from models import User, Course, Group, UserRole, UserStatus
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
    require_admin,
    require_department_head,
    require_account_confirmation,
)

# схема авторизации для извлечения токена из заголовка Authorization
security = HTTPBearer()

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FENIX.EDU API",
    description="API для образовательной платформы FENIX.EDU",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Создание первого администратора при запуске
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
    finally:
        db.close()


# Регистрация пользователя
# В функции register в main.py добавьте проверку email:
@app.post("/api/auth/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Простая проверка email
    if '@' not in user_data.email or '.' not in user_data.email.split('@')[-1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный формат email",
        )
    
    # Проверка пароля
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать минимум 6 символов",
        )
    
    # Проверка полей для студентов
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
    
    # Проверка существующего пользователя
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    # Создание пользователя
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

    # Создание токенов
    access_token = create_access_token({"user_id": user.id, "email": user.email})
    refresh_token = create_refresh_token({"user_id": user.id, "email": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user.to_dict(),
    )


# Вход в систему
@app.post("/api/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    # Проверка статуса аккаунта
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт не подтвержден администратором",
        )

    # Создание токенов
    access_token = create_access_token({"user_id": user.id, "email": user.email})
    refresh_token = create_refresh_token({"user_id": user.id, "email": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user.to_dict(),
    )


# Обновление токенов
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


# Выход из системы (упрощенная версия без Redis)
@app.post("/api/auth/logout")
def logout():
    # В упрощенной версии просто сообщаем клиенту, что выход выполнен
    # Клиент должен удалить токены на своей стороне
    return {"success": True, "message": "Успешный выход из системы"}


# Получение текущего пользователя
@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()


# Управление пользователями (для администраторов)
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


# Подтверждение/отклонение пользователей
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

    # Обновление статуса
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


# Управление курсами
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
    current_user: User = Depends(require_account_confirmation),
):
    courses = db.query(Course).all()
    return [course.to_dict() for course in courses]


# Управление группами
@app.post("/api/groups", response_model=dict)
def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(require_department_head),
    db: Session = Depends(get_db),
):
    # Проверка существования курса
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
    current_user: User = Depends(require_account_confirmation),
):
    query = db.query(Group)

    if course_id:
        query = query.filter(Group.course_id == course_id)

    groups = query.all()
    return [group.to_dict() for group in groups]


# Middleware для обработки ошибок
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)