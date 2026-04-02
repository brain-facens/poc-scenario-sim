"""
Middleware that automatically logs every HTTP request to the `request_logs` table.

Captures:
  • HTTP method, path, query string, client IP
  • Authenticated user (id + email) when available
  • Response status code and error detail
  • Wall-clock duration in milliseconds
"""

import time
import traceback

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from database import SessionLocal
from modules.logging.models.request_log_model import RequestLog
from modules.logging.services.daily_stats_services import update_daily_stats


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Starlette-compatible middleware for request logging."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()

        # Placeholders for error tracking
        error_type: str | None = None
        error_detail: str | None = None
        status_code: int = 500
        response_message: str | None = None
        response: Response | None = None

        try:
            response = await call_next(request)
            status_code = response.status_code

        except Exception as exc:
            # Catch any unhandled exception that slips past FastAPI's own
            # error handlers so we can still log it.
            error_type = type(exc).__name__
            error_detail = traceback.format_exc()
            status_code = 500
            response_message = str(exc)
            raise  # Re-raise so FastAPI returns the 500

        finally:
            duration_ms = (time.perf_counter() - start) * 1000

            # --- Extract user info from request state (set by security dep) ---
            user_id: str | None = None
            user_email: str | None = None

            if hasattr(request.state, "user"):
                user = request.state.user
                user_id = getattr(user, "id", None)
                user_email = getattr(user, "email", None)

            # --- Build the log entry ---
            log_entry = RequestLog(
                method=request.method,
                path=request.url.path,
                query_params=str(request.url.query) if request.url.query else None,
                client_ip=request.client.host if request.client else None,
                user_id=user_id,
                user_email=user_email,
                status_code=status_code,
                response_message=response_message,
                duration_ms=round(duration_ms, 2),
                error_type=error_type,
                error_detail=error_detail,
            )

            # --- Persist (fire-and-forget on its own session) ---
            try:
                db = SessionLocal()
                db.add(log_entry)

                # --- Update daily stats ---
                update_daily_stats(db, status_code, duration_ms, request.method)

                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()

        return response  # type: ignore[return-value]
