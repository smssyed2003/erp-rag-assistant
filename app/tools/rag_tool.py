from typing import Any, Dict
from app.tools.base_tool import BaseTool


class RAGTool(BaseTool):
    name = "rag_search"
    description = "Retrieve ERP context and sources from the existing RAG engine."

    def __init__(self, rag_engine):
        self.rag_engine = rag_engine

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        question = input_data.get("question")
        if not question:
            raise ValueError("rag_search tool requires a question field")

        context, sources = self.rag_engine.retriever.retrieve(question)
        return {
            "context": context,
            "sources": sources,
            "question": question
        }
