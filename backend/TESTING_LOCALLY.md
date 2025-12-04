# Testing Locally

This guide helps you test URL generation and the full CrewAI flow locally without deploying to Railway.

## Prerequisites

1. **Activate the virtual environment** (recommended):
   ```bash
   cd backend
   source venv/bin/activate  # On macOS/Linux
   # OR
   venv\Scripts\activate     # On Windows
   ```
   
   You should see `(venv)` in your terminal prompt when activated.

2. Make sure you have all environment variables set in `backend/.env`:
   - `GOOGLE_PLACES_API_KEY`
   - `OPENAI_API_KEY`
   - `SERPER_API_KEY`

3. Install dependencies (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

## Test 1: URL Generation Only

Test if Google Places API URLs are being generated correctly:

```bash
cd backend
python test_urls.py
```

This will:
- Test URL generation for problematic places (Musée d'Orsay, Louvre, etc.)
- Show the generated URLs
- Validate URL format (check for `query_place_id`, detect CID format)
- Report any issues

**What to look for:**
- ✅ All URLs should have `query_place_id` parameter
- ✅ URLs should use `/search/` format, not `/cid=` format
- ✅ Place IDs should be in the URLs

## Test 2: Full CrewAI Flow

Test the complete flow including agent execution:

```bash
cd backend
python test_local_crew.py
```

This will:
- Run the full CrewAI flow locally (3-day Paris trip)
- Extract HTML from the result
- Analyze URLs in the HTML output
- Save HTML to `test_output.html` for inspection
- Report URL issues

**What to look for:**
- Check if URLs in the HTML match what was generated in Test 1
- Verify URLs for problematic places are correct
- Open `test_output.html` in a browser to see the actual result

## Test 3: Compare with Production Logs

After running tests locally, compare with Railway logs:

1. **Local test URLs** (from `test_urls.py`):
   - These are what the API generates

2. **CrewAI output URLs** (from `test_local_crew.py`):
   - These are what the agent includes in HTML

3. **Production logs** (from Railway):
   - Check `[Google Places]` logs for API URLs
   - Check `[trip_xxx] 🔗 URL Analysis` for stored HTML URLs
   - Check `[PDF] 🔗 URLs BEFORE PDF` for PDF generation URLs

## Troubleshooting

### URLs are correct in Test 1 but wrong in Test 2
- **Issue**: Agent is modifying URLs
- **Solution**: Check `crew.py` planning task instructions
- **Fix**: Ensure instructions explicitly say to copy exact URLs

### URLs are correct in Test 2 but wrong in production
- **Issue**: Something in production is modifying URLs
- **Solution**: Check Railway logs at each stage:
  - After HTML extraction
  - Before PDF generation
  - In HTML result endpoint

### URLs are wrong in Test 1
- **Issue**: URL generation code has a bug
- **Solution**: Check `google_places.py` URL construction logic
- **Fix**: Verify `query_place_id` is being included correctly

## Quick Test Commands

```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# 3. Test URL generation only (fast, ~30 seconds)
python test_urls.py

# 4. Test full flow (slower, ~5-10 minutes)
python test_local_crew.py

# 5. View the generated HTML
open test_output.html  # macOS
# OR
start test_output.html  # Windows
```

**Note:** If you don't activate the virtual environment, make sure all dependencies are installed globally, or the scripts may fail with import errors.

## Expected Output

### test_urls.py output:
```
📍 Testing: Musée d'Orsay
  ✅ Found: Musée d'Orsay
  Place ID: ChIJ...
  🔗 Generated URL: https://www.google.com/maps/search/?api=1&query=Musée+d'Orsay&query_place_id=ChIJ...
  ✅ URL format looks correct
```

### test_local_crew.py output:
```
🔗 URL Analysis:
  Total links: 15
  Google Maps links: 15
  📍 Musée d'Orsay: https://www.google.com/maps/search/?api=1&query=Musée+d'Orsay&query_place_id=ChIJ...
  ✅ All URLs look correct!
```

## Next Steps

1. Run both tests locally
2. Compare URLs with production logs
3. Identify where URLs are being modified
4. Fix the issue at that stage

