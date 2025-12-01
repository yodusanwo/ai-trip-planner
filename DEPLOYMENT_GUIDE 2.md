# 🚀 Deployment Guide - AI Trip Planner

Complete step-by-step guide to deploy your AI Trip Planner to production.

## 📋 Overview

We'll deploy:
- **Frontend** → Vercel (Free tier, instant deployment)
- **Backend** → Railway (Free tier, $5/month for production)
- **Database** → Neon (Optional, for trip library feature)

## ⚡ Quick Deploy (5 minutes)

### Step 1: Prepare Repository

```bash
# Ensure everything is committed
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### Step 2: Deploy Backend to Railway

1. **Go to Railway:**
   - Visit [railway.app](https://railway.app)
   - Sign in with GitHub

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `ai-trip-planner` repository
   - Select `backend` as root directory

3. **Configure Environment Variables:**
   Click "Variables" and add:
   ```
   OPENAI_API_KEY=sk-your-key-here
   SERPER_API_KEY=your-serper-key
   MODEL=gpt-4o-mini
   ```

4. **Deploy:**
   - Railway auto-detects FastAPI
   - Wait for deployment (2-3 minutes)
   - Copy your Railway URL: `https://your-app.railway.app`

### Step 3: Deploy Frontend to Vercel

1. **Go to Vercel:**
   - Visit [vercel.com](https://vercel.com)
   - Sign in with GitHub

2. **Import Project:**
   - Click "Add New" → "Project"
   - Import `ai-trip-planner` repository
   - Select `frontend` as root directory

3. **Configure:**
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `.next` (auto-detected)

4. **Add Environment Variable:**
   ```
   NEXT_PUBLIC_API_URL=https://your-app.railway.app
   ```
   (Use your Railway URL from Step 2)

5. **Deploy:**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your app is live! 🎉

### Step 4: Update CORS

1. **Edit `backend/main.py`:**
   ```python
   allow_origins=[
       "http://localhost:3000",
       "https://your-app.vercel.app",  # Add your Vercel URL
       "https://your-custom-domain.com",  # If using custom domain
   ]
   ```

2. **Commit and push:**
   ```bash
   git add backend/main.py
   git commit -m "Update CORS for production"
   git push
   ```
   Railway will auto-deploy the update.

### Step 5: Test Production

1. Visit your Vercel URL
2. Try planning a trip
3. Verify everything works!

---

## 🎯 Custom Domain Setup

### Add Custom Domain to Vercel

1. **In Vercel Dashboard:**
   - Go to your project
   - Click "Settings" → "Domains"
   - Add your domain (e.g., `trip-planner.yourdomain.com`)

2. **Update DNS:**
   Add these records to your domain provider:
   ```
   Type: CNAME
   Name: trip-planner (or @)
   Value: cname.vercel-dns.com
   ```

3. **Wait for DNS propagation** (5-30 minutes)

4. **Update CORS** in backend to include your custom domain

### Add Custom Domain to Railway (Backend)

1. **In Railway Dashboard:**
   - Go to your backend project
   - Click "Settings" → "Domains"
   - Click "Generate Domain" or add custom domain

2. **Update Frontend:**
   In Vercel, update `NEXT_PUBLIC_API_URL` to your custom backend domain

---

## 🔧 Advanced Configuration

### Enable Database (Optional)

If you want the Trip Library feature:

1. **Create Neon Database:**
   - Visit [neon.tech](https://neon.tech)
   - Create free account
   - Create new project
   - Copy connection string

2. **Add to Backend:**
   In Railway, add environment variable:
   ```
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   ```

3. **Update Backend Code:**
   Uncomment database integration code in `backend/main.py`

### Optimize Performance

**Backend (Railway):**
```python
# In backend/main.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=2,  # Multiple workers for better performance
    )
```

**Frontend (Vercel):**
```typescript
// In next.config.ts
const nextConfig = {
  output: 'standalone',
  compress: true,
  poweredByHeader: false,
};
```

### Set Up Monitoring

**Railway:**
- Built-in metrics available in dashboard
- View logs in real-time
- Set up alerts for errors

**Vercel:**
- Analytics available in dashboard
- Speed Insights (free)
- Web Vitals monitoring

---

## 💰 Cost Estimation

### Free Tier Limits

**Vercel (Frontend):**
- ✅ 100GB bandwidth/month
- ✅ Unlimited deployments
- ✅ Custom domains
- ✅ SSL certificates
- **Cost:** FREE

**Railway (Backend):**
- ✅ $5 free credit/month
- ✅ ~500 hours runtime
- ✅ 1GB RAM, 1 vCPU
- **Cost:** FREE (with credit) or $5/month

**OpenAI API:**
- GPT-4o-mini: ~$0.15 per trip
- 100 trips/month = $15
- **Cost:** Pay as you go

**Total Monthly Cost:**
- Light usage (< 100 trips): **$5-20/month**
- Medium usage (< 500 trips): **$20-80/month**

### Cost Optimization Tips

1. **Use GPT-4o-mini** (not GPT-4) - 10x cheaper
2. **Enable cost caps** in backend
3. **Set rate limits** to prevent abuse
4. **Monitor usage** via dashboard
5. **Cache results** (optional database feature)

---

## 🐛 Troubleshooting

### Deployment Fails

**Railway Backend:**
```bash
# Check logs in Railway dashboard
# Common issues:
# 1. Missing environment variables
# 2. Wrong Python version
# 3. Dependencies not installed

# Fix: Ensure requirements.txt is complete
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

**Vercel Frontend:**
```bash
# Check build logs in Vercel dashboard
# Common issues:
# 1. Missing NEXT_PUBLIC_API_URL
# 2. Build errors
# 3. Node version mismatch

# Fix: Clear cache and redeploy
# In Vercel: Settings → General → Clear Cache
```

### CORS Errors

**Symptom:** Frontend can't connect to backend

**Fix:**
1. Check `allow_origins` in `backend/main.py`
2. Ensure your Vercel URL is listed
3. Redeploy backend after changes

### Slow Performance

**Backend taking too long:**
1. Check Railway logs for errors
2. Verify OpenAI API is responding
3. Consider upgrading Railway plan for more resources

**Frontend slow to load:**
1. Enable Next.js optimizations
2. Check Vercel analytics
3. Optimize images and assets

### API Rate Limits

**OpenAI rate limit exceeded:**
1. Check your OpenAI dashboard
2. Upgrade OpenAI tier if needed
3. Implement caching (database feature)

---

## 📊 Monitoring & Maintenance

### Health Checks

**Backend:**
```bash
# Check if backend is running
curl https://your-app.railway.app/

# Should return:
# {"status":"healthy","service":"AI Trip Planner API","version":"1.0.0"}
```

**Frontend:**
```bash
# Check if frontend is accessible
curl -I https://your-app.vercel.app/

# Should return: 200 OK
```

### Log Monitoring

**Railway:**
- View real-time logs in dashboard
- Set up log alerts
- Export logs for analysis

**Vercel:**
- View deployment logs
- Runtime logs (Pro plan)
- Error tracking

### Regular Updates

```bash
# Update dependencies monthly
cd backend
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

cd ../frontend
npm update
npm audit fix

# Test locally, then deploy
git add .
git commit -m "Update dependencies"
git push
```

---

## 🔐 Security Best Practices

1. **Never commit API keys** to Git
2. **Use environment variables** for all secrets
3. **Enable rate limiting** in production
4. **Monitor usage** regularly
5. **Keep dependencies updated**
6. **Use HTTPS only** (automatic on Vercel/Railway)
7. **Implement cost caps** to prevent surprise bills

---

## 🎉 Success Checklist

- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS updated with production URLs
- [ ] Custom domain added (optional)
- [ ] Test trip planning works end-to-end
- [ ] Usage monitoring set up
- [ ] Cost caps configured
- [ ] Documentation updated with URLs

---

## 📞 Need Help?

- **Railway Docs:** [docs.railway.app](https://docs.railway.app)
- **Vercel Docs:** [vercel.com/docs](https://vercel.com/docs)
- **GitHub Issues:** [Create an issue](https://github.com/yodusanwo/ai-trip-planner/issues)

---

**🚀 Your AI Trip Planner is now live!**

Share it with the world: `https://your-app.vercel.app`

