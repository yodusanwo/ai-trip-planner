# Fix WeasyPrint Error on Railway

## The Problem
Railway is showing: `OSError: cannot load library 'libgobject-2.0-0'`

This happens because WeasyPrint requires system libraries that aren't installed by default on Railway's Linux environment.

## Solutions

### Option 1: Use Dockerfile (Recommended)

I've created a `backend/Dockerfile` that installs all required system libraries.

**To use it:**
1. Railway should auto-detect the Dockerfile
2. If not, go to Railway → Settings → Build
3. Change builder from "Nixpacks" to "Dockerfile"
4. Redeploy

### Option 2: Configure Railway to Use Docker

1. In Railway dashboard → Your service → Settings
2. Go to "Build" section
3. Look for "Builder" or "Buildpack" setting
4. Select "Dockerfile" 
5. Save and redeploy

### Option 3: Make PDF Optional (Current State)

The code already makes WeasyPrint optional - the app will start even if WeasyPrint fails.

**Current behavior:**
- ✅ App starts successfully
- ⚠️ PDF download will show an error message
- ✅ All other features work normally

**To test:**
- The app should start without crashing
- Try creating a trip - it should work
- PDF download will show: "PDF generation is not available..."

## What I've Done

1. ✅ Made WeasyPrint import optional (app won't crash)
2. ✅ Created `backend/Dockerfile` with system dependencies
3. ✅ Updated `backend/nixpacks.toml` (backup option)

## Next Steps

1. **If using Dockerfile:**
   - Railway should auto-detect it
   - If not, manually select Dockerfile in Settings → Build
   - Redeploy

2. **If Dockerfile doesn't work:**
   - The app will still run (WeasyPrint is optional)
   - PDF feature will be disabled
   - All other features work normally

3. **Check logs:**
   - Look for: "⚠️ WeasyPrint not available" (means app runs without PDF)
   - Or: "Application startup complete" (means everything works)

## Verify It's Working

After redeploy, check Railway logs for:
- ✅ "Application startup complete" 
- ✅ "Uvicorn running on..."
- ❌ No "cannot load library" errors

If you see "WeasyPrint not available" warning, that's OK - the app still works, just PDF is disabled.

