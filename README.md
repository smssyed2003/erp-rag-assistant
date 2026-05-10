# ERP RAG System v1.0

**Production-Ready ERP AI Assistant with Retrieval-Augmented Generation**

An intelligent ERP assistant that helps users ask questions about ERP systems and get accurate, context-aware answers with source citations. Built with modern web technologies and AI.

---

## 🎯 What This Project Does

- **Intelligent Q&A**: Users ask questions about ERP concepts, workflows, and procedures
- **Accurate Answers**: Uses Retrieval-Augmented Generation (RAG) to find real documents and generate answers
- **Source Citations**: Shows which documents were used to generate the answer
- **Smart Agent**: Can decide whether to search documents or answer from general knowledge
- **Session Memory**: Remembers context across multiple questions in the same session
- **Production Ready**: Fully deployed and accessible 24/7

---

## 📁 Project Structure

```
ERP_RAG_System_V0.1/
├── backend/                    # FastAPI backend service (Python)
│   ├── app/
│   │   ├── main.py            # FastAPI app & endpoints
│   │   ├── agent.py           # AI Agent orchestration
│   │   ├── planner.py         # Decision-making logic
│   │   ├── rag_engine.py      # RAG pipeline
│   │   ├── retrieval.py       # Document search
│   │   ├── tool_registry.py   # Tool management
│   │   ├── memory.py          # Session memory
│   │   ├── logger.py          # Logging system
│   │   └── tools/             # Available tools
│   ├── requirements.txt        # Python dependencies
│   └── .env                   # Environment variables (create this)
│
├── frontend/                   # Angular frontend (TypeScript)
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.ts    # Root component
│   │   │   ├── app.module.ts       # Module configuration
│   │   │   └── services/
│   │   │       ├── chat.component.ts    # Chat logic
│   │   │       ├── chat.service.ts      # Backend communication
│   │   │       └── chat.component.css   # Chat styles
│   │   ├── environments/       # Environment configs
│   │   ├── styles.css         # Global styles
│   │   └── main.ts            # Bootstrap entry point
│   ├── angular.json           # Angular configuration
│   ├── package.json           # NPM dependencies
│   └── README.md              # Frontend docs
│
├── data/                       # ERP knowledge base
│   ├── erp_chunks.json        # ERP documents
│   └── erp_chunks_embeddings.npy  # Vector embeddings
│
├── docs/                       # Documentation
│   ├── ERP_AI_Assistant_Documentation.md  # Beginner guide
│   ├── CODE_ARCHITECTURE.md    # Code explanation (READ THIS!)
│   └── generate_pdf.py        # PDF generator
│
├── SETUP.md                   # Local development setup
├── DEPLOYMENT.md              # Production deployment guide
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key (free at https://aistudio.google.com/apikey)

### 3-Step Setup

**Step 1: Get API Key**
```bash
# Go to https://aistudio.google.com/apikey
# Click "Create API key" and copy it
```

**Step 2: Configure Backend**
```bash
cd backend

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# OR
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo GEMINI_API_KEY=your_key_here > .env
```

**Step 3: Run Servers**
```bash
# Terminal 1 - Backend
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm start
```

**Access the app**: http://localhost:4200

---

## 📚 Documentation Guide

| Document | For Whom | Read If |
|----------|----------|---------|
| [SETUP.md](SETUP.md) | Developers | You want to run locally |
| [DEPLOYMENT.md](DEPLOYMENT.md) | DevOps/Deployment | You want to deploy to production |
| [docs/ERP_AI_Assistant_Documentation.md](docs/ERP_AI_Assistant_Documentation.md) | Everyone | You're new to the project |
| [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md) | **Developers - START HERE** | You want to understand how code works |
| [frontend/README.md](frontend/README.md) | Frontend Developers | You're working on the Angular UI |

---

## 🏗️ How It Works

### Simple Overview
```
User asks question in chat
        ↓
Frontend sends to Backend
        ↓
Agent decides: Search documents? Or answer from knowledge?
        ↓
