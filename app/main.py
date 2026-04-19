from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from app.rag_engine import RAGEngine

load_dotenv()

app = FastAPI(
    title="ERP RAG Assistant API",
    description="Retrieval-augmented generation backend for ERP knowledge queries.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = None

@app.on_event("startup")
def startup_event():
    global rag
    print("GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
    rag = RAGEngine()
    print("RAG Engine initialized")

class Query(BaseModel):
    session_id: str
    question: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(q: Query):
    try:
        response = rag.query(q.question, q.session_id)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}