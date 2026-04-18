# ERP RAG Assistant

An intelligent ERP assistant that provides contextual, step-by-step answers for Finance, P2P, and O2C processes using Retrieval-Augmented Generation (RAG).

## 🚀 Features

- **Contextual Q&A**: Get step-by-step ERP guidance with relevant documentation context
- **Conversational Memory**: Maintains chat history for follow-up questions
- **Vector Search**: Fast retrieval using FAISS and Gemini embeddings
- **Modern UI**: Clean Angular interface with real-time responses

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Retrieval Engine**: FAISS vector search with Gemini embeddings
- **RAG Pipeline**: Context retrieval + conversational memory + LLM generation
- **API**: RESTful endpoints with CORS support

### Frontend (Angular)
- **Chat Interface**: Real-time messaging with loading states
- **Service Layer**: HTTP client for backend communication
- **Responsive Design**: Mobile-friendly UI

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, FAISS, Google Gemini AI
- **Frontend**: Angular 17, TypeScript, RxJS
- **Deployment**: Render (backend), Vercel/Netlify (frontend)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Copy .env.example to .env and add your GEMINI_API_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 10000
```

### Frontend Setup

```bash
cd frontend
npm install
npm start  # Runs on http://localhost:4200
```

### API Usage

```bash
curl -X POST "http://localhost:10000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How to create a purchase order?", "session_id": "user123"}'
```

## 📁 Project Structure

```
erp-rag-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── rag_engine.py    # RAG orchestration
│   │   ├── retrieval.py     # Vector search & LLM
│   │   ├── memory.py        # Session memory
│   │   └── utils.py         # Helpers
│   ├── data/
│   │   └── erp_chunks.json  # Knowledge base
│   ├── requirements.txt
│   ├── render.yaml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.*    # Root component
│   │   │   ├── app.module.ts      # Angular module
│   │   │   └── services/
│   │   │       ├── chat.component.*  # Chat UI
│   │   │       └── chat.service.ts   # API client
│   │   ├── environments/           # Config
│   │   └── styles.css
│   ├── angular.json
│   └── package.json
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create `.env` in backend directory:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### Frontend Config

Update `frontend/src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  backendUrl: 'http://localhost:10000'  // or your deployed URL
};
```

## 🚀 Deployment

### Backend (Render)

1. Connect GitHub repo to Render
2. Use `render.yaml` for service config
3. Set `GEMINI_API_KEY` in environment variables

### Frontend (Vercel/Netlify)

1. Build: `npm run build`
2. Deploy `dist/` folder
3. Update `environment.prod.ts` with production backend URL

## 🤖 AI Concepts Used

### Retrieval-Augmented Generation (RAG)
- **Retrieval**: Vector similarity search finds relevant ERP docs
- **Augmentation**: Retrieved context + user question fed to LLM
- **Generation**: LLM produces step-by-step answers

### Vector Embeddings
- Text converted to high-dimensional vectors
- FAISS enables fast nearest-neighbor search
- Semantic similarity drives document retrieval

### Conversational Memory
- Session-based chat history storage
- Context window management (last 5 exchanges)
- Memory injected into prompts for continuity

## 📚 Learning Path

Since you have C, Python OOP, and data science foundations:

### 1. **Web Development Basics**
- HTTP/REST APIs (FastAPI, Angular services)
- Frontend-backend communication
- CORS, middleware, routing

### 2. **AI/ML Engineering**
- Vector databases (FAISS, Pinecone)
- LLM APIs (OpenAI, Anthropic, Google)
- Prompt engineering
- Model evaluation & deployment

### 3. **Full-Stack Development**
- Angular components, services, modules
- FastAPI routers, dependencies, validation
- Database integration (PostgreSQL, MongoDB)
- Containerization (Docker)

### 4. **Production Engineering**
- CI/CD pipelines
- Cloud deployment (AWS, GCP, Azure)
- Monitoring & logging
- Security best practices

## 🎯 Next Steps

1. **Get Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Test Locally**: Run both backend and frontend
3. **Add Features**: File upload, user auth, advanced search
4. **Deploy**: Push to production
5. **Scale**: Add more ERP domains, improve accuracy

## 📞 Support

Questions? Open an issue or reach out!

---

*Built with ❤️ for ERP professionals*</content>
<parameter name="filePath">c:\Users\sayed\OneDrive\Desktop\Projects\ERP_RAG_System_V0.1\README.md