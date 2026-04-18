# ERP RAG Assistant - Complete Documentation Guide

## For Learning, Building, and Deploying an AI-Powered ERP Knowledge System

---

**Version**: 1.0  
**Date**: April 18, 2026  
**Project**: ERP RAG System  
**Status**: Production Ready

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Programming Fundamentals](#programming-fundamentals)
4. [Web Development Basics](#web-development-basics)
5. [AI and Machine Learning Concepts](#ai-and-machine-learning-concepts)
6. [Project Architecture](#project-architecture)
7. [Backend Deep Dive](#backend-deep-dive)
8. [Frontend Deep Dive](#frontend-deep-dive)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)
11. [Learning Resources](#learning-resources)

---

## Introduction

### What is ERP RAG Assistant?

ERP RAG Assistant is an AI-powered chatbot that answers questions about Enterprise Resource Planning (ERP) systems using:

- **Retrieval-Augmented Generation (RAG)**: Smart search + AI answers
- **Vector Databases**: Fast document similarity search
- **Large Language Models**: Google's Gemini AI
- **Web Technologies**: FastAPI backend + Angular frontend

### Why This Project?

1. **Learn Full-Stack Development**: Backend (Python), Frontend (TypeScript/Angular), Deployment
2. **Understand AI/ML**: Embeddings, vector search, RAG patterns
3. **Build Real Applications**: Deploy to production on free tiers
4. **Career Skills**: In-demand technologies for AI/ML engineers

### Who is This For?

- Beginners wanting to learn programming and AI
- Students learning web development
- Aspiring AI engineers
- Anyone wanting to understand how AI assistants work

---

## Quick Start

### In 5 Minutes

```bash
# 1. Clone the project
git clone https://github.com/yourusername/erp-rag-system.git
cd erp-rag-system

# 2. Setup backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# 3. Setup frontend
cd ../frontend
npm install

# 4. Start backend (new terminal)
cd ../backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 10000

# 5. Start frontend (new terminal)
cd ../frontend
npm start

# 6. Open browser
# Frontend: http://localhost:4200
# Backend API: http://localhost:10000
```

### What You'll See

- Frontend chat interface at http://localhost:4200
- Ask: "How to create a purchase order?"
- See: AI-generated answer with sources

---

## Programming Fundamentals

### Variables: Storing Information

```python
# Name, Age, Status
question = "How to create PO?"          # Text (string)
max_results = 3                         # Number (integer)
confidence = 0.95                       # Decimal (float)
is_available = True                     # True/False (boolean)
```

**In Our Project**: `backend/app/rag_engine.py` uses variables to store questions and answers.

### Data Structures: Organizing Information

```python
# List: Orders (array)
erp_processes = ["P2P", "O2C", "Finance"]

# Dictionary: Process details (key-value pairs)
process = {
    "name": "P2P",
    "steps": 5,
    "time_days": 10
}

# Nested: List of dictionaries
documents = [
    {"id": 1, "text": "...", "source": "SAP Guide"},
    {"id": 2, "text": "...", "source": "Best Practice"}
]
```

**In Our Project**: `backend/data/erp_chunks.json` uses dictionaries to store documents.

### Functions: Reusable Code

```python
def create_purchase_order(vendor, amount):
    """Create and return a PO"""
    po = {
        "vendor": vendor,
        "amount": amount,
        "status": "created"
    }
    return po

# Use it
my_po = create_purchase_order("Supplier ABC", 5000)
print(my_po)
```

**In Our Project**: Every file has functions. Example: `backend/app/utils.py` has `normalize_text()`.

### Classes: Object-Oriented Programming

```python
class MemoryManager:
    def __init__(self):
        self.conversations = {}
    
    def store(self, user_id, question, answer):
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        self.conversations[user_id].append({
            "q": question,
            "a": answer
        })
    
    def retrieve(self, user_id):
        return self.conversations.get(user_id, [])

# Use it
memory = MemoryManager()
memory.store("user1", "What is P2P?", "P2P is Procure-to-Pay...")
history = memory.retrieve("user1")
```

**In Our Project**: `backend/app/memory.py` is the `MemoryManager` class.

### Loops: Repeat Operations

```python
# For loop
documents = ["Doc1", "Doc2", "Doc3"]
for doc in documents:
    print(f"Processing: {doc}")

# For loop with index
for i, doc in enumerate(documents):
    print(f"{i+1}. {doc}")

# While loop
count = 0
while count < 3:
    print(f"Count: {count}")
    count += 1
```

**In Our Project**: `backend/app/retrieval.py` loops through embeddings.

### Conditionals: Making Decisions

```python
# If/else
api_key = "your-key"
if api_key.startswith("AIzaSyAXlKzgn"):
    print("Using placeholder key")
else:
    print("Using production key")

# Multiple conditions
score = 0.95
if score > 0.90:
    print("Highly relevant")
elif score > 0.70:
    print("Somewhat relevant")
else:
    print("Not relevant")
```

**In Our Project**: `backend/app/retrieval.py` checks if API is available.

---

## Web Development Basics

### What is a Web Application?

Think of it like a restaurant:
- **Frontend**: Menu and dining area (what customers see)
- **Backend**: Kitchen (where food is prepared)
- **API**: Waiter (brings requests to kitchen, returns responses)
- **Database**: Food storage (ingredients)

### HTTP: How Computers Talk

HTTP is the language of the web. Two main types:

```
GET: Get information
  Example: "Give me the menu" (retrieve data)
  
POST: Send information
  Example: "Send my order to the kitchen" (send data)
```

### REST API: Standard Web Service

REST uses HTTP requests to perform operations:

```
GET /ask              → Get list of questions
POST /ask             → Send a question
  Body: {"question": "...", "session_id": "..."}
GET /status           → Check if service is running
```

### How Our Project Works

```
User opens browser
    ↓
Angular frontend loads (HTML/CSS/JavaScript)
    ↓
User types: "How to create PO?"
    ↓
Frontend sends HTTP POST to backend:
    POST http://localhost:10000/ask
    Body: {"question": "How to create PO?", "session_id": "user1"}
    ↓
Backend receives, calls RAG engine
    ↓
RAG engine:
  1. Searches for relevant documents
  2. Gets conversation history
  3. Builds prompt for AI
  4. Calls Gemini AI
  5. Returns answer
    ↓
Backend sends HTTP response:
    Status: 200 OK
    Body: {"answer": "To create PO...", "sources": [...]}
    ↓
Frontend receives and displays answer
    ↓
User sees: "To create PO: 1. Go to MM01 transaction..."
```

---

## AI and Machine Learning Concepts

### What is Machine Learning?

Machine learning teaches computers to learn from examples instead of explicit instructions.

**Traditional Programming**:
```
Rules + Data → Output
"If score > 0.8, then relevant"
```

**Machine Learning**:
```
Data + Labels → Rules
"Learn what makes documents relevant"
```

### Large Language Models (LLMs)

LLMs are AI systems trained on enormous text datasets. They can:
- Understand language
- Generate text
- Answer questions
- Explain concepts

**Examples**: ChatGPT (OpenAI), Gemini (Google), Claude (Anthropic)

We use **Google Gemini 1.5 Flash** because:
- ✅ Fast responses
- ✅ Affordable API
- ✅ Good for ERP domain

### Embeddings: Turning Text into Numbers

The problem: Computers don't understand text meaning.

The solution: Convert text to vectors (lists of numbers).

```
Text: "How to create a purchase order?"
        ↓ (Embedding Model)
Vector: [0.123, -0.456, 0.789, ..., 0.234]  (768 numbers)

Text: "Steps for creating PO in SAP"
        ↓
Vector: [0.125, -0.450, 0.788, ..., 0.232]  (very similar!)
```

**Key Property**: Similar texts → similar vectors

### Vector Similarity Search

Find similar vectors quickly using distance metrics:

```
Distance between texts = How different their vectors are

Example:
- Distance to "How to create PO?" = 0.02 ← Very similar
- Distance to "Financial planning" = 1.50 ← Very different
- Distance to "PO in SAP" = 0.01 ← Extremely similar
```

### FAISS: Fast Similarity Search

With 1 million documents:
- **Naive search**: Calculate distance to each (too slow)
- **FAISS**: Smart data structures (fast!)

Think of it like:
- **Naive**: Read entire book to find "purchase orders"
- **FAISS**: Use index to jump to relevant section

### Retrieval-Augmented Generation (RAG)

Three steps:

```
1. RETRIEVAL (Vector Search)
   User Q: "How to create PO?"
   Find 3 similar documents:
   - "PO creation in SAP"
   - "P2P process workflow"
   - "Vendor master requirements"

2. AUGMENTATION (Add Context)
   Combine:
   - Retrieved documents
   - Conversation history
   - Original question
   → Create enhanced prompt

3. GENERATION (AI Answer)
   Gemini reads prompt with context
   Generates answer:
   "To create PO: 1. Go to transaction MM01..."
```

**Why RAG?** LLMs have knowledge cutoffs and can hallucinate. RAG gives them facts to work with.

---

## Project Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Browser)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    HTTP (JSON)
                           │
        ┌──────────────────▼──────────────────┐
        │   Frontend (Angular)                │
        │  - Chat UI                          │
        │  - Message display                  │
        │  - HTTP client                      │
        │                                     │
        │  Technologies:                      │
        │  - TypeScript                       │
        │  - Angular 17                       │
        │  - RxJS                             │
        └──────────────────┬──────────────────┘
                           │
                    HTTP POST /ask
                           │
        ┌──────────────────▼──────────────────┐
        │   Backend (FastAPI)                 │
        │  - HTTP server                      │
        │  - Request handling                 │
        │  - /ask endpoint                    │
        │                                     │
        │  Technologies:                      │
        │  - Python                           │
        │  - FastAPI                          │
        │  - Pydantic                         │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │   RAG Engine                        │
        │  - Orchestrates retrieval           │
        │  - Builds prompts                   │
        │  - Manages memory                   │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │   Retrieval Module                  │
        │  - Loads documents                  │
        │  - Creates embeddings               │
        │  - Builds FAISS index               │
        │  - Searches for similar docs        │
        │  - Calls Gemini API                 │
        │                                     │
        │  Technologies:                      │
        │  - NumPy (vectors)                  │
        │  - FAISS (search)                   │
        │  - google-generativeai (LLM)        │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │   Data & Services                   │
        │  - erp_chunks.json (documents)      │
        │  - Memory store (conversations)     │
        │  - Gemini AI (generation)           │
        │  - Google Embeddings API            │
        └─────────────────────────────────────┘
```

### Data Flow Diagram

```
User Question Input
       ↓
    [Frontend]
    - Display loading
    - Send HTTP request
       ↓
    [Backend: /ask endpoint]
    - Parse request
    - Extract question & session_id
       ↓
    [RAG Engine]
    - Get conversation history
    - Retrieve similar documents
       ↓
    [Retrieval Module]
    - Embed question (768 numbers)
    - Search FAISS index
    - Find top 3 documents
       ↓
    [Prompt Building]
    - Add role ("ERP Consultant")
    - Add retrieved context
    - Add conversation history
    - Add question
       ↓
    [Gemini AI]
    - Process prompt
    - Generate answer
       ↓
    [Backend Response]
    - Return {answer, sources}
       ↓
    [Frontend]
    - Hide loading
    - Display answer
    - Show sources
       ↓
    User sees answer with sources
```

---

## Backend Deep Dive

### File Structure

```
backend/
├── app/
│   ├── __init__.py          # Makes app a Python package
│   ├── main.py              # FastAPI app & /ask endpoint
│   ├── rag_engine.py        # RAG orchestration
│   ├── retrieval.py         # Vector search & LLM calls
│   ├── memory.py            # Chat memory management
│   └── utils.py             # Helper functions
├── data/
│   ├── erp_chunks.json      # Knowledge base documents
│   └── erp_chunks_embeddings.npy  # Cached embeddings
├── .env                     # Configuration (API keys)
├── requirements.txt         # Python dependencies
├── render.yaml              # Deployment configuration
└── venv/                    # Virtual environment
```

### main.py: The Entry Point

```python
from fastapi import FastAPI
# FastAPI framework

from fastapi.middleware.cors import CORSMiddleware
# Enable cross-origin requests

from pydantic import BaseModel
# Data validation

from dotenv import load_dotenv
# Load environment variables

from app.rag_engine import RAGEngine
# Import RAG logic

load_dotenv()
# Load .env file

app = FastAPI()
# Create app instance

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Allow frontend to make requests

rag = RAGEngine()
# Initialize RAG engine once

class Query(BaseModel):
    session_id: str
    question: str
# Define request schema

@app.post("/ask")
def ask(q: Query):
    return rag.query(q.question, q.session_id)
# Handle POST requests to /ask endpoint
```

### How It Works

1. **User visits** http://localhost:4200
2. **Frontend sends** `POST /ask` with question
3. **FastAPI receives** and validates request
4. **RAGEngine processes** the question
5. **Response sent** back as JSON
6. **Frontend displays** answer

### packages in requirements.txt

```
fastapi==0.110.0          # Web framework
uvicorn==0.29.0           # ASGI server
google-generativeai==0.5.0 # Gemini AI
python-dotenv==1.0.1      # Environment variables
numpy==1.26.4             # Numerical computing
faiss-cpu==1.7.4          # Vector search
```

---

## Frontend Deep Dive

### File Structure  

```
frontend/
├── src/
│   ├── app/
│   │   ├── app.component.ts          # Root component
│   │   ├── app.component.html        # Root template
│   │   ├── app.component.css         # Root styles
│   │   ├── app.module.ts             # Module definition
│   │   └── services/
│   │       ├── chat.component.ts     # Chat logic
│   │       ├── chat.component.html   # Chat template
│   │       ├── chat.component.css    # Chat styles
│   │       └── chat.service.ts       # API client
│   ├── environments/
│   │   ├── environment.ts            # Dev config
│   │   └── environment.prod.ts       # Prod config
│   ├── styles.css                    # Global styles
│   ├── index.html                    # HTML entry point
│   └── main.ts                       # Angular bootstrap
├── angular.json                      # Angular CLI config
├── package.json                      # Dependencies
└── tsconfig.json                     # TypeScript config
```

### How Angular Works

```
1. User opens browser
   ↓
2. Browser loads index.html
   <app-root></app-root>
   ↓
3. Angular loads main.ts
   ↓
4. Bootstraps AppModule
   ↓
5. Creates AppComponent
   Replaces <app-root> with template
   ↓
6. AppComponent loads ChatComponent
   ↓
7. ChatComponent renders chat interface
   ↓
8. User interacts with interface
   ↓
9. Events trigger methods
   ↓
10. Methods call ChatService
    ↓
11. ChatService makes HTTP request
    ↓
12. Response arrives
    ↓
13. Component updates template
    ↓
14. User sees result
```

### TypeScript: Typed JavaScript

```typescript
// Variables with types
let session_id: string = "user123";
let score: number = 0.95;
let messages: boolean = true;

// Arrays with types
let errors: string[] = ["Error1", "Error2"];

// Functions with types
function addNumbers(a: number, b: number): number {
    return a + b;
}

// Interfaces (define structure)
interface Message {
    role: 'user' | 'bot';
    text: string;
    sources?: string[];
}

const msg: Message = {
    role: 'bot',
    text: 'Answer...',
    sources: ['Guide1']
};
```

---

## Deployment Guide

### Option 1: Render (Backend) + Vercel (Frontend)

*Most popular free tier combination*

**Backend on Render:**

1. Push code to GitHub
2. Go to render.com
3. New → Web Service
4. Select repository
5. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment: `GEMINI_API_KEY=your-key`
7. Deploy!

**Frontend on Vercel:**

1. Go to vercel.com
2. Import Project
3. Select `frontend` folder
4. Build settings (auto-detected)
5. Deploy!

**Update URLs:**

```typescript
// frontend/src/environments/environment.prod.ts
export const environment = {
  production: true,
  backendUrl: 'https://your-render-app.onrender.com'
};
```

### Cost Analysis

| Service | Monthly | Notes |
|---------|---------|-------|
| Render (Backend) | Free | Sleeps unpopular after 15 min |
| Vercel (Frontend) | Free | Full features |
| Total | **Free** | ✓ Production ready |

### Upgrading When You Need More

- **Render**: $7/month → Always on
- **Vercel**: $20+/month → Advanced features

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Cause**: Running from wrong directory

**Solution**: 
```bash
cd backend  # Be in backend directory
uvicorn app.main:app --reload
```

**Problem**: `EnvironmentError: GEMINI_API_KEY not found`

**Cause**: .env file missing or incomplete

**Solution**:
```bash
cp .env.example .env
# Edit .env and add your actual API key
```

**Problem**: `FileNotFoundError: erp_chunks.json not found`

**Cause**: Data file missing

**Solution**: Check `backend/data/` folder exists with JSON file

### Frontend Issues

**Problem**: `Can't find module '@angular/core'`

**Cause**: Dependencies not installed

**Solution**:
```bash
npm install
```

**Problem**: CORS error in browser console

**Cause**: Backend not allowing frontend domain

**Solution**: Update `backend/app/main.py`:
```python
allow_origins=[
    "http://localhost:4200",  # Dev
    "https://your-vercel-app.vercel.app"  # Production
]
```

**Problem**: Button doesn't respond

**Cause**: Chat service not configured correctly

**Solution**: Check `environment.ts` has correct backend URL

### Deployment Issues

**Problem**: Render backend times out on first request

**Cause**: Free tier sleeps after inactivity

**Solution**: Wait 30-40 seconds for wake-up, or upgrade

**Problem**: Frontend can't reach backend

**Cause**: URL mismatch

**Solution**:
1. Check Render URL is correct
2. Update `environment.prod.ts`
3. Redeploy frontend

---

## Learning Resources

### Programming Basics
- **Python**: [Automate the Boring Stuff](https://automatetheboringstuff.com/)
- **TypeScript**: [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- **Web Dev**: [MDN Web Docs](https://developer.mozilla.org/)

### Web Frameworks
- **FastAPI**: [Official Tutorial](https://fastapi.tiangolo.com/tutorial/)
- **Angular**: [Official Tutorial](https://angular.io/start)

### AI/ML Concepts
- **Embeddings**: [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- **Vector Databases**: [Pinecone Learn](https://www.pinecone.io/learn/)
- **RAG**: [Official RAG Guide (LangChain)](https://python.langchain.com/docs/modules/retrieval/rag)
- **Google Gemini**: [AI Studio](https://makersuite.google.com/)

### Deployment
- **Render**: [Deploy Python App](https://render.com/docs/deploy-python-fastapi)
- **Vercel**: [Deploy Angular](https://vercel.com/docs/frameworks/angular)

---

## Next Steps

### Immediate (This Week)
- [ ] Set up locally and run
- [ ] Read through main.py
- [ ] Modify prompts in rag_engine.py
- [ ] Test with different questions

### Soon (This Month)
- [ ] Deploy to Render + Vercel
- [ ] Share with friends
- [ ] Add more ERP documents
- [ ] Implement new features

### Future (This Quarter)
- [ ] Add user authentication
- [ ] Store conversations in database
- [ ] Multi-language support
- [ ] Advanced search features

### Career Growth
- [ ] Master FastAPI
- [ ] Become Angular expert
- [ ] Study advanced RAG techniques
- [ ] Build larger AI projects
- [ ] Deploy to enterprise clients

---

## Quick Reference

### Commands

```bash
# Development
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload
cd frontend && npm start

# Deployment
# Render: git push origin main
# Vercel: vercel deploy

# Utilities
python -m venv venv          # Create virtual env
pip install -r requirements.txt  # Install deps
npm install                  # Install frontend deps
```

### URLs

- **Local Frontend**: http://localhost:4200
- **Local API**: http://localhost:10000
- **API Docs**: http://localhost:10000/docs
- **Deployed**: Check Render/Vercel dashboards

### Key Files to Understand

1. **Backend Logic**
   - `backend/app/main.py` - Entry point
   - `backend/app/rag_engine.py` - Core logic
   - `backend/data/erp_chunks.json` - Knowledge base

2. **Frontend**
   - `frontend/src/app/app.component.ts` - Root
   - `frontend/src/app/services/chat.component.ts` - Chat logic
   - `frontend/src/environments/environment.ts` - Config

3. **Configuration**
   - `backend/.env` - API keys
   - `frontend/package.json` - Dependencies
   - `render.yaml` - Deployment config

---

## Conclusion

You now have:
- ✅ Complete understanding of the project
- ✅ Knowledge to modify and extend it
- ✅ Deployment strategy
- ✅ Learning resources

Next: Deploy,share with friends, and build amazing things!

---

## Document Information

- **Written for**: Beginners and aspiring AI/ML engineers
- **Skill Level**: No prior programming required
- **Time to Complete**: 4-8 hours (depending on depth)
- **Last Updated**: April 18, 2026
- **Version**: 1.0

---

**Happy Learning! 🚀**

*"The best way to learn is to build. Build this project, modify it, break it, learn from it, and then build something greater!"*

