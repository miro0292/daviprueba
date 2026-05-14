import logging
import json
from datetime import datetime, timezone
from app.config import settings


class StructuredLogger:
    def __init__(self, service: str = settings.service_name):
        self.service = service
        self.logger = logging.getLogger(service)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    def _build_entry(self, level: str, operation: str, message: str, **kwargs) -> dict:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "service": self.service,
            "traceId": kwargs.get("trace_id", "-"),
            "sessionId": self._mask(kwargs.get("session_id")),
            "operation": operation,
            "message": message,
            "status": kwargs.get("status", ""),
            "durationMs": kwargs.get("duration_ms"),
            "httpStatus": kwargs.get("http_status"),
            "errorCode": kwargs.get("error_code"),
        }
        return {k: v for k, v in entry.items() if v is not None or k in ("traceId", "sessionId")}

    def _mask(self, value: str | None) -> str:
        if not value:
            return "-"
        return value[:4] + "***"

    def info(self, operation: str, message: str, **kwargs):
        self.logger.info(json.dumps(self._build_entry("INFO", operation, message, **kwargs)))

    def error(self, operation: str, message: str, **kwargs):
        self.logger.error(json.dumps(self._build_entry("ERROR", operation, message, **kwargs)))

    def warning(self, operation: str, message: str, **kwargs):
        self.logger.warning(json.dumps(self._build_entry("WARNING", operation, message, **kwargs)))


logger = StructuredLogger()
