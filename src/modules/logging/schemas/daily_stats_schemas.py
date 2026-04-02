from datetime import date
from pydantic import BaseModel
from typing import List


class DailyStatsRead(BaseModel):
    stat_date: date
    total_requests: int
    total_duration_ms: float
    error_count: int
    count_2xx: int
    count_3xx: int
    count_4xx: int
    count_5xx: int
    count_get: int
    count_post: int
    count_put: int
    count_delete: int
    count_patch: int

    class Config:
        from_attributes = True


class GlobalAveragesRead(BaseModel):
    total_requests: int
    avg_duration_ms: float
    total_errors: int
