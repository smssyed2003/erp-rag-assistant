"""
ERP RAG Assistant API - Production-Ready Backend
Implements Retrieval-Augmented Generation with Agent-based routing and planning
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.logger import logger, set_correlation_id, get_correlation_id
from app.rag_engine import RAGEngine
from app.agent import Agent
from app.exceptions import (
    ERPRAGException, InitializationError, ValidationError, 
    create_error_response, APIError
)

# Load environment variables
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# Global components
rag: Optional[RAGEngine] = None
agent: Optional[Agent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager
    Handles startup and shutdown events
    """
    # Startup
    try:
        logger.info("=" * 60)
        logger.info("STARTING ERP RAG API")
        logger.info("=" * 60)
        
        global rag, agent
        
        # Validate environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise InitializationError(
                "GEMINI_API_KEY",
                "Environment variable not set"
            )
        
        logger.info("✓ Environment validated")
        
        # Initialize RAG Engine
        rag = RAGEngine()
        logger.info("✓ RAG Engine initialized")
        
        # Initialize Agent
        agent = Agent(rag)
        logger.info("✓ Agent initialized")
        
        logger.info("=" * 60)
        logger.info("API STARTUP COMPLETE - Ready to serve requests")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"CRITICAL: Startup failed - {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("API shutting down...")
    logger.info("Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title="ERP RAG Assistant API",
    description="Production-ready Retrieval-Augmented Generation backend for ERP knowledge queries",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Apply lifespan context manager
app.router.lifespan_context = lifespan


# Middleware for correlation IDs
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to all requests for tracing"""
    correlation_id = request.headers.get("X-Correlation-ID")
    set_correlation_id(correlation_id)
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Correlation-ID"] = get_correlation_id() or "N/A"
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Request/Response Models
class QueryRequest(BaseModel):
    """Base query request model with validation"""
    session_id: str = Field(..., min_length=1, max_length=100, description="Unique session identifier")
    question: str = Field(..., min_length=3, max_length=2000, description="User question")
    
    @validator("session_id")
    def validate_session_id(cls, v):
        """Validate session ID format"""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Session ID must be alphanumeric with optional - or _")
        return v
    
    @validator("question")
    def validate_question(cls, v):
        """Sanitize question"""
        # Remove excessive whitespace
        v = " ".join(v.split())
        if len(v) < 3:
            raise ValueError("Question must be at least 3 characters")
        return v


class QueryResponse(BaseModel):
    """Standard query response model"""
    answer: str
    sources: List[Dict[str, str]] = []
    execution_time_ms: float
    correlation_id: Optional[str] = None


class AgentQueryResponse(BaseModel):
    """Agent query response with steps"""
    answer: str
    steps: List[Dict[str, Any]] = []
    sources: List[Dict[str, str]] = []
    execution_time_ms: float
    correlation_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    components: Dict[str, str]
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response model"""
    error: Dict[str, Any]


class StatsResponse(BaseModel):
    """System statistics response"""
    retriever_stats: Dict[str, Any]
    memory_stats: Dict[str, Any]
    timestamp: str


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(ERPRAGException)
async def erp_exception_handler(request: Request, exc: ERPRAGException):
    """Handle ERP RAG exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    error_response = create_error_response(exc)
    return JSONResponse(
        status_code=500,
        content=error_response
    )


# API Endpoints
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint"
)
def health_check() -> HealthResponse:
    """
    Check API health and component status
    Returns detailed component information
    """
    try:
        rag_status = "healthy" if rag is not None else "not_initialized"
        agent_status = "healthy" if agent is not None else "not_initialized"
        
        return HealthResponse(
            status="operational" if rag and agent else "degraded",
            timestamp=datetime.utcnow().isoformat(),
            components={
                "rag_engine": rag_status,
                "agent": agent_status,
                "api": "healthy"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise APIError("Health check failed", 503)


@app.get(
    "/stats",
    response_model=StatsResponse,
    tags=["System"],
    summary="System statistics"
)
def get_stats() -> StatsResponse:
    """
    Get system statistics and metrics
    Useful for monitoring and debugging
    """
    try:
        if not rag:
            raise APIError("System not initialized", 503)
        
        retriever_stats = rag.retriever.get_stats()
        memory_stats = rag.memory.get_stats()
        
        return StatsResponse(
            retriever_stats=retriever_stats,
            memory_stats=memory_stats,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise


@app.post(
    "/ask",
    response_model=QueryResponse,
    tags=["Query"],
    summary="Direct RAG query",
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}}
)
def ask(query: QueryRequest) -> QueryResponse:
    """
    Direct RAG-based query without agent planning
    Faster for simple questions
    
    Args:
        query: QueryRequest with session_id and question
        
    Returns:
        Direct answer with sources
    """
    try:
        if not rag:
            raise APIError("RAG Engine not initialized", 503)
        
        start_time = time.time()
        
        logger.info(
            f"Direct RAG query received",
            session_id=query.session_id,
            question_length=len(query.question)
        )
        
        # Execute query
        response = rag.query(query.question, query.session_id)
        
        execution_time = (time.time() - start_time) * 1000
        
        logger.info(
            f"Direct RAG query completed",
            session_id=query.session_id,
            execution_time_ms=execution_time,
            sources_count=len(response.get("sources", []))
        )
        
        return QueryResponse(
            answer=response.get("answer", ""),
            sources=response.get("sources", []),
            execution_time_ms=execution_time,
            correlation_id=get_correlation_id()
        )
    
    except Exception as e:
        logger.error(f"RAG query failed: {e}", exc_info=True)
        raise


@app.post(
    "/agent-ask",
    response_model=AgentQueryResponse,
    tags=["Query"],
    summary="Agent-based query with planning",
    responses={400: {"model": ErrorResponse}, 503: {"model": ErrorResponse}}
)
def agent_ask(query: QueryRequest) -> AgentQueryResponse:
    """
    Query with intelligent agent planning and tool selection
    Better for complex multi-step reasoning
    
    Args:
        query: QueryRequest with session_id and question
        
    Returns:
        Answer with reasoning steps and sources
    """
    try:
        if not agent:
            raise APIError("Agent not initialized", 503)
        
        start_time = time.time()
        
        logger.info(
            f"Agent query received",
            session_id=query.session_id,
            question_length=len(query.question)
        )
        
        # Execute agent
        response = agent.run(query.question, query.session_id)
        
        execution_time = (time.time() - start_time) * 1000
        
        logger.info(
            f"Agent query completed",
            session_id=query.session_id,
            execution_time_ms=execution_time,
            steps_count=len(response.get("steps", []))
        )
        
        return AgentQueryResponse(
            answer=response.get("answer", ""),
            steps=response.get("steps", []),
            sources=response.get("sources", []),
            execution_time_ms=execution_time,
            correlation_id=get_correlation_id()
        )
    
    except Exception as e:
        logger.error(f"Agent query failed: {e}", exc_info=True)
        raise


@app.get(
    "/sessions/{session_id}/history",
    tags=["Session Management"],
    summary="Get session conversation history"
)
def get_session_history(session_id: str) -> Dict[str, Any]:
    """
    Get conversation history for a specific session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Conversation history with metadata
    """
    try:
        if not rag:
            raise APIError("System not initialized", 503)
        
        history = rag.memory.get_session_history(session_id)
        
        if history is None:
            return {
                "session_id": session_id,
                "message": "Session not found or empty",
                "entries": []
            }
        
        return {
            "session_id": session_id,
            "entries": history,
            "count": len(history),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Session history retrieval failed: {e}")
        raise


@app.delete(
    "/sessions/{session_id}",
    tags=["Session Management"],
    summary="Delete a session"
)
def delete_session(session_id: str) -> Dict[str, Any]:
    """
    Delete a specific session and its history
    
    Args:
        session_id: Session identifier
        
    Returns:
        Deletion status
    """
    try:
        if not rag:
            raise APIError("System not initialized", 503)
        
        deleted = rag.memory.delete_session(session_id)
        
        return {
            "session_id": session_id,
            "deleted": deleted,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Session deletion failed: {e}")
        raise


@app.post(
    "/cache/clear",
    tags=["System"],
    summary="Clear retrieval cache"
)
def clear_cache() -> Dict[str, str]:
    """Clear the retrieval cache"""
    try:
        if not rag:
            raise APIError("System not initialized", 503)
        
        rag.retriever.clear_cache()
        
        return {
            "status": "success",
            "message": "Cache cleared",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise


@app.get("/", tags=["System"], summary="Root endpoint")
def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "name": "ERP RAG Assistant API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs",
        "health": "/health"
    }


# Startup logging
if __name__ == "__main__":
    logger.info("ERP RAG API module loaded successfully")