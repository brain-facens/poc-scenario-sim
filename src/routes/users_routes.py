from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi import Query

from database import get_db
from schemas.users_schemas import UserCreate, UserRead, Token, UserUpdate
from services.users_services import create_user_service, authenticate_user
from core.security import create_access_token
from core.security import get_current_user
from schemas.users_schemas import UserPaginated
from services.users_services import get_all_users_service, get_user_by_id_service, update_user_service, soft_delete_user_service
from models.users_model import User

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@users_router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(db=db, user_data=user)

@users_router.get("/", response_model=UserPaginated)
def get_users(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user)
):
    return get_all_users_service(db, page=page, limit=limit)

@users_router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: str = Path(..., description="The ID of the user to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_by_id_service(db=db, user_id=user_id)

@users_router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_user_service(db=db, user_id=user_id, update_data=user_update)

@users_router.delete("/{user_id}", response_model=UserRead)
def soft_delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return soft_delete_user_service(db=db, user_id=user_id)