from datetime import date
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from modules.logging.models.daily_stats_model import DailyStats


def update_daily_stats(db: Session, status_code: int, duration_ms: float, method: str):
    """
    Atomically updates (or creates) the daily record for request metrics.
    """
    today = date.today()

    # Try to find today's stat record
    stats = db.query(DailyStats).filter(DailyStats.stat_date == today).with_for_update().first()

    if not stats:
        # Create new record if one doesn't exist for the day
        stats = DailyStats(
            stat_date=today,
            total_requests=0,
            total_duration_ms=0.0,
            error_count=0,
            count_2xx=0,
            count_3xx=0,
            count_4xx=0,
            count_5xx=0,
            count_get=0,
            count_post=0,
            count_put=0,
            count_delete=0,
            count_patch=0,
        )
        db.add(stats)

    # Increment metrics
    stats.total_requests += 1
    stats.total_duration_ms += duration_ms

    # Track status codes
    if 200 <= status_code < 300:
        stats.count_2xx += 1
    elif 300 <= status_code < 400:
        stats.count_3xx += 1
    elif 400 <= status_code < 500:
        stats.count_4xx += 1
        stats.error_count += 1
    elif 500 <= status_code < 600:
        stats.count_5xx += 1
        stats.error_count += 1

    # Track common HTTP methods
    method_upper = method.upper()
    if method_upper == "GET":
        stats.count_get += 1
    elif method_upper == "POST":
        stats.count_post += 1
    elif method_upper == "PUT":
        stats.count_put += 1
    elif method_upper == "DELETE":
        stats.count_delete += 1
    elif method_upper == "PATCH":
        stats.count_patch += 1

    # The caller manages the commit to group the log entry and stat update
    db.flush()


def get_daily_stats_list(db: Session, limit: int = 30) -> List[DailyStats]:
    """Retrieve the last N days of statistics."""
    return (
        db.query(DailyStats)
        .order_by(DailyStats.stat_date.desc())
        .limit(limit)
        .all()
    )


def get_global_averages(db: Session):
    """Calculate aggregated info across all stats for the dashboard summary."""
    result = db.query(
        func.sum(DailyStats.total_requests).label("total_requests"),
        func.sum(DailyStats.total_duration_ms).label("total_duration"),
        func.sum(DailyStats.error_count).label("total_errors"),
    ).one()

    total_req = result.total_requests or 1
    avg_duration = (result.total_duration or 0) / total_req

    return {
        "total_requests": int(result.total_requests or 0),
        "avg_duration_ms": round(avg_duration, 2),
        "total_errors": int(result.total_errors or 0),
    }
