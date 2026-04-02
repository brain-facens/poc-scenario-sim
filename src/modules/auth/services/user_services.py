from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional

from core.security import hash_password, verify_password
from core.pagination import paginate_and_filter
from modules.auth.models.user_model import User
from modules.auth.schemas.user_schemas import UserCreate, UserUpdate


def authenticate_user(db: Session, login_id: str, password: str):
    user = db.query(User).filter(
        or_(User.email == login_id, User.name == login_id)
    ).first()

    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_user_service(db: Session, user_data: UserCreate):
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users_service(db: Session, page: int, limit: int, name: Optional[str] = None, role: Optional[str] = None):
    filters = {"name": name, "role": role}
    return paginate_and_filter(
        db=db,
        model=User,
        page=page,
        limit=limit,
        filters=filters
    )


def get_user_by_id_service(db: Session, user_id: str):
    """Fetches a user by their ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


def update_user_service(db: Session, user_id: str, update_data: UserUpdate):
    db_user = get_user_by_id_service(db, user_id)

    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def soft_delete_user_service(db: Session, user_id: str):
    db_user = get_user_by_id_service(db, user_id)

    db_user.is_active = False

    db.commit()
    db.refresh(db_user)
    return db_user
