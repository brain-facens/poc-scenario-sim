from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.pagination import PaginatedResponse
from core.security import get_current_user
from database import get_db
from modules.auth.models.user_model import User
from modules.logging.schemas.request_log_schemas import RequestLogRead
from modules.logging.schemas.daily_stats_schemas import DailyStatsRead, GlobalAveragesRead
from modules.logging.services.request_log_services import get_request_logs_service
from modules.logging.services.daily_stats_services import get_daily_stats_list, get_global_averages

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


@logs_router.get("/stats/daily", response_model=list[DailyStatsRead])
def get_daily_stats(
    db: Session = Depends(get_db),
    limit: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    current_user: User = Depends(get_current_user),
):
    """Retrieve daily request statistics for trends."""
    return get_daily_stats_list(db, limit=limit)


@logs_router.get("/stats/summary", response_model=GlobalAveragesRead)
def get_stats_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve global summary of all time stats."""
    return get_global_averages(db)
