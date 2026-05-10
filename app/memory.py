"""
Session Memory Manager for ERP RAG System
Handles conversation history and context persistence
Production-ready with TTL and size limits
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.logger import logger


class ConversationEntry:
    """Represents a single conversation turn"""
    
    def __init__(self, question: str, answer: str, metadata: Optional[Dict] = None):
        self.timestamp = datetime.utcnow()
        self.question = question
        self.answer = answer
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "question": self.question,
            "answer": self.answer,
            "metadata": self.metadata
        }


class SessionMemory:
    """
    Manages conversation history for a single session
    Features:
    - TTL (Time To Live) for sessions
    - Max conversation history limit
    - Automatic cleanup of old entries
    """
    
    def __init__(self, session_id: str, max_history: int = 20, ttl_minutes: int = 60):
        """
        Initialize session memory
        
        Args:
            session_id: Unique session identifier
            max_history: Maximum number of conversation turns to keep
            ttl_minutes: Time in minutes before session expires
        """
        self.session_id = session_id
        self.max_history = max_history
        self.ttl = timedelta(minutes=ttl_minutes)
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.conversation_history: List[ConversationEntry] = []
    
    def add_entry(self, question: str, answer: str, metadata: Optional[Dict] = None) -> None:
        """Add a new conversation entry"""
        self.last_accessed = datetime.utcnow()
        
        entry = ConversationEntry(question, answer, metadata)
        self.conversation_history.append(entry)
        
        # Maintain size limit by removing oldest entries
        if len(self.conversation_history) > self.max_history:
            removed = len(self.conversation_history) - self.max_history
            self.conversation_history = self.conversation_history[-self.max_history:]
            logger.info(f"Session {self.session_id}: Trimmed {removed} old entries")
    
    def get_history(self, max_entries: Optional[int] = None) -> str:
        """
        Get formatted conversation history
        
        Args:
            max_entries: Number of recent entries to return (default: all)
            
        Returns:
            Formatted string of conversation history
        """
        self.last_accessed = datetime.utcnow()
        
        if not self.conversation_history:
            return ""
        
        # Use specified max or all history
        entries = self.conversation_history
        if max_entries:
            entries = entries[-max_entries:]
        
        formatted_history = []
        for entry in entries:
            formatted_history.append(
                f"User: {entry.question}\nAssistant: {entry.answer}"
            )
        
        return "\n---\n".join(formatted_history)
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() - self.last_accessed > self.ttl
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "entries_count": len(self.conversation_history),
            "is_expired": self.is_expired(),
            "age_minutes": int((datetime.utcnow() - self.created_at).total_seconds() / 60)
        }
    
    def clear(self) -> None:
        """Clear all history from session"""
        self.conversation_history.clear()
        logger.info(f"Session {self.session_id}: History cleared")


class MemoryManager:
    """
    Manages multiple user sessions
    Handles session lifecycle, cleanup, and persistence
    
    Features:
    - Automatic cleanup of expired sessions
    - Session monitoring and statistics
    - Configurable memory limits
    """
    
    def __init__(self, max_sessions: int = 1000, session_ttl_minutes: int = 60):
        """
        Initialize memory manager
        
        Args:
            max_sessions: Maximum number of concurrent sessions
            session_ttl_minutes: TTL for each session in minutes
        """
        self.sessions: Dict[str, SessionMemory] = {}
        self.max_sessions = max_sessions
        self.session_ttl_minutes = session_ttl_minutes
        logger.info(f"MemoryManager initialized: max_sessions={max_sessions}, ttl={session_ttl_minutes}m")
    
    def get(self, session_id: str, max_entries: Optional[int] = 5) -> str:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            max_entries: Number of recent entries to return
            
        Returns:
            Formatted conversation history
        """
        self._cleanup_expired_sessions()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(
                session_id,
                ttl_minutes=self.session_ttl_minutes
            )
            logger.info(f"Created new session: {session_id}")
        
        memory = self.sessions[session_id]
        return memory.get_history(max_entries)
    
    def update(self, session_id: str, question: str, answer: str, 
               metadata: Optional[Dict] = None) -> None:
        """
        Update session with new conversation entry
        
        Args:
            session_id: Session identifier
            question: User question
            answer: Assistant answer
            metadata: Optional metadata to store with entry
        """
        self._cleanup_expired_sessions()
        
        # Ensure session exists
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(
                session_id,
                ttl_minutes=self.session_ttl_minutes
            )
        
        # Check session limit
        if len(self.sessions) > self.max_sessions:
            logger.warning(f"Session limit approaching: {len(self.sessions)}/{self.max_sessions}")
            self._cleanup_expired_sessions()
        
        self.sessions[session_id].add_entry(question, answer, metadata)
    
    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions from memory"""
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def clear_all(self) -> int:
        """
        Clear all sessions
        
        Returns:
            Number of sessions cleared
        """
        count = len(self.sessions)
        self.sessions.clear()
        logger.info(f"Cleared all sessions: {count}")
        return count
    
    def get_stats(self) -> Dict:
        """
        Get manager statistics
        
        Returns:
            Dictionary with statistics
        """
        self._cleanup_expired_sessions()
        
        active_sessions = len(self.sessions)
        total_entries = sum(len(s.conversation_history) for s in self.sessions.values())
        
        return {
            "active_sessions": active_sessions,
            "max_sessions": self.max_sessions,
            "total_entries": total_entries,
            "utilization_percent": (active_sessions / self.max_sessions) * 100,
            "session_ttl_minutes": self.session_ttl_minutes,
            "sessions": [s.get_stats() for s in self.sessions.values()]
        }
    
    def get_session_history(self, session_id: str) -> Optional[List[Dict]]:
        """
        Get full conversation history for a session
        Useful for client-side state management
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of conversation entries or None if session not found
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return [entry.to_dict() for entry in session.conversation_history]
