import uuid

from sqlalchemy import Column, Float, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))

    # --- Request info ---
    method = Column(String(10), nullable=False, index=True)          # GET, POST, PATCH, DELETE …
    path = Column(String(512), nullable=False, index=True)           # /users/me/
    query_params = Column(Text, nullable=True)                       # raw query string
    client_ip = Column(String(45), nullable=True)                    # IPv4 / IPv6

    # --- User info (populated when the request is authenticated) ---
    user_id = Column(String(36), nullable=True, index=True)
    user_email = Column(String, nullable=True)

    # --- Response info ---
    status_code = Column(Integer, nullable=False, index=True)
    response_message = Column(Text, nullable=True)                   # short detail for non-200 responses

    # --- Performance ---
    duration_ms = Column(Float, nullable=False)                      # processing time in milliseconds

    # --- Error info ---
    error_type = Column(String(256), nullable=True, index=True)      # e.g. "ValueError", "HTTPException"
    error_detail = Column(Text, nullable=True)                       # full traceback / detail string

    # --- Timestamps ---
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
