from typing import Any, Dict
from app.tools.base_tool import BaseTool
from app.retrieval import Retriever


class DirectAnswerTool(BaseTool):
    name = "direct_answer"
    description = "Generate a direct answer using the retrieval LLM for general questions."

    def __init__(self, retriever: Retriever):
        super().__init__(name=self.name, description=self.description)
        self.retriever = retriever

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        question = input_data.get("question", "")

        if not question:
            return {
                "answer": "",
                "sources": [],
                "error": "Question is required for direct answer."
            }

        prompt = (
            "Answer the following ERP question clearly and succinctly. "
            "If the answer is not available from the internal knowledge base, say that you do not have enough information.\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        answer = self.retriever.generate(prompt)
        return {
            "answer": answer,
            "sources": []
        }
