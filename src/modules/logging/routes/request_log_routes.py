from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.pagination import PaginatedResponse
from core.security import get_current_user
from database import get_db
from modules.auth.models.user_model import User
from modules.logging.schemas.request_log_schemas import RequestLogRead
from modules.logging.services.request_log_services import get_request_logs_service

logs_router = APIRouter(prefix="/logs", tags=["logs"])


@logs_router.get("/requests", response_model=PaginatedResponse[RequestLogRead])
def get_request_logs(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    method: Optional[str] = Query(None, description="Filter by HTTP method (GET, POST, …)"),
    path: Optional[str] = Query(None, description="Filter by endpoint path"),
    status_code: Optional[int] = Query(None, description="Filter by response status code"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    user_email: Optional[str] = Query(None, description="Filter by user email"),
    error_type: Optional[str] = Query(None, description="Filter by error type"),
    client_ip: Optional[str] = Query(None, description="Filter by client IP"),
    current_user: User = Depends(get_current_user),
):
    return get_request_logs_service(
        db=db,
        page=page,
        limit=limit,
        method=method,
        path=path,
        status_code=status_code,
        user_id=user_id,
        user_email=user_email,
        error_type=error_type,
        client_ip=client_ip,
    )
