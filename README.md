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

**For detailed setup instructions and troubleshooting, see [SETUP.md](SETUP.md)**

### Quick Setup (3 steps)

1. **Get Gemini API Key**:
   - Go to https://aistudio.google.com/apikey
   - Click "Create API key"
   - Copy your key

2. **Configure Backend**:
   - Navigate to `backend/`
   - Create a `.env` file with:
     ```
     GEMINI_API_KEY=your_key_here
     ```

3. **Run Backend**:
   ```bash
   cd backend
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

The backend will run at `http://127.0.0.1:8000`

**See [SETUP.md](SETUP.md) for detailed instructions, testing, and troubleshooting.**

## Backend endpoints

- `POST /ask` - Use the RAG engine for ERP-based answers.
- `POST /agent-ask` - Use the AI Agent layer that chooses actions and may call tools.

## Documentation

- **Getting Started**: See [SETUP.md](SETUP.md) for detailed local development setup
- **Production Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md) for Render & Vercel deployment guides
- **Project Overview**: Read [docs/ERP_AI_Assistant_Documentation.md](docs/ERP_AI_Assistant_Documentation.md) for beginner-friendly documentation
- **Generate PDF**: Create a PDF version with:
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
