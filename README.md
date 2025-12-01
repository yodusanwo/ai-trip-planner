# 🌍 AI Trip Planner

> **Professional AI-powered trip planning application built with Next.js and FastAPI**

Plan your perfect trip with specialized AI agents that research, review, and create personalized travel itineraries. Built with CrewAI, Next.js, and FastAPI for production deployment.

![AI Trip Planner](trip_planner/assets/AI_trip-planner_preview.png)

## ✨ Features

- 🤖 **AI Agent Team**: Three specialized AI agents work together (Researcher, Reviewer, Planner)
- ⚡ **Real-time Progress**: Server-Sent Events for live updates during trip planning
- 🎨 **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- 🔒 **Security Built-in**: Rate limiting, input validation, and cost caps
- 📊 **Usage Dashboard**: Track your API usage and costs
- 📱 **Mobile Responsive**: Works perfectly on all devices
- 🚀 **Production Ready**: Deploy to Vercel (frontend) and Railway (backend)

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Next.js       │         │   FastAPI       │         │   CrewAI        │
│   Frontend      │ ──────> │   Backend       │ ──────> │   Agents        │
│   (Vercel)      │   API   │   (Railway)     │  Runs   │   (OpenAI)      │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

### Tech Stack

**Frontend:**
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- Server-Sent Events (SSE)

**Backend:**
- FastAPI
- CrewAI
- OpenAI GPT-4o-mini
- SerperDev (Search API)

**Deployment:**
- Vercel (Frontend)
- Railway/Fly.io (Backend)
- Neon (PostgreSQL - Optional)

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- OpenAI API key
- Serper API key

### 1. Clone the Repository

```bash
git clone https://github.com/yodusanwo/ai-trip-planner.git
cd ai-trip-planner
```

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your-key-here
# SERPER_API_KEY=your-key-here
# MODEL=gpt-4o-mini

# Run the backend
uvicorn main:app --reload
```

Backend will run at `http://localhost:8000`

### 3. Set Up Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the frontend
npm run dev
```

Frontend will run at `http://localhost:3000`

### 4. Test Locally

1. Open `http://localhost:3000` in your browser
2. Fill in the trip planning form
3. Watch the AI agents work in real-time
4. Download your personalized itinerary

## 📦 Deployment

### Deploy Frontend to Vercel

1. **Push to GitHub:**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Select the `frontend` folder as the root directory
   - Add environment variable:
     - `NEXT_PUBLIC_API_URL`: Your backend URL (from Railway)
   - Click "Deploy"

3. **Custom Domain (Optional):**
   - Go to Project Settings → Domains
   - Add your custom domain
   - Update DNS records as instructed

### Deploy Backend to Railway

1. **Create Railway Account:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy Backend:**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Choose the `backend` folder
   - Add environment variables:
     - `OPENAI_API_KEY`
     - `SERPER_API_KEY`
     - `MODEL=gpt-4o-mini`
   - Railway will auto-detect FastAPI and deploy

3. **Get Backend URL:**
   - Copy the generated Railway URL (e.g., `https://your-app.railway.app`)
   - Update frontend's `NEXT_PUBLIC_API_URL` in Vercel

### Alternative: Deploy Backend to Fly.io

```bash
cd backend

# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app
fly launch

# Set secrets
fly secrets set OPENAI_API_KEY=your-key
fly secrets set SERPER_API_KEY=your-key
fly secrets set MODEL=gpt-4o-mini

# Deploy
fly deploy
```

## 🔧 Configuration

### Backend Configuration

Edit `backend/main.py` to customize:

```python
# Rate limiting
MAX_REQUESTS_PER_HOUR = 10

# Cost management
WEEKLY_COST_CAP = 10.0  # $10 per week
COST_PER_REQUEST = 0.15  # Estimated cost

# CORS origins (add your domain)
allow_origins=[
    "http://localhost:3000",
    "https://your-domain.com",
]
```

### Agent Configuration

Edit `trip_planner/src/trip_planner/config/agents.yaml` and `tasks.yaml` to customize agent behavior.

## 📊 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/trips/plan` - Start trip planning
- `GET /api/trips/{trip_id}/progress` - Get progress
- `GET /api/trips/{trip_id}/stream` - Real-time SSE updates
- `GET /api/trips/{trip_id}/result` - Get final result
- `GET /api/usage/{client_id}` - Get usage stats

## 🔒 Security Features

- ✅ Rate limiting (10 requests/hour per client)
- ✅ Weekly cost cap ($10/week)
- ✅ Input validation and sanitization
- ✅ XSS protection
- ✅ SQL injection prevention
- ✅ CORS configuration

## 🎨 Customization

### Branding

1. Replace images in `frontend/public/`:
   - `og-image.png` (1200x630) - Social media preview
   - `twitter-image.png` (1200x630) - Twitter card

2. Update metadata in `frontend/app/layout.tsx`

3. Update footer text in `frontend/app/page.tsx`

### Styling

Edit `frontend/app/globals.css` and component Tailwind classes to match your brand colors.

## 🐛 Troubleshooting

### Backend Issues

**"Module not found" error:**
```bash
# Ensure you're in the backend directory and venv is activated
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**"CORS error" in frontend:**
- Check `allow_origins` in `backend/main.py`
- Ensure frontend URL is listed

### Frontend Issues

**"Failed to fetch" error:**
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check backend is running
- Check CORS configuration

**Build errors:**
```bash
# Clear cache and reinstall
rm -rf .next node_modules
npm install
npm run build
```

## 📝 Environment Variables

### Backend (.env)
```env
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...
MODEL=gpt-4o-mini
DATABASE_URL=postgresql://... (optional)
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Credits

- **Created by**: [Zora Digital](https://zoradigital.com)
- **Powered by**: CrewAI, OpenAI, Next.js, FastAPI
- **Search API**: SerperDev

## 📞 Support

For questions or support:
- GitHub Issues: [Create an issue](https://github.com/yodusanwo/ai-trip-planner/issues)
- Website: [zoradigital.com](https://zoradigital.com)

---

**Built with ❤️ by Zora Digital** | Showcasing AI Agent Capabilities

