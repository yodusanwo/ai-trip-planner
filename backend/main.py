"""
FastAPI Backend for AI Trip Planner
Handles CrewAI agent execution and provides REST API endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import hashlib
import re
from collections import defaultdict
import time

# Add the trip_planner module to the path
sys.path.append(str(Path(__file__).parent.parent / "trip_planner" / "src"))

from trip_planner.crew import TripPlanner

app = FastAPI(
    title="AI Trip Planner API",
    description="Backend API for AI-powered trip planning using CrewAI",
    version="1.0.0"
)

# CORS middleware - allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",   # Vercel preview/production
        # Add your custom domain here when ready
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for trip planning progress and results
trip_progress: Dict[str, Dict[str, Any]] = {}
trip_results: Dict[str, str] = {}

# Rate limiting storage
rate_limit_store: Dict[str, List[float]] = defaultdict(list)
usage_store: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
    "requests": 0,
    "cost": 0.0,
    "last_reset": time.time()
})

# Configuration
MAX_REQUESTS_PER_HOUR = 10
WEEKLY_COST_CAP = 10.0  # $10 per week
COST_PER_REQUEST = 0.15  # Estimated cost per trip generation


# Pydantic models
class TripRequest(BaseModel):
    destination: str = Field(..., min_length=2, max_length=100)
    duration: str = Field(..., min_length=2, max_length=50)
    budget_level: str = Field(..., pattern="^(Budget|Moderate|Luxury)$")
    travel_style: List[str] = Field(..., min_items=1, max_items=5)
    special_requirements: Optional[str] = Field(None, max_length=500)
    client_id: str = Field(..., description="Unique client identifier for rate limiting")


class TripResponse(BaseModel):
    trip_id: str
    status: str
    message: str


class ProgressUpdate(BaseModel):
    trip_id: str
    status: str
    current_agent: Optional[str] = None
    progress_percentage: int
    message: str
    estimated_time_remaining: Optional[int] = None


class TripResult(BaseModel):
    trip_id: str
    html_content: str
    created_at: str


# Validation functions
def validate_input(text: str, field_name: str) -> str:
    """Validate and sanitize user input"""
    # Remove potential XSS
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    # Remove SQL injection attempts
    sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC', 'UNION', 'SELECT']
    for keyword in sql_keywords:
        text = re.sub(rf'\b{keyword}\b', '', text, flags=re.IGNORECASE)
    
    # Limit length
    max_lengths = {
        "destination": 100,
        "duration": 50,
        "special_requirements": 500
    }
    max_len = max_lengths.get(field_name, 100)
    text = text[:max_len]
    
    return text.strip()


def check_rate_limit(client_id: str) -> tuple[bool, str]:
    """Check if client has exceeded rate limits"""
    current_time = time.time()
    
    # Clean old requests (older than 1 hour)
    rate_limit_store[client_id] = [
        req_time for req_time in rate_limit_store[client_id]
        if current_time - req_time < 3600
    ]
    
    # Check hourly rate limit
    if len(rate_limit_store[client_id]) >= MAX_REQUESTS_PER_HOUR:
        return False, f"Rate limit exceeded. Maximum {MAX_REQUESTS_PER_HOUR} requests per hour."
    
    # Check weekly cost cap
    usage = usage_store[client_id]
    
    # Reset weekly counter if needed
    if current_time - usage["last_reset"] > 604800:  # 7 days
        usage["requests"] = 0
        usage["cost"] = 0.0
        usage["last_reset"] = current_time
    
    if usage["cost"] >= WEEKLY_COST_CAP:
        return False, f"Weekly cost cap reached (${WEEKLY_COST_CAP}). Resets in {int((604800 - (current_time - usage['last_reset'])) / 3600)} hours."
    
    return True, "OK"


def update_usage(client_id: str):
    """Update usage statistics"""
    current_time = time.time()
    rate_limit_store[client_id].append(current_time)
    usage_store[client_id]["requests"] += 1
    usage_store[client_id]["cost"] += COST_PER_REQUEST


async def run_crew_async(trip_id: str, inputs: Dict[str, Any]):
    """Run CrewAI agents asynchronously and update progress"""
    try:
        # Initialize progress
        trip_progress[trip_id] = {
            "status": "running",
            "current_agent": "researcher",
            "progress_percentage": 0,
            "message": "Starting trip research...",
            "estimated_time_remaining": 180  # 3 minutes estimate
        }
        
        # Simulate progress updates (in real implementation, hook into CrewAI callbacks)
        await asyncio.sleep(2)
        trip_progress[trip_id].update({
            "current_agent": "researcher",
            "progress_percentage": 20,
            "message": "Researching destinations and attractions...",
            "estimated_time_remaining": 150
        })
        
        # Run the actual CrewAI crew
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: TripPlanner().crew().kickoff(inputs=inputs)
        )
        
        # Update progress - Researcher done
        trip_progress[trip_id].update({
            "current_agent": "reviewer",
            "progress_percentage": 40,
            "message": "Reviewing travel information...",
            "estimated_time_remaining": 100
        })
        await asyncio.sleep(1)
        
        # Update progress - Reviewer working
        trip_progress[trip_id].update({
            "current_agent": "reviewer",
            "progress_percentage": 60,
            "message": "Analyzing recommendations...",
            "estimated_time_remaining": 60
        })
        await asyncio.sleep(1)
        
        # Update progress - Planner working
        trip_progress[trip_id].update({
            "current_agent": "planner",
            "progress_percentage": 80,
            "message": "Creating your itinerary...",
            "estimated_time_remaining": 30
        })
        await asyncio.sleep(1)
        
        # Read the output file
        output_file = Path(__file__).parent.parent / "trip_planner" / "output" / "trip_plan.html"
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Clean HTML content
            html_content = html_content.strip()
            if html_content.startswith('```html'):
                html_content = html_content[7:]
            elif html_content.startswith('```'):
                html_content = html_content[3:]
            if html_content.endswith('```'):
                html_content = html_content[:-3]
            html_content = html_content.strip()
            
            # Store result
            trip_results[trip_id] = html_content
            
            # Update progress - Complete
            trip_progress[trip_id].update({
                "status": "completed",
                "current_agent": None,
                "progress_percentage": 100,
                "message": "Trip plan ready!",
                "estimated_time_remaining": 0
            })
        else:
            raise Exception("Output file not found")
            
    except Exception as e:
        trip_progress[trip_id].update({
            "status": "error",
            "message": f"Error: {str(e)}",
            "progress_percentage": 0
        })


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Trip Planner API",
        "version": "1.0.0"
    }


@app.post("/api/trips/plan", response_model=TripResponse)
async def plan_trip(request: TripRequest, background_tasks: BackgroundTasks):
    """
    Start a new trip planning request
    Returns a trip_id to track progress
    """
    # Rate limiting check
    allowed, message = check_rate_limit(request.client_id)
    if not allowed:
        raise HTTPException(status_code=429, detail=message)
    
    # Validate inputs
    try:
        destination = validate_input(request.destination, "destination")
        duration = validate_input(request.duration, "duration")
        special_requirements = validate_input(
            request.special_requirements or "", 
            "special_requirements"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    
    # Generate unique trip ID
    trip_hash = hashlib.md5(
        f"{destination}{duration}{request.budget_level}{','.join(sorted(request.travel_style))}{special_requirements}{datetime.now().isoformat()}".encode()
    ).hexdigest()
    
    # Update usage
    update_usage(request.client_id)
    
    # Prepare inputs for CrewAI
    inputs = {
        'destination': destination,
        'duration': duration,
        'budget_level': request.budget_level,
        'travel_style': ', '.join(request.travel_style),
        'special_requirements': special_requirements,
        'current_year': str(datetime.now().year)
    }
    
    # Start background task
    background_tasks.add_task(run_crew_async, trip_hash, inputs)
    
    return TripResponse(
        trip_id=trip_hash,
        status="started",
        message="Trip planning started. Use the trip_id to check progress."
    )


@app.get("/api/trips/{trip_id}/progress")
async def get_progress(trip_id: str):
    """Get the current progress of a trip planning request"""
    if trip_id not in trip_progress:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return trip_progress[trip_id]


@app.get("/api/trips/{trip_id}/stream")
async def stream_progress(trip_id: str):
    """
    Server-Sent Events endpoint for real-time progress updates
    """
    async def event_generator():
        while True:
            if trip_id in trip_progress:
                progress = trip_progress[trip_id]
                yield f"data: {json.dumps(progress)}\n\n"
                
                # Stop streaming if completed or error
                if progress["status"] in ["completed", "error"]:
                    break
            else:
                yield f"data: {json.dumps({'status': 'not_found'})}\n\n"
                break
            
            await asyncio.sleep(2)  # Update every 2 seconds
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/api/trips/{trip_id}/result", response_model=TripResult)
async def get_result(trip_id: str):
    """Get the final HTML result of a completed trip"""
    if trip_id not in trip_results:
        # Check if still in progress
        if trip_id in trip_progress:
            status = trip_progress[trip_id]["status"]
            if status == "running":
                raise HTTPException(status_code=202, detail="Trip planning still in progress")
            elif status == "error":
                raise HTTPException(status_code=500, detail="Trip planning failed")
        
        raise HTTPException(status_code=404, detail="Trip result not found")
    
    return TripResult(
        trip_id=trip_id,
        html_content=trip_results[trip_id],
        created_at=datetime.now().isoformat()
    )


@app.get("/api/usage/{client_id}")
async def get_usage(client_id: str):
    """Get usage statistics for a client"""
    usage = usage_store[client_id]
    current_time = time.time()
    
    # Calculate remaining quota
    remaining_requests = MAX_REQUESTS_PER_HOUR - len([
        t for t in rate_limit_store[client_id]
        if current_time - t < 3600
    ])
    
    remaining_budget = WEEKLY_COST_CAP - usage["cost"]
    
    # Time until reset
    time_until_reset = int((604800 - (current_time - usage["last_reset"])) / 3600)
    
    return {
        "requests_this_week": usage["requests"],
        "cost_this_week": round(usage["cost"], 2),
        "remaining_requests_this_hour": remaining_requests,
        "remaining_budget": round(remaining_budget, 2),
        "hours_until_reset": time_until_reset,
        "weekly_cap": WEEKLY_COST_CAP
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

