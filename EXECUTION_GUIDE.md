# 🎯 DEPLOYMENT EXECUTION GUIDE

**Follow these steps in order. Each section takes 5-10 minutes.**

---

## ✅ PRE-DEPLOYMENT VERIFICATION

Before starting, verify everything is working locally:

### Check Backend
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 10000
```
✅ Should show: `Uvicorn running on http://0.0.0.0:10000`

### Check Frontend (new terminal)
```powershell
cd frontend
npm start
```
✅ Should show: `Angular Live Development Server is listening on localhost:4200`

### Manual Test
1. Open: http://localhost:4200
2. Type: "What is purchase order?"
3. Click Send
4. ✅ Should get response

---

## STEP 1️⃣: SETUP GITHUB (5 minutes)

### 1.1 Create GitHub Repository

1. Open: https://github.com/new
2. **Repository name**: `erp-rag-system`
3. **Description**: "AI-powered ERP chatbot with RAG and embeddings"
4. **Public**: ✓ (checked)
5. Click **Create repository**

### 1.2 Initialize Local Git

Open PowerShell in project root:

```powershell
# Go to project root
cd C:\Users\sayed\OneDrive\Desktop\Projects\ERP_RAG_System_V0.1

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: ERP RAG System with FastAPI backend and Angular frontend"

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/erp-rag-system.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

### 1.3 Verify on GitHub

Open: https://github.com/YOUR_USERNAME/erp-rag-system

✅ You should see your files there!

---

## STEP 2️⃣: DEPLOY BACKEND TO RENDER (10 minutes)

### 2.1 Create Render Account

1. Open: https://render.com
2. Click **Sign up**
3. Select **Continue with GitHub** (easier)
4. Authorize Render
5. Done!

### 2.2 Create Backend Service

In Render Dashboard:
1. Click **+ New**
2. Select **Web Service**
3. Under "Connect a repository", find your `erp-rag-system` repo
4. Click **Connect**

### 2.3 Configure Service

Fill in the form:

```
Name: erp-rag-backend
Region: (pick closest to you - e.g., Ohio)
Branch: main
Runtime: Python 3.10
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 2.4 Add API Key

Click **Environment** tab:

```
GEMINI_API_KEY = AIzaSyA_xxxxxxxxxxxxx
```

