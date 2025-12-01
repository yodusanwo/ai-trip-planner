# 🛠️ Development Guide - AI Trip Planner

Complete guide for local development and contributing to the AI Trip Planner.

## 🏗️ Project Structure

```
ai-trip-planner/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main API application
│   ├── requirements.txt       # Python dependencies
│   ├── railway.json          # Railway deployment config
│   └── Procfile              # Process configuration
│
├── frontend/                  # Next.js frontend
│   ├── app/                  # Next.js app directory
│   │   ├── page.tsx         # Main page
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Global styles
│   ├── components/           # React components
│   │   ├── TripForm.tsx     # Trip planning form
│   │   ├── ProgressTracker.tsx  # Real-time progress
│   │   ├── TripResult.tsx   # Results display
│   │   └── UsageStats.tsx   # Usage dashboard
│   ├── public/              # Static assets
│   ├── package.json         # Node dependencies
│   └── next.config.ts       # Next.js configuration
│
└── trip_planner/             # CrewAI agents (original)
    └── src/trip_planner/
        ├── crew.py          # Agent definitions
        ├── main.py          # CLI entry point
        └── config/
            ├── agents.yaml  # Agent configurations
            └── tasks.yaml   # Task definitions
```

## 🚀 Local Development Setup

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Git**
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **Serper API Key** ([Get one here](https://serper.dev))

### Step 1: Clone and Install

```bash
# Clone repository
git clone https://github.com/yodusanwo/ai-trip-planner.git
cd ai-trip-planner

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Step 2: Environment Configuration

**Backend `.env`:**
```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-key-here
SERPER_API_KEY=your-serper-key
MODEL=gpt-4o-mini
```

**Frontend `.env.local`:**
```bash
cd frontend
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 3: Run Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔧 Development Workflow

### Making Changes

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**

3. **Test locally:**
```bash
# Backend tests
cd backend
pytest  # If you add tests

# Frontend tests
cd frontend
npm run build  # Check for build errors
npm run lint   # Check for linting errors
```

4. **Commit and push:**
```bash
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
```

5. **Create Pull Request** on GitHub

### Code Style

**Backend (Python):**
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Keep functions small and focused

```python
def validate_input(text: str, field_name: str) -> str:
    """
    Validate and sanitize user input.
    
    Args:
        text: Input text to validate
        field_name: Name of the field for length limits
        
    Returns:
        Sanitized text string
    """
    # Implementation
```

**Frontend (TypeScript):**
- Use TypeScript strictly
- Follow React best practices
- Use functional components with hooks
- Keep components small and reusable

```typescript
interface TripFormProps {
  onSubmit: (data: TripData) => void;
}

export default function TripForm({ onSubmit }: TripFormProps) {
  // Implementation
}
```

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

**Example test:**
```python
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Frontend Testing

```bash
cd frontend

# Type checking
npm run build

# Linting
npm run lint

# Run tests (if you add them)
npm test
```

## 🎨 Customizing the Application

### Modify AI Agents

**Edit agent behavior:**
```yaml
# trip_planner/src/trip_planner/config/agents.yaml
trip_researcher:
  role: >
    Expert Travel Researcher
  goal: >
    Research and discover the best destinations
  backstory: >
    You're an experienced travel researcher...
```

**Edit tasks:**
```yaml
# trip_planner/src/trip_planner/config/tasks.yaml
research_task:
  description: >
    Research {destination} for {duration} trip...
  expected_output: >
    Brief report with attractions, restaurants...
```

**Adjust performance:**
```python
# trip_planner/src/trip_planner/crew.py
@agent
def trip_researcher(self) -> Agent:
    return Agent(
        config=self.agents_config['trip_researcher'],
        verbose=True,
        tools=[SerperDevTool()],
        max_iter=5,   # Reduce for faster execution
        max_rpm=30,   # Increase for more API calls
        allow_delegation=False,
    )
```

### Modify UI Components

**Change colors:**
```typescript
// frontend/app/page.tsx
<button className="bg-gradient-to-r from-blue-600 to-purple-600">
  // Change to your brand colors
</button>
```

**Update branding:**
```typescript
// frontend/app/layout.tsx
export const metadata: Metadata = {
  title: "Your App Name",
  description: "Your description",
  // ... more metadata
};
```

### Add New Features

**Example: Add trip sharing**

1. **Backend endpoint:**
```python
# backend/main.py
@app.post("/api/trips/{trip_id}/share")
async def share_trip(trip_id: str):
    # Generate shareable link
    share_token = generate_share_token(trip_id)
    return {"share_url": f"/shared/{share_token}"}
```

2. **Frontend component:**
```typescript
// frontend/components/ShareButton.tsx
export default function ShareButton({ tripId }: { tripId: string }) {
  const handleShare = async () => {
    const response = await fetch(`/api/trips/${tripId}/share`, {
      method: 'POST',
    });
    const data = await response.json();
    navigator.clipboard.writeText(data.share_url);
    alert('Link copied!');
  };
  
  return <button onClick={handleShare}>Share Trip</button>;
}
```

## 🔍 Debugging

### Backend Debugging

**Enable verbose logging:**
```python
# backend/main.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/api/trips/plan")
async def plan_trip(request: TripRequest):
    logger.debug(f"Received request: {request}")
    # ... rest of code
```

**Use FastAPI's interactive docs:**
- Visit http://localhost:8000/docs
- Test endpoints directly
- View request/response schemas

### Frontend Debugging

**Use React DevTools:**
- Install React DevTools browser extension
- Inspect component state and props
- Profile performance

**Check API calls:**
```typescript
// Add logging to API calls
const response = await fetch(url);
console.log('API Response:', await response.json());
```

**Use Next.js debug mode:**
```bash
NODE_OPTIONS='--inspect' npm run dev
# Open chrome://inspect in Chrome
```

## 📦 Building for Production

### Backend

```bash
cd backend

# Test production build
uvicorn main:app --host 0.0.0.0 --port 8000

# Or with gunicorn (production server)
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend

```bash
cd frontend

# Build for production
npm run build

# Test production build locally
npm run start

# Check bundle size
npm run build -- --analyze
```

## 🐛 Common Issues

### Backend Issues

**Issue: "Module not found: trip_planner"**
```bash
# Solution: Add to Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/../trip_planner/src"
```

**Issue: "Rate limit exceeded"**
```python
# Solution: Adjust rate limits in main.py
MAX_REQUESTS_PER_HOUR = 20  # Increase limit
```

### Frontend Issues

**Issue: "Failed to fetch"**
```typescript
// Solution: Check NEXT_PUBLIC_API_URL
console.log(process.env.NEXT_PUBLIC_API_URL);
// Ensure backend is running
```

**Issue: "Hydration error"**
```typescript
// Solution: Use useEffect for client-only code
useEffect(() => {
  // Client-only code here
}, []);
```

## 📚 Useful Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [CrewAI Docs](https://docs.crewai.com/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [VS Code](https://code.visualstudio.com/) - Recommended IDE

### Extensions (VS Code)
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

**Contribution areas:**
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- ⚡ Performance optimizations

## 📞 Getting Help

- **GitHub Issues:** Report bugs or request features
- **Discussions:** Ask questions or share ideas
- **Email:** Contact Zora Digital

---

**Happy coding! 🚀**

