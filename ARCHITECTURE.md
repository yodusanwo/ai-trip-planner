# Next.js + FastAPI Architecture

This document describes the new Next.js + FastAPI architecture for the AI Trip Planner application.

## Overview

The application is split into two main components:

1. **Backend (FastAPI)**: Python-based API server handling CrewAI integration and business logic
2. **Frontend (Next.js)**: React-based web application with TypeScript and Tailwind CSS

## Architecture Diagram

```
┌─────────────────┐
│   Next.js App   │  (Frontend - Port 3000)
│   (TypeScript)  │
└────────┬────────┘
         │ HTTP/REST + SSE
         │
┌────────▼────────┐
│  FastAPI Server │  (Backend - Port 8000)
│   (Python)      │
└────────┬────────┘
         │
┌────────▼────────┐
│   CrewAI Crew   │
│  (AI Agents)    │
└─────────────────┘
```

## Backend (FastAPI)

### Location
`/backend`

### Key Features
- RESTful API endpoints
- Server-Sent Events (SSE) for real-time progress tracking
- Rate limiting and cost management
- Security features (input validation, suspicious pattern detection)
- CrewAI integration

### API Endpoints

#### `GET /`
Health check endpoint

#### `GET /api/usage/{client_id}`
Get usage statistics for a client
- Returns: trips today, trips this hour, daily cost, cost cap, can_create_trip status

#### `POST /api/trips`
Create a new trip planning request
- Request body: `TripRequest` (destination, duration, budget, travel_style, special_requirements)
- Returns: trip_id, client_id, status

#### `GET /api/trips/{trip_id}/progress`
Get current progress of a trip planning request
- Returns: status, current_agent, progress percentage, message, estimated_time_remaining

#### `GET /api/trips/{trip_id}/progress/stream`
Stream progress updates using Server-Sent Events (SSE)
- Returns: Real-time progress updates as JSON events

#### `GET /api/trips/{trip_id}/result`
Get the final HTML result of a completed trip
- Returns: trip_id, html_content

### Security Features

1. **Rate Limiting**
   - Maximum trips per hour: 5
   - Maximum trips per day: 20
   - Configurable via `security_config.py`

2. **Cost Management**
   - Daily cost cap: $10.00 USD
   - Estimated cost per trip: $0.03 USD
   - Tracks usage per client

3. **Input Validation**
   - Maximum destination length: 100 characters
   - Maximum duration: 30 days
   - Maximum special requirements: 500 characters
   - Suspicious pattern detection (SQL injection, XSS, path traversal)

### Running the Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The backend will run on `http://localhost:8000`

## Frontend (Next.js)

### Location
`/frontend`

### Key Features
- TypeScript for type safety
- Tailwind CSS for styling
- Real-time progress tracking with SSE
- Responsive design
- Client-side state management

### Components

#### `TripForm`
Form component for creating trip planning requests
- Destination input
- Duration slider (1-30 days)
- Budget selector (budget/moderate/luxury)
- Travel style selection (up to 5 options)
- Special requirements textarea

#### `ProgressTracker`
Real-time progress tracking component
- Uses SSE to receive updates
- Falls back to polling if SSE unavailable
- Shows progress bar, current agent, status messages

#### `TripResult`
Displays the final HTML trip plan
- Embedded iframe preview
- Download HTML functionality
- Raw HTML view toggle

#### `UsageStats`
Displays usage statistics
- Trips this hour
- Trips today
- Daily cost and cost cap
- Visual progress indicators

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

## Environment Variables

### Backend
- `OPENAI_API_KEY`: Required - Your OpenAI API key
- `SERPER_API_KEY`: Required - Your Serper API key for search functionality

### Frontend
- `NEXT_PUBLIC_API_URL`: Optional - Backend API URL (defaults to `http://localhost:8000`)

## Deployment

### Backend (Railway)

1. Create a new Railway project
2. Connect your GitHub repository
3. Set the root directory to `/backend`
4. Add environment variables:
   - `OPENAI_API_KEY`
   - `SERPER_API_KEY`
5. Railway will automatically detect and deploy using `railway.json` and `Procfile`

### Frontend (Vercel)

1. Import your GitHub repository to Vercel
2. Set the root directory to `/frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Railway backend URL
4. Deploy

## Development Workflow

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open `http://localhost:3000` in your browser

## API Communication Flow

1. User fills out trip form in frontend
2. Frontend sends POST request to `/api/trips`
3. Backend validates input and checks rate limits
4. Backend starts CrewAI crew in background task
5. Frontend connects to SSE endpoint `/api/trips/{trip_id}/progress/stream`
6. Backend sends progress updates via SSE
7. When complete, frontend fetches result from `/api/trips/{trip_id}/result`
8. Frontend displays HTML trip plan

## Security Considerations

- Input validation on all user inputs
- Rate limiting per client (using client_id)
- Cost caps to prevent excessive API usage
- CORS configured for frontend origin only
- Suspicious pattern detection
- No SQL injection vulnerabilities (no database queries)

## Future Improvements

- [ ] Add database for persistent storage
- [ ] Implement user authentication
- [ ] Add WebSocket support for bidirectional communication
- [ ] Implement caching for trip results
- [ ] Add analytics and monitoring
- [ ] Implement request queuing for high load
- [ ] Add email notifications for completed trips

