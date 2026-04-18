from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from app.rag_engine import RAGEngine

load_dotenv()

app = FastAPI(
    title="ERP RAG Assistant API",
    description="Retrieval-augmented generation backend for ERP knowledge queries.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGEngine()

class Query(BaseModel):
    session_id: str
    question: str

@app.post("/ask")
def ask(q: Query):
    return rag.query(q.question, q.session_id)
