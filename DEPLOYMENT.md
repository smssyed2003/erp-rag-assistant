# 🚀 Deployment Guide

Complete guide to deploy the ERP RAG Assistant to free tier services.

## Backend Deployment (Render.com)

### Prerequisites
- GitHub account with your project repo
- Render account (free tier available)

### Step 1: Prepare Your Repository

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/erp-rag-system.git
git push -u origin main
```

2. Ensure `.env` is NOT committed (add to `.gitignore`):
```
.env
venv/
.DS_Store
node_modules/
dist/
```

### Step 2: Create Render Web Service

1. Go to [render.com](https://render.com)
2. Sign up and connect your GitHub
3. Click "New +" → "Web Service"
4. Select your GitHub repository
5. Fill in the form:
   - **Name**: `erp-rag-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables

1. In Render dashboard, click "Environment"
2. Add `GEMINI_API_KEY` with your actual key
3. Click "Deploy"

**Backend will be available at**: `https://erp-rag-backend.onrender.com`

### Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'app'`
- **Solution**: Ensure `backend/app/__init__.py` exists

**Issue**: CORS errors from frontend
- **Solution**: Update `backend/app/main.py` with correct frontend domain

**Issue**: Timeout on large embeddings
- **Solution**: Build index locally, cache embeddings

---

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (free tier)
- GitHub account

### Step 1: Configure for Production

Update `frontend/src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  backendUrl: 'https://erp-rag-backend.onrender.com'  // Your Render URL
};
```

### Step 2: Deploy to Vercel

**Option A: Using Vercel CLI**
```bash
npm install -g vercel
cd frontend
vercel
```

**Option B: Using Vercel Dashboard**

1. Go to [vercel.com](https://vercel.com)
2. Sign up and import your GitHub repo
3. Select `frontend` as root directory
4. Build settings (auto-detected):
   - **Framework**: Angular
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist/erp-rag-frontend`

### Step 3: Configure Deployment

1. Set environment variables:
   - Go to Settings → Environment Variables
   - Add any needed vars (usually none for frontend)

2. Click "Deploy"

**Frontend will be available at**: `https://your-project.vercel.app`

---

## Alternative Free Deployments

### For Backend:
- **Railway**: 5GB/month free
- **Heroku**: Paused (was free, now paid only)
- **Replit**: Good for simple apps
- **PythonAnywhere**: $5/month

### For Frontend:
- **Netlify**: Same as Vercel, excellent free tier
- **GitHub Pages**: Good for static sites
- **Firebase Hosting**: Good free tier

---

## Post-Deployment Steps

### 1. Update Your Local Config
```typescript
// frontend/src/environments/environment.ts
export const environment = {
  production: false,
  backendUrl: 'http://localhost:10000'  // Local development
};
```

### 2. Test the Deployment
1. Visit your Vercel frontend URL
2. Ask a test question
3. Check browser console for errors
4. Check Render logs for backend issues

### 3. Set Custom Domain (Optional)
- Vercel: Settings → Domains → Add Domain
- Render: Settings → Custom Domains

### 4. Enable HTTPS
- Both services auto-enable HTTPS ✅

---

## Monitoring and Debugging

### View Logs

**Render Backend Logs:**
- Dashboard → Service → Logs

**Vercel Frontend Logs:**
- Deployments → Select deployment → Click logs

### Common Issues

**CORS Errors**:
```python
# In backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**API Timeout**:
- Render free tier sleeps after 15 mins of inactivity
- First request takes 30 seconds
- Upgrade to paid tier for always-on

**Can't Find Module**:
- Check `requirements.txt` has all dependencies
- Verify `__init__.py` files exist in app folders

---

## Cost Analysis

| Service | Backend | Frontend | Monthly Cost |
|---------|---------|----------|--------------|
| Render + Vercel | Free (with sleep) | Free | $0 |
| Railway | $5/month | Free | $5 |
| Firebase | $0-28 | $0-28 | Variable |
| AWS Free Tier | $0-12 | $0-12 | Variable |

**Recommendation**: Start with Render + Vercel (Free), upgrade if needed.

---

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ✅ Update environment URLs
4. ✅ Test the full deployed system
5. ✅ Share deployed URLs with your friends!

