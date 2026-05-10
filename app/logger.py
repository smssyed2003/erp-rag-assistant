import logging
import sys
import json
import uuid
from datetime import datetime
from contextvars import ContextVar
from typing import Optional, Any, Dict

# Context variable for tracking correlation IDs across async contexts
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelationIDFilter(logging.Filter):
    """
    Add correlation ID to every log message
    Useful for tracing requests through the system
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        correlation_id = correlation_id_var.get()
        if correlation_id:
            record.correlation_id = correlation_id
        else:
            record.correlation_id = "N/A"
        return True


class JSONFormatter(logging.Formatter):
    """
    Format logs as JSON for better parsing in production environments
    Can be toggled on/off based on environment
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "N/A"),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


class StructuredLogger:
    """
    Enhanced logger with structured logging capabilities
    Supports correlation IDs and extra metadata
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
    
    def _log(self, level: int, message: str, **extra_data):
        """Internal logging method with extra data support"""
        if extra_data:
            self.logger.log(level, message, extra={"extra_data": extra_data})
        else:
            self.logger.log(level, message)
    
    def info(self, message: str, **extra_data):
        """Log info level"""
        self._log(logging.INFO, message, **extra_data)
    
    def error(self, message: str, **extra_data):
        """Log error level"""
        self._log(logging.ERROR, message, **extra_data)
    
    def warning(self, message: str, **extra_data):
        """Log warning level"""
        self._log(logging.WARNING, message, **extra_data)
    
    def debug(self, message: str, **extra_data):
        """Log debug level"""
        self._log(logging.DEBUG, message, **extra_data)
    
    def exception(self, message: str, **extra_data):
        """Log exception with traceback"""
        self.logger.exception(message, extra={"extra_data": extra_data} if extra_data else None)


def setup_logger(use_json: bool = False) -> StructuredLogger:
    """
    Setup and configure the logger
    
    Args:
        use_json: Use JSON formatting for logs (better for production)
        
    Returns:
        StructuredLogger instance
    """
    logger_instance = StructuredLogger("erp_rag")
    underlying_logger = logger_instance.logger
    
    # Remove existing handlers if any
    underlying_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Add correlation ID filter
    correlation_filter = CorrelationIDFilter()
    console_handler.addFilter(correlation_filter)
    
    # Choose formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(correlation_id)s | %(levelname)s | %(message)s"
        )
    
    console_handler.setFormatter(formatter)
    underlying_logger.addHandler(console_handler)
    
    return logger_instance


# Global logger instance
logger = setup_logger()


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set or generate a correlation ID for the current context
    
    Args:
        correlation_id: Optional specific ID, generates UUID if None
        
    Returns:
        The correlation ID
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return correlation_id_var.get()


def reset_correlation_id() -> None:
    """Reset correlation ID for context"""
    correlation_id_var.set(None)