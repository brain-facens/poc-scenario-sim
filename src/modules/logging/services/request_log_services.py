from typing import Optional

from sqlalchemy.orm import Session

from core.pagination import paginate_and_filter
from modules.logging.models.request_log_model import RequestLog


def get_request_logs_service(
    db: Session,
    page: int,
    limit: int,
    method: Optional[str] = None,
    path: Optional[str] = None,
    status_code: Optional[int] = None,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    error_type: Optional[str] = None,
    client_ip: Optional[str] = None,
):
    filters = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "user_id": user_id,
        "user_email": user_email,
        "error_type": error_type,
        "client_ip": client_ip,
    }

    return paginate_and_filter(
        db=db,
        model=RequestLog,
        page=page,
        limit=limit,
        filters=filters,
        default_order_by=RequestLog.created_at.desc(),
    )
