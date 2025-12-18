from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from settings import decode_token
from database import get_db
from models import User, UserRole, UserStatus
import redis
import json


security = HTTPBearer()

# Подключение к Redis для хранения токенов (опционально)
redis_client = redis.Redis(host='localhost', port=6379, db=0)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )

    # Проверка статуса аккаунта
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт не подтвержден или заблокирован",
        )

    # Проверка в blacklist (если используем Redis)
    if redis_client.get(f"blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен заблокирован",
        )

    return user


def require_role(required_roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return current_user

    return role_checker


# Проверки для конкретных ролей
require_admin = require_role([UserRole.ADMIN])
require_department_head = require_role([UserRole.ADMIN, UserRole.DEPARTMENT_HEAD])
require_teacher = require_role([UserRole.ADMIN, UserRole.DEPARTMENT_HEAD, UserRole.TEACHER])
require_student = require_role([UserRole.ADMIN, UserRole.DEPARTMENT_HEAD, UserRole.TEACHER, UserRole.STUDENT])


def require_account_confirmation():
    def confirmation_checker(current_user: User = Depends(get_current_user)):
        if current_user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Требуется подтверждение аккаунта администратором",
            )
        return current_user

    return confirmation_checker
