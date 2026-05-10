"""
Custom exceptions for ERP RAG System
Production-ready error handling with detailed logging
"""

from typing import Optional, Any, Dict
from app.logger import logger


class ERPRAGException(Exception):
    """Base exception for all ERP RAG errors"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        
        logger.error(
            f"ERPRAGException: {error_code} - {message}",
            extra={"details": self.details}
        )
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to API response format"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "status": self.status_code,
                "details": self.details
            }
        }


class ConfigurationError(ERPRAGException):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            status_code=500,
            details=details
        )


class EnvironmentError(ERPRAGException):
    """Raised when required environment variables are missing"""
    
    def __init__(self, missing_keys: list[str]):
        message = f"Missing environment variables: {', '.join(missing_keys)}"
        super().__init__(
            message=message,
            error_code="ENV_CONFIG_ERROR",
            status_code=500,
            details={"missing_keys": missing_keys}
        )


class InitializationError(ERPRAGException):
    """Raised when system initialization fails"""
    
    def __init__(self, component: str, error: str):
        super().__init__(
            message=f"Failed to initialize {component}: {error}",
            error_code="INIT_ERROR",
            status_code=500,
            details={"component": component, "error": error}
        )


class RetrievalError(ERPRAGException):
    """Raised when retrieval operations fail"""
    
    def __init__(self, message: str, query: Optional[str] = None):
        details = {}
        if query:
            details["query"] = query[:500]  # Truncate for security
        
        super().__init__(
            message=message,
            error_code="RETRIEVAL_ERROR",
            status_code=500,
            details=details
        )


class LLMError(ERPRAGException):
    """Raised when LLM operations fail"""
    
    def __init__(self, message: str, operation: str = "generate"):
        super().__init__(
            message=message,
            error_code="LLM_ERROR",
            status_code=503,
            details={"operation": operation}
        )


class ValidationError(ERPRAGException):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation failed for '{field}': {reason}",
            error_code="VALIDATION_ERROR",
            status_code=400,
            details={"field": field, "reason": reason}
        )


class RateLimitError(ERPRAGException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, session_id: str, limit: int, window: str = "minute"):
        super().__init__(
            message=f"Rate limit exceeded ({limit} requests per {window})",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"limit": limit, "window": window}
        )


class SessionError(ERPRAGException):
    """Raised when session management fails"""
    
    def __init__(self, session_id: str, reason: str):
        super().__init__(
            message=f"Session error for '{session_id}': {reason}",
            error_code="SESSION_ERROR",
            status_code=400,
            details={"session_id": session_id, "reason": reason}
        )


class ToolExecutionError(ERPRAGException):
    """Raised when tool execution fails"""
    
    def __init__(self, tool_name: str, error: str):
        super().__init__(
            message=f"Tool '{tool_name}' execution failed: {error}",
            error_code="TOOL_ERROR",
            status_code=500,
            details={"tool": tool_name, "error": error}
        )


class PlanningError(ERPRAGException):
    """Raised when planning/reasoning fails"""
    
    def __init__(self, message: str, question: Optional[str] = None):
        details = {}
        if question:
            details["question"] = question[:500]
        
        super().__init__(
            message=message,
            error_code="PLANNING_ERROR",
            status_code=500,
            details=details
        )


class APIError(ERPRAGException):
    """Generic API error"""
    
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(
            message=message,
            error_code="API_ERROR",
            status_code=status_code
        )


def create_error_response(exc: Exception) -> Dict[str, Any]:
    """
    Create standardized error response
    
    Args:
        exc: Exception to convert
        
    Returns:
        Dictionary suitable for JSON response
    """
    if isinstance(exc, ERPRAGException):
        return exc.to_dict()
    
    # Handle unexpected exceptions
    logger.exception(f"Unexpected exception: {exc}")
    
    return {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An internal error occurred. Please try again later.",
            "status": 500,
            "details": {"type": type(exc).__name__}
        }
    }
