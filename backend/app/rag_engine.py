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
        You are an ERP assistant helping users understand ERP concepts clearly.

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

        INSTRUCTIONS:
        - Give a clear and concise answer
        - Use simple language (non-technical if possible)
        - Keep it under 120 words
        - Use short paragraphs or bullet points if needed
        - Avoid markdown symbols like ** or ###
        - Do NOT over-explain
        - If context is missing, say: "Based on standard ERP practices"
        - If question is simple → give short answer
        - If question asks "explain" → give step-by-step

        ANSWER:
        """

        answer = self.retriever.generate(prompt)

        self.memory.update(session_id, question, answer)

        return {
            "answer": answer,
            "sources": sources
        }