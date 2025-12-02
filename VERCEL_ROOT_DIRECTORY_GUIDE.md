# How to Set Root Directory in Vercel

## Option 1: During Project Import (Easiest)

When you first import your project to Vercel:

1. Go to [vercel.com](https://vercel.com) → "Add New" → "Project"
2. Import your GitHub repository
3. **Before clicking "Deploy"**, look for the **"Configure Project"** section
4. Find **"Root Directory"** field
5. Click "Edit" next to Root Directory
6. Enter: `frontend`
7. Click "Deploy"

## Option 2: After Project Creation (Settings)

If your project is already created:

1. Go to your project dashboard
2. Click **"Settings"** tab (top navigation)
3. Click **"General"** in the left sidebar (you're already here!)
4. Scroll down to find **"Build & Development Settings"** section
5. Look for **"Root Directory"** field
6. Click **"Override"** or **"Edit"**
7. Enter: `frontend`
8. Click **"Save"**

## Option 3: Using vercel.json (Recommended)

The easiest way is to use the `vercel.json` file (already in your repo):

Your `frontend/vercel.json` file already exists and should work, but Vercel might not be reading it if it's in the `frontend` folder.

**Solution:** Move or copy `vercel.json` to the **root** of your repository:

1. Copy `frontend/vercel.json` to the root directory
2. Or create a new `vercel.json` in the root with:

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "framework": "nextjs"
}
```

## Option 4: Check Current Settings

To see what Vercel is currently using:

1. Go to Settings → General
2. Scroll to **"Build & Development Settings"**
3. Check what's listed under:
   - **Root Directory** (might show `/` or blank)
   - **Build Command**
   - **Output Directory**

## Quick Fix Steps

1. **In Vercel Dashboard:**
   - Settings → General
   - Scroll to "Build & Development Settings"
   - Find "Root Directory"
   - Change from `/` (or blank) to `frontend`
   - Save

2. **If you don't see Root Directory option:**
   - Go to your project's main page
   - Click the **"..."** (three dots) menu
   - Select **"View Configuration"** or **"Settings"**
   - Look for build settings there

3. **Alternative:** Delete and re-import the project, making sure to set root directory during import

## Verify It's Working

After setting root directory:

1. Go to **"Deployments"** tab
2. Trigger a new deployment (or push a commit)
3. Check the build logs
4. You should see it running `npm install` and `npm run build` from the `frontend` directory

## Troubleshooting

**Problem:** Can't find Root Directory setting
- **Solution:** It might be in a different location. Try:
  - Settings → General → Scroll all the way down
  - Or check the project's main page for configuration options

**Problem:** Setting exists but doesn't work
- **Solution:** Make sure you've saved and triggered a new deployment

**Problem:** Build still fails
- **Solution:** Check that `frontend/package.json` exists and has correct build scripts

