"""
Configuration Management for ERP RAG System
Centralized configuration with environment variable support and validation
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    Allows configuration via .env file or environment variables
    """
    
    # API Configuration
    api_title: str = "ERP RAG Assistant API"
    api_version: str = "1.0.0"
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    api_workers: int = Field(default=1, env="API_WORKERS")
    
    # CORS Configuration
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    
    # LLM Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    model_name: str = Field(default="models/gemma-4-26b-a4b-it", env="MODEL_NAME")
    
    # RAG Configuration
    retrieval_top_k: int = Field(default=5, env="RETRIEVAL_TOP_K")
    session_ttl_minutes: int = Field(default=60, env="SESSION_TTL_MINUTES")
    max_sessions: int = Field(default=1000, env="MAX_SESSIONS")
    max_history_per_session: int = Field(default=20, env="MAX_HISTORY")
    
    # LLM Generation Configuration
    temperature: float = Field(default=0.1, env="TEMPERATURE")
    max_output_tokens: int = Field(default=2048, env="MAX_OUTPUT_TOKENS")
    max_context_chars: int = Field(default=12000, env="MAX_CONTEXT_CHARS")
    
    # Agent Configuration
    agent_max_iterations: int = Field(default=3, env="AGENT_MAX_ITERATIONS")
    agent_retry_attempts: int = Field(default=3, env="AGENT_RETRY_ATTEMPTS")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    use_json_logging: bool = Field(default=False, env="USE_JSON_LOGGING")
    
    # Data Configuration
    data_dir: str = Field(default="data", env="DATA_DIR")
    chunks_file: str = Field(default="erp_chunks.json", env="CHUNKS_FILE")
    embeddings_file: str = Field(default="erp_chunks_embeddings.npy", env="EMBEDDINGS_FILE")
    
    # Cache Configuration
    cache_max_size: int = Field(default=256, env="CACHE_MAX_SIZE")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=False, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: str = Field(default="minute", env="RATE_LIMIT_WINDOW")
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v
    
    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("temperature must be between 0 and 2")
        return v
    
    @validator("cors_origins")
    def parse_cors_origins(cls, v):
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"Error loading configuration: {e}")
    # Create minimal settings for error handling
    settings = None


def get_settings() -> Settings:
    """Get or create settings instance"""
    global settings
    if settings is None:
        settings = Settings()
    return settings


def validate_settings() -> Optional[str]:
    """
    Validate all critical settings
    Returns error message if validation fails, None if OK
    """
    try:
        s = get_settings()
        
        # Check critical environment variables
        if not s.gemini_api_key:
            return "GEMINI_API_KEY is not set"
        
        # Validate numeric ranges
        if s.retrieval_top_k < 1 or s.retrieval_top_k > 50:
            return "RETRIEVAL_TOP_K must be between 1 and 50"
        
        if s.max_output_tokens < 100 or s.max_output_tokens > 4096:
            return "MAX_OUTPUT_TOKENS must be between 100 and 4096"
        
        if s.session_ttl_minutes < 5 or s.session_ttl_minutes > 1440:
            return "SESSION_TTL_MINUTES must be between 5 and 1440"
        
        return None
    
    except Exception as e:
        return f"Configuration validation error: {str(e)}"
