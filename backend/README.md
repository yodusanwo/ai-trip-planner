# 🔧 Backend - AI Trip Planner API

FastAPI backend for the AI Trip Planner application.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your API keys to .env

# Run server
uvicorn main:app --reload
```

Server runs at: http://localhost:8000

## 📚 API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔑 Environment Variables

Required:
- `OPENAI_API_KEY` - OpenAI API key
- `SERPER_API_KEY` - Serper search API key
- `MODEL` - OpenAI model (default: gpt-4o-mini)

Optional:
- `DATABASE_URL` - PostgreSQL connection string (for trip library)

## 📦 Dependencies

- **FastAPI** - Modern web framework
- **CrewAI** - AI agent orchestration
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

## 🔒 Security Features

- Rate limiting (10 requests/hour)
- Input validation and sanitization
- Cost caps ($10/week)
- CORS protection

## 🚀 Deployment

### Railway

```bash
# Push to GitHub
git push origin main

# Deploy via Railway dashboard
# Add environment variables
# Railway auto-detects FastAPI
```

### Fly.io

```bash
fly launch
fly secrets set OPENAI_API_KEY=your-key
fly secrets set SERPER_API_KEY=your-key
fly deploy
```

## 📊 Monitoring

View logs:
```bash
# Railway: Check dashboard
# Fly.io: fly logs
# Local: Check terminal output
```

## 🐛 Troubleshooting

**"Module not found: trip_planner"**
```bash
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/../trip_planner/src"
```

**"CORS error"**
- Update `allow_origins` in `main.py`
- Add your frontend URL

## 📞 Support

See main [README.md](../README.md) for full documentation.

