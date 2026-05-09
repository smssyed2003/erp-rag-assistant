# ERP RAG System v0.1

This repository contains an ERP AI Assistant project with a backend service, frontend interface, and documentation.

## What this project does

- Helps users ask questions about ERP concepts and workflows.
- Uses retrieval-augmented generation (RAG) to find ERP content and answer questions accurately.
- Includes an AI Agent that can decide whether to search for context or answer directly.
- Provides a frontend chat interface for user interaction.

## Main folders

- `backend/` - The complete backend service with FastAPI, retrieval logic, and agent code.
- `frontend/` - Angular-based chat application.
- `data/` - ERP content chunks used for retrieval.
- `docs/` - Project documentation and a PDF generation utility.

## Quick start

1. Open the terminal and go to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Add your Gemini API key to a `.env` file in `backend/`:
   ```text
   GEMINI_API_KEY=your_api_key_here
   ```
5. Run the backend service:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Backend endpoints

- `POST /ask` - Use the RAG engine for ERP-based answers.
- `POST /agent-ask` - Use the AI Agent layer that chooses actions and may call tools.

## Documentation

- Read the beginner-friendly documentation in `docs/ERP_AI_Assistant_Documentation.md`.
- Generate a PDF version with:
  ```bash
  python docs/generate_pdf.py
  ```

## Notes for non-technical users

- The backend is the brain of the system.
- The frontend is the user interface.
- The AI Agent is a smart helper inside the backend that decides how to answer.
- If you are not familiar with AI, the documentation explains the main ideas in plain language.

## How to use this project (non-technical)

1. Start the backend server first from the `backend/` folder.
2. Open the frontend app in a browser.
3. Type your question in the chat box.
4. The assistant will answer using ERP knowledge and show sources.
5. If the assistant needs more detail, it may search ERP documents before answering.

This setup is built so that non-technical users can ask questions and receive clear written answers without needing to understand the code.

## Frontend integration

- The frontend uses `frontend/src/environments/environment.ts` to locate the backend.
- It sends requests to `backendUrl + '/agent-ask'`.
- The backend allows browser requests through CORS, so the frontend and backend can communicate.

## Git and cleanup

- The repository is now organized with only one backend service.
- Local virtual environments are excluded in `.gitignore`:
  - `venv/`
  - `.venv/`
  - `backend/venv/`
