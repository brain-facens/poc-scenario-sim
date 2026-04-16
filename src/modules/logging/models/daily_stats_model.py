from sqlalchemy import Column, Integer, Float, Date
from database import Base


class DailyStats(Base):
    __tablename__ = "daily_stats"

    stat_date = Column(Date, primary_key=True)
    total_requests = Column(Integer, default=0, nullable=False)
    total_duration_ms = Column(Float, default=0.0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)  # 4xx and 5xx

    # Status code ranges
    count_2xx = Column(Integer, default=0, nullable=False)
    count_3xx = Column(Integer, default=0, nullable=False)
    count_4xx = Column(Integer, default=0, nullable=False)
    count_5xx = Column(Integer, default=0, nullable=False)

    # Method counts
    count_get = Column(Integer, default=0, nullable=False)
    count_post = Column(Integer, default=0, nullable=False)
    count_put = Column(Integer, default=0, nullable=False)
    count_delete = Column(Integer, default=0, nullable=False)
    count_patch = Column(Integer, default=0, nullable=False)
