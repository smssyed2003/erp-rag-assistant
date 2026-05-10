from typing import Any, Dict
from app.tools.base_tool import BaseTool
from app.rag_engine import RAGEngine


class RAGTool(BaseTool):
    name = "rag_search"
    description = "Run retrieval augmented generation queries via the RAG engine."

    def __init__(self, rag_engine: RAGEngine):
        super().__init__(name=self.name, description=self.description)
        self.rag_engine = rag_engine

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        question = input_data.get("question", "")
        session_id = input_data.get("session_id", "agent-session")

        if not question:
            return {
                "answer": "",
                "sources": [],
                "error": "Question is required for RAG search."
            }

        result = self.rag_engine.query(question, session_id)
        return {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
        }
