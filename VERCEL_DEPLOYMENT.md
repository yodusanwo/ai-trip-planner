# Vercel Deployment Guide

This guide will walk you through deploying your AI Trip Planner to Vercel (frontend) and Railway (backend).

## Quick Overview

- **Frontend (Next.js)**: Deploy to Vercel
- **Backend (FastAPI)**: Deploy to Railway (or another Python hosting service)
- **Why separate?**: Vercel is optimized for frontend/Next.js, while Railway is better for Python backends

---

## Step 1: Deploy Backend to Railway

### 1.1 Create Railway Account & Project

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `trip_planner` repository
5. Railway will auto-detect it's a Python project

### 1.2 Configure Backend Settings

1. In Railway dashboard, click on your service
2. Go to **Settings** → **Root Directory**
3. Set to: `backend`
4. Go to **Variables** tab and add:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   ```

### 1.3 Deploy & Get Backend URL

1. Railway will automatically start building
2. Wait for deployment to complete (check **Deployments** tab)
3. Once deployed, go to **Settings** → **Networking**
4. Click **"Generate Domain"** or use the provided domain
5. **Copy the URL** (e.g., `https://your-app.railway.app`) - this is your backend API URL

### 1.4 Update CORS Settings

1. Go back to your local code
2. Edit `backend/main.py` - find the CORS section (around line 100)
3. Add your Vercel domain to the allowed origins:
   ```python
   allow_origins=[
       "http://localhost:3000",
       "http://localhost:3001",
       "https://your-app.vercel.app",  # Add this after Vercel deployment
   ],
   ```
4. Commit and push - Railway will auto-redeploy

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Import Project to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New"** → **"Project"**
3. Import your `trip_planner` repository
4. Vercel will auto-detect Next.js

### 2.2 Configure Project Settings

In the project configuration:

- **Framework Preset**: Next.js (auto-detected)
- **Root Directory**: `frontend` ⚠️ **IMPORTANT**: Change this from `/` to `frontend`
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `.next` (auto-detected)
- **Install Command**: `npm install` (auto-detected)

### 2.3 Set Environment Variables

Before deploying, add environment variable:

1. Scroll down to **"Environment Variables"** section
2. Add:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your Railway backend URL (e.g., `https://your-app.railway.app`)
   - **Environment**: Production, Preview, Development (select all)

### 2.4 Deploy

1. Click **"Deploy"**
2. Wait for build to complete (usually 1-2 minutes)
3. Vercel will provide a URL (e.g., `https://your-app.vercel.app`)

### 2.5 Update Backend CORS (Again)

1. Go back to Railway dashboard
2. Edit `backend/main.py` locally
3. Update CORS with your actual Vercel URL:
   ```python
   allow_origins=[
       "http://localhost:3000",
       "http://localhost:3001",
       "https://your-actual-app.vercel.app",  # Replace with your real Vercel URL
   ],
   ```
4. Commit and push - Railway will redeploy

---

## Step 3: Test Your Deployment

1. Visit your Vercel URL
2. Fill out the trip planning form
3. Verify:
   - ✅ Form submits successfully
   - ✅ Progress tracker shows updates
   - ✅ Trip results display correctly
   - ✅ PDF download works

---

## Troubleshooting

### Frontend Issues

**Problem**: "Cannot connect to backend" or CORS errors
- ✅ Check `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- ✅ Verify backend is running (check Railway logs)
- ✅ Ensure CORS includes your Vercel domain

**Problem**: Build fails on Vercel
- ✅ Check build logs in Vercel dashboard
- ✅ Ensure `frontend` is set as root directory
- ✅ Verify all dependencies are in `package.json`

**Problem**: Environment variable not working
- ✅ Make sure variable name starts with `NEXT_PUBLIC_`
- ✅ Redeploy after adding environment variables
- ✅ Check variable is set for correct environment (Production/Preview)

### Backend Issues

**Problem**: Backend won't start
- ✅ Check Railway logs for errors
- ✅ Verify all environment variables are set (OPENAI_API_KEY, SERPER_API_KEY)
- ✅ Ensure `backend/requirements.txt` includes all dependencies

**Problem**: 500 errors or API failures
- ✅ Check Railway logs for detailed error messages
- ✅ Verify API keys are valid
- ✅ Check if backend has enough resources (Railway free tier limits)

---

## Environment Variables Summary

### Vercel (Frontend)
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Railway (Backend)
```
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...
```

---

## Cost Estimate

### Vercel
- **Free tier**: Unlimited deployments, 100GB bandwidth/month
- **Perfect for**: Personal projects, small to medium traffic

### Railway
- **Free tier**: $5 credit/month
- **Estimated cost**: ~$0.10-0.50/month for low traffic
- **Upgrade needed**: If you exceed free tier limits

### API Costs
- **OpenAI**: ~$0.01-0.03 per trip (with gpt-4o-mini)
- **Serper**: Free tier available, then pay-as-you-go

---

## Continuous Deployment

Both Vercel and Railway support automatic deployments:

- **Vercel**: Automatically deploys on every push to `main` branch
- **Railway**: Automatically deploys on every push to `main` branch

To deploy updates:
1. Make changes locally
2. Commit and push to GitHub
3. Both services will automatically redeploy

---

## Custom Domain (Optional)

### Vercel
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### Railway
1. Go to Settings → Networking
2. Add custom domain
3. Configure DNS records

---

## Monitoring

### Vercel
- View build logs in dashboard
- Monitor analytics and performance
- Check function logs for errors

### Railway
- View real-time logs in dashboard
- Monitor resource usage
- Set up alerts for errors

---

## Need Help?

- Check application logs in both Vercel and Railway dashboards
- Review browser console for frontend errors
- Check Network tab for API call issues
- Review error messages in Railway logs