RAG Engine retrieves relevant ERP documents
        ↓
Gemini AI generates answer using those documents
        ↓
Response sent back with sources
        ↓
User sees answer + which documents it came from
```

### Architecture Diagram
```
┌─────────────────────────┐
│   Frontend (Angular)    │
│   localhost:4200        │
└────────────┬────────────┘
             │ HTTP
             ↓
┌─────────────────────────┐
│   Backend (FastAPI)     │
│   localhost:8000        │
│  ├─ Agent               │
│  ├─ RAG Engine          │
│  └─ Document Search     │
└────────────┬────────────┘
             │ API Calls
             ↓
┌─────────────────────────┐
│  Google Gemini API      │
│  (AI/LLM)               │
└─────────────────────────┘
```

---

## 🔌 API Endpoints

### POST /ask
**Direct RAG search** (no agent planning)

Request:
```json
{
  "question": "How do I process a purchase order?",
  "session_id": "user123"
}
```

Response:
```json
{
  "answer": "To process a purchase order...",
  "sources": ["PO_Procedure.pdf", "Finance_Guide.md"]
}
```

### POST /agent-ask
**Smart agent routing** (decides which tool to use)

Request:
```json
{
  "question": "What is an ERP system?",
  "session_id": "user123"
}
```

Response:
```json
{
  "answer": "An ERP system is...",
  "sources": ["ERP_Basics.pdf"],
  "steps": [
    {
      "action": "rag_search",
      "result": {...}
    }
  ]
}
```

---

## 🛠️ Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Python + FastAPI | REST API, business logic |
| Frontend | Angular 17 + TypeScript | Web user interface |
| AI/LLM | Google Gemini API | Answer generation |
| Search | FAISS + BM25 | Vector & keyword search |
| Deployment | Render + Vercel | Production hosting |

---

## 📖 Code Structure Explained

**Want to understand the code?** Read [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md) for:
- Detailed explanation of every file
- How components communicate
- Request/response flow diagrams
- Code examples with explanations

---

## 🚢 Production Deployment

The system is deployed on:
- **Backend**: Render.com (https://erp-rag-assistant-1.onrender.com/)
- **Frontend**: Vercel (https://erp-rag-assistant.vercel.app/)

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 🤝 Contributing

1. Clone the repository
2. Create a feature branch
3. Make changes
4. Test locally (see SETUP.md)
5. Push and create a Pull Request

---

## ❓ FAQ

**Q: Do I need AI knowledge to understand this?**  
A: No! See [docs/ERP_AI_Assistant_Documentation.md](docs/ERP_AI_Assistant_Documentation.md) for beginner-friendly explanations.

**Q: How do I run this locally?**  
A: Follow the Quick Start section above or see [SETUP.md](SETUP.md) for detailed instructions.

**Q: How do I deploy to production?**  
A: See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step deployment guide.

**Q: What if something breaks?**  
A: Check the logs in `backend/logs/` and see troubleshooting in [SETUP.md](SETUP.md).

---

## 📝 License

This project is proprietary. All rights reserved.

---

## 🎓 Learning Path

**For Beginners:**
1. Read this README
2. Read [docs/ERP_AI_Assistant_Documentation.md](docs/ERP_AI_Assistant_Documentation.md)
3. Run locally following SETUP.md
4. Ask questions in the app and see how it works

**For Developers:**
1. Read [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md)
2. Explore backend code: `backend/app/`
3. Explore frontend code: `frontend/src/app/`
4. Run locally and debug
5. Make modifications

**For DevOps:**
1. Read [DEPLOYMENT.md](DEPLOYMENT.md)
2. Set up Render backend
3. Set up Vercel frontend
4. Configure environment variables
5. Monitor production logs

---

## 📞 Support

- **Questions?** Check the documentation first
- **Found a bug?** Create an issue on GitHub
- **Want to contribute?** See contributing section

---

**Status**: ✅ Production Ready  
**Last Updated**: May 2026  
**Version**: 1.0