(Get your key from: https://makersuite.google.com/)

### 2.5 Deploy

Click **Create Web Service**

**Wait 3-5 minutes...**

✅ When done, you'll see:
```
✓ Your service is live
https://erp-rag-backend.onrender.com
```

### 2.6 Test Backend

Open: https://YOUR_BACKEND_URL.onrender.com/docs

✅ You should see interactive API documentation (Swagger UI)

**💾 Save your Render backend URL** - you'll need it!

---

## STEP 3️⃣: UPDATE CONFIGURATION (5 minutes)

### 3.1 Update Production Environment

Edit: `frontend/src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  backendUrl: 'https://YOUR_RENDER_BACKEND_URL.onrender.com'  // PASTE YOUR RENDER URL HERE
};
```

### 3.2 Update Backend CORS

Edit: `backend/app/main.py`

Find the CORS section (around line 25) and add:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",              # Keep for development
        "https://erp-rag-frontend.vercel.app"  # Vercel frontend (full URL after deployment)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3.3 Commit & Push

```powershell
cd C:\Users\sayed\OneDrive\Desktop\Projects\ERP_RAG_System_V0.1

git add .
git commit -m "Update production configuration for Render and Vercel"
git push origin main
```

✅ Changes pushed to GitHub!

---

## STEP 4️⃣: DEPLOY FRONTEND TO VERCEL (10 minutes)

### 4.1 Create Vercel Account

1. Open: https://vercel.com
2. Click **Sign up**
3. Click **Continue with GitHub** (recommended)
4. Authorize Vercel
5. Done!

### 4.2 Import Project

In Vercel Dashboard:
1. Click **Add New** → **Project**
2. Search for `erp-rag-system`
3. Click **Import**

### 4.3 Configure Project

**Project Settings**:
- **Project Name**: `erp-rag-frontend`
- **Framework**: Should show `Angular` ✓
- **Root Directory**: `./frontend`
- **Build Command**: Auto-detected (should be fine)
- **Output Directory**: `.angular/cache` or `dist`

### 4.4 Deploy

Click **Deploy**

**Wait 2-3 minutes...**

✅ When done, you'll see:
```
✓ Congratulations! Your project has been successfully deployed
https://erp-rag-frontend.vercel.app
```

**💾 Save your Vercel frontend URL** - you'll need it!

### 4.5 Test Frontend

Open: https://YOUR_FRONTEND_URL.vercel.app

✅ You should see the chat interface!

---

## STEP 5️⃣: FINAL CONFIGURATION (5 minutes)

### 5.1 Update Backend CORS with Vercel URL

Now that you have your Vercel URL, update backend:

Edit: `backend/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://erp-rag-frontend.vercel.app"  # YOUR ACTUAL VERCEL URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.2 Commit & Push

```powershell
git add backend/app/main.py
git commit -m "Update CORS with Vercel frontend URL"
git push origin main
```

### 5.3 Trigger Backend Redeploy

1. Go to Render Dashboard
2. Click your `erp-rag-backend` service
3. Click **Manual Deploy** → **Deploy latest commit**
4. Wait 2-3 minutes

---

## STEP 6️⃣: COMPREHENSIVE TEST (5 minutes)

### 6.1 Test Frontend

Open: https://YOUR_VERCEL_URL.vercel.app

✅ Chat interface loads

### 6.2 Send a Message

1. Type in chat box: "What is a purchase order?"
2. Click **Send**
3. Wait for response...

✅ Should see AI response with sources!

### 6.3 Check Console for Errors

Press **F12** → **Console** tab

✅ Should be clear (no red errors)

### 6.4 If Issues Occur

**Error**: "Failed to fetch"
- **Fix**: Verify Render URL in `environment.prod.ts`
- Redeploy frontend

**Error**: CORS error
- **Fix**: Check backend CORS configuration
- Verify Vercel URL in list
- Trigger backend redeploy

**Error**: Long wait/timeout
- **Fix**: Render free tier sleeps. Wait 30 seconds and retry.

---

## STEP 7️⃣: GENERATE PDFS (10 minutes)

### Option A: Automatic Script (Recommended)

**First, install Pandoc** (one-time):

```powershell
# Using Chocolatey
choco install pandoc

# Or download: https://pandoc.org/installing.html
```

**Run PDF generation**:

```powershell
cd C:\Users\sayed\OneDrive\Desktop\Projects\ERP_RAG_System_V0.1

# Run PowerShell script
.\generate_pdfs.ps1
```

Or run batch script:
```powershell
.\generate_pdfs.bat
```

✅ PDFs will be created in `pdfs/` folder!

### Option B: Manual (if script fails)

```powershell
cd C:\Users\sayed\OneDrive\Desktop\Projects\ERP_RAG_System_V0.1

# Complete Guide PDF
pandoc docs/ERP_RAG_Complete_Guide.md -o ERP_RAG_Complete_Guide.pdf --pdf-engine=xelatex -V papersize:a4 --toc

# All-in-one PDF
pandoc docs/ERP_RAG_Complete_Guide.md docs/01-DETAILED-MARKDOWN.md DEPLOYMENT.md -o ERP_RAG_COMPLETE_DOCUMENTATION.pdf --pdf-engine=xelatex -V papersize:a4 --toc
```

✅ PDFs created in project root!

---

## ✨ DEPLOYMENT COMPLETE!

### Save These URLs

```
🎯 Frontend (Vercel):
https://your-vercel-url.vercel.app

🔌 Backend (Render):
https://your-render-url.onrender.com

📖 API Docs:
https://your-render-url.onrender.com/docs

📦 GitHub:
https://github.com/YOUR_USERNAME/erp-rag-system

📄 PDF Docs:
pdfs/ERP_RAG_Complete_Guide.pdf
```

### Share with Friends

Email Template:
```
Subject: I built an AI chatbot! Check it out 🤖

Hi [Friend],

I've built an AI-powered ERP assistant that answers questions about business processes!

🎯 Live Demo: https://your-frontend-url.vercel.app
📖 Documentation: docs/ERP_RAG_Complete_Guide.pdf
💻 GitHub: https://github.com/your-username/erp-rag-system

Try asking:
- "What is a purchase order?"
- "Explain the P2P process"
- "How to create a vendor master?"

See you got AI powers! 🚀
```

---

## 🎯 Quick Verification Checklist

- [ ] GitHub repo created and files pushed
- [ ] Backend deployed to Render
- [ ] Backend /docs page loads
- [ ] Frontend deployed to Vercel
- [ ] Frontend chat page loads
- [ ] Can send message and get response
- [ ] No CORS errors in console
- [ ] PDF files generated
- [ ] URLs saved
- [ ] Ready to share!

---

## 📞 Support

### Common Issues & Fixes

**Backend won't deploy**
- Check Root Directory is `backend`
- Check Python version is 3.10
- Verify `requirements.txt` exists

**Frontend won't build**
- Run locally: `npm run build`
- Check for TypeScript errors
- Clear cache: `npm cache clean --force`

**Can't send messages**
- Check browser console (F12)
- Verify backend URL in environment.prod.ts
- Wait 40 seconds for Render wake-up

**Can't install Pandoc**
- Download from: https://pandoc.org/installing.html
- Or use online converter: https://cloudconvert.com/md-to-pdf

---

## 🎉 You're Done!

Your AI ERP assistant is now:
- ✅ Live on the internet
- ✅ Fully functional
- ✅ Ready to share
- ✅ Completely free

**Next**: Share the frontend URL with friends and see them amazed! 🚀

---

**Total Time**: ~45 minutes  
**Cost**: $0/month  
**Difficulty**: Easy (follow steps)

Good luck! 🎊

