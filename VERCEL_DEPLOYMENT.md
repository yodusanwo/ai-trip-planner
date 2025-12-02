# Vercel Deployment Guide

## Step 1: Prepare Frontend

✅ Frontend files have been restored from commit `e9f8e4a`

## Step 2: Deploy to Vercel

1. **Go to Vercel:** https://vercel.com
2. **Sign in** with your GitHub account
3. **Click "Add New..." → "Project"**
4. **Import your GitHub repository:**
   - Select `yodusanwo/ai-trip-planner`
   - Click "Import"

5. **Configure Project Settings:**
   - **Root Directory:** `frontend` (click "Edit" and set to `frontend`)
   - **Framework Preset:** Next.js (should auto-detect)
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)
   - **Install Command:** `npm install` (default)

6. **Add Environment Variable:**
   - Click "Environment Variables"
   - Add:
     - **Name:** `NEXT_PUBLIC_API_URL`
     - **Value:** `https://ai-trip-planner-production-45dc.up.railway.app`
     - **Environment:** Production, Preview, Development (select all)
   - Click "Save"

7. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete (usually 2-3 minutes)

## Step 3: Update CORS in Railway

After Vercel deployment completes:

1. **Get your Vercel URL:**
   - It will be something like: `https://ai-trip-planner-xyz.vercel.app`
   - Copy this URL

2. **Update Railway CORS:**
   - Go to Railway → Your service → Variables
   - Find or add `CORS_ORIGINS`
   - Set value to:
     ```
     http://localhost:3000,http://localhost:3001,https://your-vercel-url.vercel.app
     ```
   - Replace `your-vercel-url.vercel.app` with your actual Vercel URL
   - Railway will auto-redeploy

## Step 4: Test Full Stack

1. Visit your Vercel URL
2. Fill out the trip form
3. Submit and watch progress
4. Verify trip results display
5. Test PDF download

## Troubleshooting

### Build Fails
- Check Vercel build logs
- Ensure `NEXT_PUBLIC_API_URL` is set correctly
- Verify all dependencies are in `package.json`

### CORS Errors
- Make sure Railway `CORS_ORIGINS` includes your Vercel URL
- Wait for Railway to redeploy after updating CORS

### API Not Connecting
- Verify `NEXT_PUBLIC_API_URL` matches your Railway URL exactly
- Check Railway logs to ensure backend is running
- Test backend directly: `curl https://ai-trip-planner-production-45dc.up.railway.app/`

## Next Steps

1. ✅ Deploy frontend to Vercel
2. ⏭️ Update CORS with Vercel URL
3. ⏭️ Test full application
4. ⏭️ Celebrate! 🎉

