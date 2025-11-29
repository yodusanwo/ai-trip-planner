# 🚀 Streamlit Deployment Guide

## Local Development

### Prerequisites
- Python 3.10-3.13
- OpenAI API Key
- Serper API Key

### Setup

1. **Install dependencies:**
```bash
cd trip_planner
uv sync
# or
pip install -r requirements.txt
```

2. **Configure environment variables:**
Create a `.env` file in the `trip_planner` directory:
```env
OPENAI_API_KEY=your-openai-api-key-here
SERPER_API_KEY=your-serper-api-key-here
MODEL=gpt-4o-mini
```

3. **Run the Streamlit app:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Ensure these files are in your repo:**
- ✅ `app.py` - Main Streamlit application
- ✅ `requirements.txt` - Python dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `src/trip_planner/` - CrewAI crew code
- ✅ `.gitignore` - Excludes `.env` and sensitive files

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**

2. **Sign in with GitHub**

3. **Click "New app"**

4. **Configure your app:**
   - **Repository:** Select your GitHub repo
   - **Branch:** `main` (or your default branch)
   - **Main file path:** `trip_planner/app.py`
   - **App URL:** Choose a custom URL (e.g., `my-trip-planner`)

5. **Add secrets:**
   Click "Advanced settings" → "Secrets" and add:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key-here"
   SERPER_API_KEY = "your-serper-api-key-here"
   MODEL = "gpt-4o-mini"
   ```

6. **Click "Deploy!"**

Your app will be live at `https://your-app-name.streamlit.app` in a few minutes!

---

## Other Deployment Options

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t trip-planner .
docker run -p 8501:8501 --env-file .env trip-planner
```

### Heroku Deployment

1. Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

3. Deploy:
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key
heroku config:set SERPER_API_KEY=your-key
heroku config:set MODEL=gpt-4o-mini
git push heroku main
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ Yes |
| `SERPER_API_KEY` | Your Serper API key for search | ✅ Yes |
| `MODEL` | OpenAI model to use (default: gpt-4o-mini) | ❌ No |

---

## Performance Tips

✅ **Already Optimized:**
- Using `gpt-4o-mini` (fastest model)
- Max iterations: 5 per agent
- Max RPM: 30
- No delegation or memory overhead
- Concise task descriptions

⚡ **Expected Performance:**
- Execution time: 30-60 seconds
- Cost per trip: ~$0.01-0.05

---

## Troubleshooting

### App won't start
- Check that all dependencies are installed
- Verify `.env` file exists with correct API keys
- Ensure you're in the correct directory

### API errors
- Verify API keys are valid
- Check OpenAI account has credits
- Ensure Serper API key is active

### Slow execution
- Already optimized for speed with gpt-4o-mini
- Check your internet connection
- Verify API rate limits aren't exceeded

### Import errors
- Run `uv sync` or `pip install -r requirements.txt`
- Check Python version (3.10-3.13)

---

## Support

For issues or questions:
1. Check the [CrewAI Documentation](https://docs.crewai.com/)
2. Check the [Streamlit Documentation](https://docs.streamlit.io/)
3. Review the code comments in `app.py` and `crew.py`

---

## Security Notes

⚠️ **Never commit your `.env` file or API keys to GitHub!**

✅ Use `.gitignore` to exclude sensitive files
✅ Use Streamlit secrets for cloud deployment
✅ Rotate API keys if accidentally exposed


