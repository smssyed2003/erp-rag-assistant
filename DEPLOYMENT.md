# ERP RAG System - Production Deployment Guide

## Architecture Overview

```
┌─────────────────┐
│   Vercel CDN    │ (Frontend - Angular)
│   (Frontend)    │
└────────┬────────┘
         │
         │ HTTPS
         │
┌────────▼────────┐
│  Render.com     │ (Backend - FastAPI)
│  (Backend API)  │
└────────┬────────┘
         │
         │ HTTPS
         │
┌────────▼────────┐
│  Google Gemini  │ (AI/LLM)
│  (Embeddings &  │
│  Generation)    │
└─────────────────┘
```

## Backend Deployment (Render)

### Prerequisites
- Render.com account (free tier available)
- GitHub repository with code
- Gemini API key

### Step-by-Step Deployment

#### 1. Prepare Repository
```bash
# Make sure all changes are committed
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

#### 2. Create Render Account
- Go to https://render.com
- Sign up with GitHub
- Grant access to your repository

#### 3. Create Web Service
1. Click "New" → "Web Service"
2. Select your GitHub repository
3. Configure settings:
   - **Name**: `erp-rag-api`
   - **Runtime**: `Python 3.10`
   - **Build Command**: 
     ```
     pip install -r backend/requirements.txt
     ```
   - **Start Command**: 
     ```
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
     ```
   - **Instance Type**: `Free` (or `Standard` for better performance)

#### 4. Set Environment Variables
1. In Render dashboard, go to Service → Settings
2. Click "Environment"
3. Add these variables:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

#### 5. Deploy
- Click "Deploy"
- Wait for build to complete
- Note your service URL (e.g., `https://erp-rag-api-xxxx.onrender.com`)

#### 6. Verify Deployment
```bash
# Test health endpoint
curl https://erp-rag-api-xxxx.onrender.com/

# Test agent endpoint
curl -X POST https://erp-rag-api-xxxx.onrender.com/agent-ask \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "question": "How do I manage inventory?"
  }'
```

### Render Cold Start Issue
**Problem**: First request after inactivity takes 30+ seconds

**Solutions**:
1. **Upgrade to Standard Instance** (costs ~$7/month):
   - Removes cold start issue
   - Better performance

2. **Use Render Cron Job** (Free):
   - Create a cron job that pings the API every 5 minutes
   - Keeps the service "warm"
   - Add environment variable: `RENDER_URL=https://erp-rag-api-xxxx.onrender.com`

