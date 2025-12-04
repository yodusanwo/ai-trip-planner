# Switching Between Debugging and Production Versions

## Current Version: Debugging Mode (URLs Only)

The current `crew.py` is set to **debugging mode** - it outputs only URLs to help diagnose URL issues.

## Files Available:

1. **`crew.py`** - Current debugging version (outputs only URLs)
2. **`crew.py.original_html_version`** - Original HTML output version (production-ready)
3. **`crew.py.backup`** - Backup of debugging version

## To Switch Back to HTML Output Version:

```bash
cd backend/src/trip_planner
cp crew.py.original_html_version crew.py
```

## To Switch Back to Debugging Version:

```bash
cd backend/src/trip_planner
cp crew.py.backup crew.py
```

## What Each Version Does:

### Debugging Version (Current)
- Outputs ONLY URLs in format: `Place Name: URL`
- No HTML, no descriptions, no addresses
- Helps diagnose if URLs are being modified during output

### HTML Output Version (Original)
- Outputs full HTML itinerary with:
  - Accommodation options section
  - Daily structure with Morning/Afternoon/Evening
  - All place details (name, address, rating, links)
  - Proper HTML formatting

## After Switching:

1. Commit the change:
   ```bash
   git add backend/src/trip_planner/crew.py
   git commit -m "Switch back to HTML output version"
   git push origin main
   ```

2. Railway will automatically redeploy

## Quick Commands:

```bash
# Switch to HTML version
cp backend/src/trip_planner/crew.py.original_html_version backend/src/trip_planner/crew.py

# Switch to debugging version  
cp backend/src/trip_planner/crew.py.backup backend/src/trip_planner/crew.py
```

