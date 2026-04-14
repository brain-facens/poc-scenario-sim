from datetime import datetime
from sqlalchemy import func, case
from database import SessionLocal
from modules.logging.models.request_log_model import RequestLog
from modules.logging.models.daily_stats_model import DailyStats


def backfill_daily_stats():
    """Populates daily_stats table from existing request_logs."""
    db = SessionLocal()
    try:
        # Group logs by date
        stats_query = (
            db.query(
                func.date(RequestLog.created_at).label("log_date"),
                func.count(RequestLog.id).label("total_requests"),
                func.sum(RequestLog.duration_ms).label("total_duration"),
                func.sum(
                    case((RequestLog.status_code >= 400, 1), else_=0)
                ).label("error_count"),
                func.sum(
                    case(((RequestLog.status_code >= 200) & (RequestLog.status_code < 300), 1), else_=0)
                ).label("count_2xx"),
                func.sum(
                    case(((RequestLog.status_code >= 300) & (RequestLog.status_code < 400), 1), else_=0)
                ).label("count_3xx"),
                func.sum(
                    case(((RequestLog.status_code >= 400) & (RequestLog.status_code < 500), 1), else_=0)
                ).label("count_4xx"),
                func.sum(
                    case((RequestLog.status_code >= 500, 1), else_=0)
                ).label("count_5xx"),
            )
            .group_by(func.date(RequestLog.created_at))
            .all()
        )

        for s in stats_query:
            if not s.log_date:
                continue

            stat_date = datetime.strptime(s.log_date, "%Y-%m-%d").date()

            # Check if exists
            daily = db.query(DailyStats).filter(DailyStats.stat_date == stat_date).first()
            if not daily:
                daily = DailyStats(stat_date=stat_date)
                db.add(daily)

            daily.total_requests = s.total_requests
            daily.total_duration_ms = float(s.total_duration or 0.0)
            daily.error_count = int(s.error_count or 0)
            daily.count_2xx = int(s.count_2xx or 0)
            daily.count_3xx = int(s.count_3xx or 0)
            daily.count_4xx = int(s.count_4xx or 0)
            daily.count_5xx = int(s.count_5xx or 0)

        db.commit()
        print(f"Successfully backfilled stats for {len(stats_query)} days.")

    except Exception as e:
        db.rollback()
        print(f"Error backfilling stats: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    backfill_daily_stats()
