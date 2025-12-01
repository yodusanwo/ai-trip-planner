# Deployment Guide - Next.js + FastAPI Architecture

This guide walks you through deploying the AI Trip Planner application to production using Vercel (frontend) and Railway (backend).

## Prerequisites

- GitHub account
- Vercel account (free tier available)
- Railway account (free tier available)
- OpenAI API key
- Serper API key

## Step 1: Deploy Backend to Railway

### 1.1 Create Railway Project

1. Go to [Railway](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will detect the Python project

### 1.2 Configure Backend

1. In Railway dashboard, click on your service
2. Go to "Settings" → "Root Directory"
3. Set root directory to: `backend`
4. Go to "Variables" and add:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERPER_API_KEY=your_serper_api_key
   ```

### 1.3 Deploy

1. Railway will automatically build and deploy
2. Wait for deployment to complete
3. Copy the generated URL (e.g., `https://your-app.railway.app`)
4. This is your backend API URL

## Step 2: Deploy Frontend to Vercel

### 2.1 Import Project

1. Go to [Vercel](https://vercel.com) and sign in
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)

### 2.2 Configure Environment Variables

Add the following environment variable:
- `NEXT_PUBLIC_API_URL`: Your Railway backend URL (e.g., `https://your-app.railway.app`)

### 2.3 Deploy

1. Click "Deploy"
2. Wait for build to complete
3. Vercel will provide you with a URL (e.g., `https://your-app.vercel.app`)

## Step 3: Update CORS Settings

After deploying, update the backend CORS settings to allow your Vercel domain:

1. Go to Railway dashboard
2. Open your backend service
3. Edit `backend/main.py`
4. Update the CORS origins:
   ```python
   allow_origins=[
       "http://localhost:3000",
       "http://localhost:3001",
       "https://your-app.vercel.app",  # Add your Vercel URL
   ],
   ```
5. Commit and push changes
6. Railway will automatically redeploy

## Step 4: Test Deployment

1. Visit your Vercel URL
2. Fill out the trip planning form
3. Verify that:
   - Form submission works
   - Progress tracking displays
   - Trip results are shown

## Troubleshooting

### Backend Issues

**Problem**: Backend fails to start
- Check Railway logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is correct

**Problem**: CORS errors
- Verify CORS origins include your Vercel URL
- Check that `NEXT_PUBLIC_API_URL` is set correctly

### Frontend Issues

**Problem**: Cannot connect to backend
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check that backend is running and accessible
- Verify CORS settings in backend

**Problem**: Build fails
- Check Vercel build logs
- Ensure all dependencies are in `package.json`
- Verify TypeScript compilation errors

## Environment Variables Reference

### Backend (Railway)
```
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## Monitoring

### Railway
- View logs in Railway dashboard
- Monitor resource usage
- Set up alerts for errors

### Vercel
- View build logs
- Monitor analytics
- Check function logs

## Cost Estimation

### Railway (Backend)
- Free tier: $5 credit/month
- Estimated cost: ~$0.10-0.50/month for low traffic

### Vercel (Frontend)
- Free tier: Unlimited deployments
- Hobby plan: Free for personal projects

### API Costs
- OpenAI: ~$0.01-0.03 per trip (with gpt-4o-mini)
- Serper: Free tier available, then pay-as-you-go

## Scaling Considerations

### Backend
- Railway auto-scales based on traffic
- Consider upgrading for high traffic
- Monitor API rate limits

### Frontend
- Vercel Edge Network provides global CDN
- Automatic scaling
- Consider upgrading for custom domains

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Enable HTTPS** - Both Railway and Vercel provide SSL
3. **Monitor usage** - Set up alerts for cost caps
4. **Review logs** - Regularly check for suspicious activity
5. **Update dependencies** - Keep packages up to date

## Rollback Procedure

### Railway
1. Go to deployments
2. Select previous deployment
3. Click "Redeploy"

### Vercel
1. Go to deployments
2. Find previous deployment
3. Click "..." → "Promote to Production"

## Support

For issues or questions:
- Check application logs in Railway/Vercel
- Review error messages in browser console
- Check API responses in Network tab
- Review this documentation

