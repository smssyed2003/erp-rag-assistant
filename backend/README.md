# Backend Service - ERP RAG System

This folder contains the backend API and core ERP assistant logic.

## What is here

- `app/main.py` - FastAPI application with endpoints.
- `app/agent.py` - AI Agent orchestration logic.
- `app/planner.py` - Decides the next action and builds prompts.
- `app/tool_registry.py` - Maps agent actions to tools.
- `app/rag_engine.py` - Runs retrieval and answer generation.
- `app/retrieval.py` - Loads ERP data, builds embeddings, and performs search.
- `app/tools/` - Available agent tools like `rag_search` and `direct_answer`.
- `app/utils.py` - Helper functions for paths, JSON, and environment variables.
- `app/memory.py` - Simple session memory tracking.

## How the agent works

- The Agent receives a question and asks the Planner what to do.
- The Planner chooses between:
  - `rag_search` - get ERP context and sources
  - `direct_answer` - answer directly without retrieval
- The tool result is stored as a step.
- The agent synthesizes the final answer from all tool outputs.

## Required setup

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` with your Gemini key:
   ```text
   GEMINI_API_KEY=your_api_key_here
   ```

## Run locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API endpoints

- `POST /ask` - Use the RAG engine for ERP questions.
- `POST /agent-ask` - Use the AI Agent layer.

## Notes

- If the Gemini API key is missing, the code will log the error and cannot call the model.
- The `agent` path is designed to run if the planner can access Gemini.
- The backend is now self-contained in `backend/` and the `app/` code needed for this service is inside `backend/app/`.
