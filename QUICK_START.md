# ⚡ Quick Start - AI Trip Planner

Get your AI Trip Planner running in 5 minutes!

## 🎯 What You'll Build

A production-ready AI trip planning application with:
- ✨ Beautiful Next.js frontend
- 🚀 FastAPI backend with CrewAI agents
- 📊 Real-time progress tracking
- 🔒 Built-in security features
- 🌐 Ready to deploy to Vercel + Railway

## 📋 Prerequisites

Before starting, get:
1. **OpenAI API Key** → [Get it here](https://platform.openai.com/api-keys)
2. **Serper API Key** → [Get it here](https://serper.dev) (Free tier available)
3. **Node.js 18+** → [Download](https://nodejs.org/)
4. **Python 3.11+** → [Download](https://python.org/)

## 🚀 Local Setup (5 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/yodusanwo/ai-trip-planner.git
cd ai-trip-planner
```

### Step 2: Backend Setup (2 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your-key-here
SERPER_API_KEY=your-key-here
MODEL=gpt-4o-mini" > .env

# Edit .env and add your actual API keys
nano .env  # or use any text editor
```

### Step 3: Frontend Setup (2 minutes)

Open a NEW terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Step 4: Run Both Servers (1 minute)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 5: Test It! 🎉

1. Open http://localhost:3000
2. Fill in the form:
   - Destination: "Paris, France"
   - Duration: "5 days"
   - Budget: "Moderate"
   - Travel Style: Select a few options
3. Click "Plan My Trip"
4. Watch the AI agents work!

---

## 🌐 Deploy to Production (10 minutes)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 2: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Choose `backend` folder
6. Add environment variables:
   - `OPENAI_API_KEY`
   - `SERPER_API_KEY`
   - `MODEL=gpt-4o-mini`
7. Wait 2-3 minutes for deployment
8. **Copy your Railway URL** (e.g., `https://your-app.railway.app`)

### Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "Add New" → "Project"
4. Import your repository
5. Set Root Directory: `frontend`
6. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = Your Railway URL from Step 2
7. Click "Deploy"
8. Wait 2-3 minutes

### Step 4: Update CORS

Edit `backend/main.py` and add your Vercel URL:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add this
]
```

Commit and push:
```bash
git add backend/main.py
git commit -m "Update CORS"
git push
```

Railway will auto-deploy the update.

### Step 5: Done! 🎉

Your app is live at: `https://your-app.vercel.app`

---

## 🎨 Customize Your App

### Change Branding

1. **Update title and description:**
   Edit `frontend/app/layout.tsx`

2. **Change colors:**
   Edit `frontend/app/page.tsx` and component files

3. **Add your logo:**
   Replace images in `frontend/public/`

### Adjust AI Behavior

1. **Make agents faster/slower:**
   Edit `trip_planner/src/trip_planner/crew.py`
   ```python
   max_iter=5,   # Lower = faster, higher = more thorough
   max_rpm=30,   # Higher = more API calls = faster
   ```

2. **Change agent personalities:**
   Edit `trip_planner/src/trip_planner/config/agents.yaml`

3. **Modify tasks:**
   Edit `trip_planner/src/trip_planner/config/tasks.yaml`

### Update Rate Limits

Edit `backend/main.py`:
```python
MAX_REQUESTS_PER_HOUR = 10  # Change this
WEEKLY_COST_CAP = 10.0      # Change this
```

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "Module not found: trip_planner"**
```bash
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/../trip_planner/src"
```

**Error: "Invalid API key"**
- Check your `.env` file has correct keys
- Make sure there are no spaces or quotes around keys

### Frontend won't connect

**Error: "Failed to fetch"**
- Check backend is running on port 8000
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS settings in `backend/main.py`

### Deployment issues

**Railway: "Build failed"**
- Check `requirements.txt` is complete
- Verify Python version (3.11+)
- Check environment variables are set

**Vercel: "Build failed"**
- Verify `frontend` is set as root directory
- Check `NEXT_PUBLIC_API_URL` is set
- Clear cache and redeploy

---

## 💰 Cost Estimate

**Development (Free):**
- OpenAI: ~$0.15 per trip
- Serper: Free tier (2,500 searches/month)
- Total: ~$0.15 per trip

**Production:**
- Vercel: FREE (100GB bandwidth)
- Railway: $5/month (or free with credit)
- OpenAI: ~$0.15 per trip
- **Total: $5-20/month** (depending on usage)

---

## 📚 Next Steps

1. ✅ **Read the full docs:** [README.md](README.md)
2. 🚀 **Deploy guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
3. 🛠️ **Development guide:** [DEVELOPMENT.md](DEVELOPMENT.md)
4. 🎨 **Customize your app**
5. 🌐 **Add custom domain**
6. 📊 **Monitor usage**

---

## 🆘 Need Help?

- **Documentation:** See README.md
- **Issues:** [GitHub Issues](https://github.com/yodusanwo/ai-trip-planner/issues)
- **Email:** Contact Zora Digital

---

## 🎉 Success!

You now have a production-ready AI trip planner!

**Share your deployment:**
- Tweet about it
- Add to your portfolio
- Show it to friends

**Built with ❤️ by Zora Digital**

