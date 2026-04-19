from app.memory import MemoryManager
from app.retrieval import Retriever

class RAGEngine:

    def __init__(self):
        self.retriever = Retriever()
        self.memory = MemoryManager()

    def query(self, question, session_id):

        result = self.retriever.retrieve(question)

        if not result or not isinstance(result, tuple):
            context, sources = "", []
        else:
            context, sources = result
            
        memory = self.memory.get(session_id)

        prompt = f"""
        ROLE: ERP Functional Consultant

        PRIORITY:
        1. Context
        2. Chat history
        3. General ERP knowledge

        CHAT HISTORY:
        {memory}

        CONTEXT:
        {context}

        QUESTION:
        {question}

        RULES:
        - Always answer
        - If missing → "Based on standard ERP practices"
        - Step-by-step explanation
        """

        answer = self.retriever.generate(prompt)

        self.memory.update(session_id, question, answer)

        return {
            "answer": answer,
            "sources": sources
        }