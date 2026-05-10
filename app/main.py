from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from app.logger import logger
import os
from pathlib import Path
from app.rag_engine import RAGEngine
from app.agent import Agent

# Load environment variables from .env file in backend directory
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="ERP RAG Assistant API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = None
agent = None

@app.on_event("startup")
def startup_event():
    global rag, agent
    logger.info("Starting ERP RAG API...")

    try:
        logger.info(f"GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")
        rag = RAGEngine()
        agent = Agent(rag)
        logger.info("RAG Engine and Agent initialized successfully")
    except Exception as e:
        logger.exception("Failed during startup")
        raise e

class Query(BaseModel):
    session_id: str
    question: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(q: Query):
    logger.info(f"Incoming query | session={q.session_id} | question={q.question}")

    try:
        response = rag.query(q.question, q.session_id)

        logger.info("Response generated successfully")

        return {"response": response}

    except Exception as e:
        logger.exception("Error during /ask")
        return {"error": str(e)}

@app.post("/agent-ask")
def agent_ask(q: Query):
    logger.info(f"Incoming agent query | session={q.session_id} | question={q.question}")

    try:
        if not agent:
            raise RuntimeError("Agent is not initialized")

        response = agent.run(q.question, q.session_id)
        logger.info("Agent response generated successfully")

        return {
            "answer": response.get("answer", ""),
            "steps": response.get("steps", []),
            "sources": response.get("sources", []),
        }

    except Exception as e:
        logger.exception("Error during /agent-ask")
        fallback = rag.query(q.question, q.session_id)

        return {
            "answer": fallback.get("answer", ""),
            "steps": [{
                "action": "fallback",
                "description": "Fallback to direct RAG answer due to agent endpoint failure"
            }],
            "sources": fallback.get("sources", []),
        }