# Quick Deployment Checklist

## ✅ Pre-Deployment

- [ ] All code committed and pushed to GitHub
- [ ] Backend dependencies in `backend/requirements.txt` are up to date
- [ ] Frontend dependencies in `frontend/package.json` are up to date
- [ ] Environment variables documented (.env.example if needed)
- [ ] API keys ready (OpenAI, Serper)

---

## 🚂 Railway (Backend) Deployment

- [ ] Created Railway account and connected GitHub
- [ ] Created new project from GitHub repo
- [ ] Set Root Directory to `backend`
- [ ] Added environment variables:
  - [ ] `OPENAI_API_KEY`
  - [ ] `SERPER_API_KEY`
  - [ ] `CORS_ORIGINS` (optional, for production)
- [ ] Deployment successful
- [ ] Backend URL copied (e.g., `https://your-app.railway.app`)
- [ ] Tested backend endpoint: `https://your-backend.railway.app/`

---

## ▲ Vercel (Frontend) Deployment

- [ ] Created Vercel account and connected GitHub
- [ ] Imported project from GitHub repo
- [ ] Set Root Directory to `frontend` ⚠️ **CRITICAL**
- [ ] Added environment variable:
  - [ ] `NEXT_PUBLIC_API_URL` = Your Railway backend URL
- [ ] Build successful
- [ ] Frontend URL copied (e.g., `https://your-app.vercel.app`)

---

## 🔗 Post-Deployment Configuration

- [ ] Updated backend CORS to include Vercel URL:
  - [ ] Option 1: Add to `CORS_ORIGINS` env var in Railway: `http://localhost:3000,http://localhost:3001,https://your-app.vercel.app`
  - [ ] Option 2: Edit `backend/main.py` CORS origins list
- [ ] Committed and pushed CORS changes
- [ ] Railway auto-redeployed with new CORS settings

---

## 🧪 Testing

- [ ] Visit Vercel URL
- [ ] Form submission works
- [ ] Progress tracker displays
- [ ] Trip results show correctly
- [ ] PDF download works
- [ ] Spell check works (if applicable)
- [ ] No CORS errors in browser console
- [ ] No 404/500 errors

---

## 📊 Monitoring Setup

- [ ] Railway logs accessible
- [ ] Vercel build logs accessible
- [ ] Error tracking set up (optional)
- [ ] Usage monitoring enabled

---

## 🔐 Security Checklist

- [ ] No API keys in code (all in environment variables)
- [ ] HTTPS enabled (automatic on Vercel/Railway)
- [ ] CORS properly configured
- [ ] Rate limiting working
- [ ] Input validation working

---

## 📝 Notes

**Backend URL**: `_________________________`

**Frontend URL**: `_________________________`

**Deployment Date**: `_________________________`

---

## 🆘 If Something Goes Wrong

1. Check Railway logs for backend errors
2. Check Vercel build logs for frontend errors
3. Check browser console for client-side errors
4. Verify environment variables are set correctly
5. Verify CORS includes your Vercel domain
6. Test backend endpoint directly (curl or Postman)
7. Check Network tab in browser DevTools

