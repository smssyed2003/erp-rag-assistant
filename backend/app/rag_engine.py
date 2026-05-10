"""
RAG Engine - Core Retrieval-Augmented Generation Component
Combines retrieval, memory management, and LLM generation
"""

from typing import Dict, Any, Optional
from app.memory import MemoryManager
from app.retrieval import Retriever
from app.logger import logger
from app.exceptions import RetrievalError, LLMError


class RAGEngine:
    """
    Main RAG Engine orchestrating retrieval and generation
    
    Features:
    - Hybrid retrieval (vector + BM25)
    - Session-based memory management
    - Context-aware LLM prompting
    - Comprehensive error handling
    - Performance metrics
    """
    
    def __init__(self, session_ttl_minutes: int = 60):
        """
        Initialize RAG Engine
        
        Args:
            session_ttl_minutes: Session timeout in minutes
        """
        try:
            self.retriever = Retriever()
            self.memory = MemoryManager(session_ttl_minutes=session_ttl_minutes)
            logger.info("RAG Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Engine: {e}", exc_info=True)
            raise
    
    def query(self, question: str, session_id: str) -> Dict[str, Any]:
        """
        Execute a RAG query with retrieval, memory, and generation
        
        Args:
            question: User question
            session_id: Unique session identifier
            
        Returns:
            Dictionary with 'answer' and 'sources'
            
        Raises:
            RetrievalError: If retrieval fails
            LLMError: If generation fails
        """
        try:
            # Step 1: Retrieve relevant context
            try:
                result = self.retriever.retrieve(question)
                if not result or not isinstance(result, tuple):
                    context, sources = "", []
                else:
                    context, sources = result
            except Exception as e:
                logger.error(f"Retrieval failed: {e}")
                context, sources = "", []
            
            # Step 2: Get conversation history from memory
            try:
                memory_context = self.memory.get(session_id)
            except Exception as e:
                logger.error(f"Memory retrieval failed: {e}")
                memory_context = ""
            
            # Step 3: Build comprehensive prompt
            prompt = self._build_prompt(question, memory_context, context)
            
            # Step 4: Generate answer
            try:
                answer = self.retriever.generate(prompt)
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                answer = f"Unable to generate response. Error: {str(e)}"
            
            # Step 5: Update memory
            try:
                self.memory.update(session_id, question, answer, {
                    "sources_count": len(sources),
                    "context_available": bool(context)
                })
            except Exception as e:
                logger.warning(f"Memory update failed: {e}")
            
            logger.info(
                f"Query completed successfully",
                session_id=session_id,
                answer_length=len(answer),
                sources_count=len(sources)
            )
            
            return {
                "answer": answer,
                "sources": sources
            }
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}", exc_info=True)
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": []
            }
    
    def _build_prompt(self, question: str, memory: str, context: str) -> str:
        """
        Build optimized prompt for LLM with memory and context
        
        Args:
            question: User question
            memory: Conversation history
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are an expert ERP assistant helping users understand ERP concepts clearly.

Your response should be:
- Clear and concise (120-150 words maximum)
- Non-technical when possible
- Well-structured with short paragraphs or bullet points
- Based primarily on the provided context
- Factually accurate without speculation

PRIORITY:
1. Retrieved Context (most important)
2. Conversation History
3. General ERP Knowledge

CONVERSATION HISTORY (from this session):
{memory if memory else "No previous conversation"}

RETRIEVED CONTEXT (from knowledge base):
{context if context else "No matching documents found"}

USER QUESTION:
{question}

RESPONSE INSTRUCTIONS:
- Give a direct, clear answer
- If context directly answers the question, use it
- If context is limited, acknowledge it clearly
- Do NOT over-explain or use markdown formatting
- For "what is" questions: provide definition + 1-2 examples
- For "how to" questions: provide step-by-step process
- For complex questions: structure with bullets
- If uncertain: Say "Based on available documentation..." or "I don't have specific information on this"

ANSWER:"""
        
        return prompt
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get full context for a session
        Useful for debugging or frontend state management
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session context with history and metadata
        """
        try:
            history = self.memory.get_session_history(session_id)
            stats = self.memory.get_stats()
            
            session_stats = None
            for s in stats.get("sessions", []):
                if s["session_id"] == session_id:
                    session_stats = s
                    break
            
            return {
                "session_id": session_id,
                "history": history or [],
                "metadata": session_stats or {},
                "retriever_stats": self.retriever.get_stats()
            }
        except Exception as e:
            logger.error(f"Failed to get session context: {e}")
            return {
                "session_id": session_id,
                "error": str(e),
                "history": [],
                "metadata": {}
            }
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear conversation history for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        try:
            success = self.memory.delete_session(session_id)
            if success:
                logger.info(f"Session cleared: {session_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics
        
        Returns:
            Dictionary with all system metrics
        """
        return {
            "retriever": self.retriever.get_stats(),
            "memory": self.memory.get_stats()
        }