3. **Implement Uptime Monitor**:
   - Use UptimeRobot (https://uptimerobot.com) - Free tier
   - Ping your API every 5 minutes to prevent cold starts

### Environment Variables for Production

```env
GEMINI_API_KEY=your_production_api_key
```

**Security Notes**:
- Never commit `.env` to Git
- Use Render's environment variable management
- Rotate API keys periodically
- Monitor API usage

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (free tier available)
- GitHub repository
- Backend API URL from Render

### Step-by-Step Deployment

#### 1. Create Vercel Account
- Go to https://vercel.com
- Sign up with GitHub
- Grant access to your repository

#### 2. Create Project
1. Click "Add New" → "Project"
2. Select your GitHub repository
3. Vercel auto-detects it's an Angular project

#### 3. Configure Build Settings
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Root Directory**: `./frontend`

#### 4. Set Environment Variables
In Vercel dashboard:
1. Go to Settings → Environment Variables
2. Add:
   ```
   VITE_BACKEND_URL=https://erp-rag-api-xxxx.onrender.com
   ```

#### 5. Update Frontend Config
Update `frontend/src/environments/environment.prod.ts`:
```typescript
export const environment = {
  production: true,
  backendUrl: 'https://erp-rag-api-xxxx.onrender.com'
};
```

Update `frontend/src/environments/environment.ts` (local development):
```typescript
export const environment = {
  production: false,
  backendUrl: 'http://localhost:8000'
};
```

#### 6. Deploy
- Click "Deploy"
- Wait for build to complete
- Get your production URL (e.g., `https://erp-rag-assistant.vercel.app`)

#### 7. Enable CORS
Make sure backend CORS is configured correctly:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://erp-rag-assistant.vercel.app"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Production Monitoring

### Monitor Backend Health
```bash
# Check API status
curl https://erp-rag-api-xxxx.onrender.com/

# Monitor logs on Render
# Go to Render Dashboard → Logs tab
```

### Monitor Frontend
```bash
# Check deployment on Vercel
# Go to Vercel Dashboard → Deployments tab
```

### Set Up Alerts
1. **Render**: Go to Service → Alerts
2. **Vercel**: Go to Project → Analytics & Monitoring

### API Usage Monitoring
Monitor your Gemini API usage:
- Go to https://aistudio.google.com/billing/overview
- Check usage and quotas
- Set up alerts if needed

## Production Checklist

- [ ] Gemini API key obtained
- [ ] Backend deployed on Render
- [ ] Frontend deployed on Vercel
- [ ] Environment variables set
- [ ] Backend API responding
- [ ] Frontend loading without CORS errors
- [ ] Test agent endpoint with real query
- [ ] Monitor logs for errors
- [ ] Set up uptime monitoring
- [ ] Document production URLs

## Common Production Issues

### Issue 1: CORS Errors
**Error**: `Access to XMLHttpRequest blocked by CORS`

**Solution**:
1. Update backend CORS to allow your frontend domain
2. Verify environment variable points to correct backend
3. Clear browser cache

### Issue 2: Cold Start Delays
**Error**: First request takes 30+ seconds

**Solution**: See "Render Cold Start Issue" above

### Issue 3: API Key Errors
**Error**: `GEMINI_API_KEY not found`

**Solution**:
1. Verify environment variable is set on Render
2. Check variable name matches exactly: `GEMINI_API_KEY`
3. Redeploy after setting environment variable

### Issue 4: File Not Found Errors
**Error**: `FileNotFoundError: data/erp_chunks.json`

**Solution**:
1. Ensure data directory is in root, not in backend/
2. Update file paths if necessary
3. Redeploy

## Scaling & Optimization

### For High Traffic
1. **Upgrade Render Instance**: Use Standard+ tier
2. **Add Caching**: Implement Redis for session storage
3. **Optimize Embeddings**: Cache frequently used embeddings
4. **Use CDN**: Vercel already uses Vercel Edge Network

### For Better Performance
1. **Lazy Load Frontend**: Implement code splitting in Angular
2. **Optimize Backend**: Add response caching
3. **Database Connection**: Use connection pooling if adding database
4. **Rate Limiting**: Add rate limits to prevent abuse

## Cost Estimation

### Free Tier (Recommended for Testing)
- Render Web Service: Free (with cold starts)
- Vercel Frontend: Free
- Google Gemini API: Free tier (~$15/month after free credits)
- **Total**: ~$15/month

### Paid Tier (Recommended for Production)
- Render Web Service: ~$7/month (no cold starts)
- Vercel Pro: $20/month (optional, for priority support)
- Google Gemini API: Pay per use (~$0.001 per request)
- **Total**: ~$30-50/month depending on usage

## Rollback Plan

### If Deployment Fails

#### Render Rollback
1. Go to Render Dashboard
2. Click on your service
3. Go to "Logs" tab
4. Click "Deployments" 
5. Select previous successful deployment
6. Click "Deploy"

#### Vercel Rollback
1. Go to Vercel Dashboard
2. Click on your project
3. Go to "Deployments" tab
4. Select previous successful deployment
5. Click "Redeploy"

### If API Key Leaks
1. Go to https://aistudio.google.com/apikey
2. Delete the compromised key
3. Create a new key
4. Update environment variable on Render
5. Trigger redeploy

## Next Steps

1. Deploy backend to Render
2. Deploy frontend to Vercel
3. Configure environment variables
4. Test production URLs
5. Set up monitoring
6. Document for team

## Support & Troubleshooting

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Gemini API Docs: https://ai.google.dev
- Google Cloud Support: https://cloud.google.com/support
