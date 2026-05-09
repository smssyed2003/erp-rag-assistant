from typing import Any, Dict
from app.tools.base_tool import BaseTool


class DirectAnswerTool(BaseTool):
    name = "direct_answer"
    description = "Answer general knowledge questions directly using the LLM without retrieval."

    def __init__(self, retriever):
        self.retriever = retriever

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        question = input_data.get("question")
        if not question:
            raise ValueError("direct_answer tool requires a question field")

        prompt = f"""
You are an AI assistant helping with general knowledge questions.

QUESTION:
{question}

INSTRUCTIONS:
- Give a clear and concise answer
- Use simple language
- Keep it under 120 words
- Avoid markdown symbols

ANSWER:
"""

        answer = self.retriever.generate(prompt)

        return {
            "answer": answer,
            "question": question
        }