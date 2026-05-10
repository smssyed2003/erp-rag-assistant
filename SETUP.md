# ERP RAG System - Setup & Troubleshooting Guide

## Prerequisites
- Python 3.10+ installed
- Git installed
- Gemini API key (free tier available)

## Local Development Setup

### Step 1: Get Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API key"
3. Copy the API key

### Step 2: Configure Backend Environment
1. Navigate to `backend/` directory
2. Open `.env` file
3. Paste your API key after `GEMINI_API_KEY=`
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
4. Save the file

### Step 3: Install Dependencies & Run Backend

#### Using Virtual Environment (Recommended)
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

The backend will start at `http://127.0.0.1:8000`

#### Using System Python (Not Recommended)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Step 4: Test the Backend
```bash
# In a new terminal, test the health endpoint
curl http://127.0.0.1:8000/

# Test the agent endpoint
curl -X POST http://127.0.0.1:8000/agent-ask \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "question": "How do I manage inventory?"
  }'
```

## Common Errors & Solutions

### Error 1: FileNotFoundError - data/erp_chunks.json
**Message**: `FileNotFoundError: Required data file not found`

**Cause**: Backend can't locate the data file

**Solution**:
- Ensure you're in the `backend/` directory
- Verify `data/erp_chunks.json` exists in the root project folder
- Check that the path is correct by running:
  ```bash
  ls ../data/erp_chunks.json  # On Linux/macOS
  dir ..\data\erp_chunks.json  # On Windows
  ```

### Error 2: GEMINI_API_KEY Not Found
**Message**: `OSError: Environment variable 'GEMINI_API_KEY' is required but was not found`

**Cause**: API key not set in `.env` file

**Solution**:
1. Check `.env` file exists: `backend/.env`
2. Verify it contains: `GEMINI_API_KEY=your_key_here`
3. Restart the server: `uvicorn app.main:app --reload`

### Error 3: Embedding Service Unavailable
**Message**: `RuntimeError: Embedding service unavailable`

**Cause**: Gemini API is unreachable (no internet or invalid API key)

**Solution**:
- Verify internet connection
- Check API key is valid: https://aistudio.google.com/apikey
- Ensure `.env` file is properly formatted (no extra quotes or spaces)
- Verify file is in `backend/` directory
- Restart the server

### Error 4: Port 8000 Already in Use
**Message**: `OSError: [Errno 48] Address already in use`

**Cause**: Port 8000 is being used by another process

**Solution**:
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001

# Or kill the process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

## Production Deployment

### Deploy Backend to Render

1. **Create Render Account**: https://render.com
2. **Connect GitHub Repository**
3. **Create New Web Service**:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. **Set Environment Variables**:
   - Go to Service Settings > Environment
   - Add: `GEMINI_API_KEY=your_api_key`
5. **Deploy**: Push to GitHub or click Deploy

### Deploy Frontend to Vercel

1. **Create Vercel Account**: https://vercel.com
2. **Connect GitHub Repository**
3. **Configure Build Settings**:
   - Framework: Angular
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Set Environment Variables**:
   - Add: `VITE_BACKEND_URL=https://your-render-backend.onrender.com`
5. **Deploy**: Click Deploy

### Configure Frontend for Production
Update `frontend/src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  backendUrl: 'https://your-render-backend.onrender.com'
};
```

## Verification Checklist

- [ ] Python 3.10+ installed
- [ ] Gemini API key obtained
- [ ] `.env` file created with API key
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend starts without errors
- [ ] Health endpoint responds: `curl http://127.0.0.1:8000/`
- [ ] Agent endpoint works with test query
- [ ] Frontend loads (if running locally)

## Still Having Issues?

1. Check the error message carefully - it usually indicates the exact problem
2. Ensure all files are in correct locations
3. Verify API key is valid at https://aistudio.google.com/apikey
4. Check internet connection
5. Try restarting the terminal/IDE
6. Delete `venv/` folder and recreate it
7. Check GitHub Issues for similar problems

## File Structure Reference

```
ERP_RAG_System_V0.1/
├── backend/
│   ├── .env                 # <- Add GEMINI_API_KEY here
│   ├── requirements.txt     # Backend dependencies
│   ├── venv/               # Virtual environment (auto-created)
│   └── app/
│       ├── main.py
│       ├── agent.py
│       ├── rag_engine.py
│       ├── retrieval.py
│       └── ...
├── frontend/
│   └── src/
│       ├── main.ts
│       └── environments/
│           └── environment.ts  # Backend URL config
├── data/
│   └── erp_chunks.json      # Knowledge base data
└── README.md
```

## Next Steps

1. ✅ Set up backend locally
2. ✅ Test backend endpoints
3. Run frontend locally (optional)
4. Deploy to production
