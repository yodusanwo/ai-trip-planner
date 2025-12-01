"""
FastAPI Backend for AI Trip Planner
Provides REST API and SSE endpoints for the Next.js frontend
"""

import os
import asyncio
import uuid
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

# Load environment variables
# Try loading from backend directory first, then parent directory
backend_dir = Path(__file__).parent
parent_dir = backend_dir.parent
load_dotenv(dotenv_path=backend_dir / '.env')
load_dotenv(dotenv_path=parent_dir / '.env', override=False)  # Don't override if already loaded

# Validate required environment variables
required_env_vars = ['OPENAI_API_KEY', 'SERPER_API_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    import warnings
    warnings.warn(
        f"Missing required environment variables: {', '.join(missing_vars)}\n"
        f"Please create a .env file in the project root or backend directory with:\n"
        f"OPENAI_API_KEY=your_openai_api_key\n"
        f"SERPER_API_KEY=your_serper_api_key\n"
        f"MODEL=gpt-4o-mini  # Optional, defaults to CrewAI's default if not specified",
        UserWarning
    )

# Optional: Set model if specified (CrewAI will use its default if not set)
if os.getenv('MODEL'):
    os.environ['OPENAI_MODEL_NAME'] = os.getenv('MODEL')

# Import CrewAI components
import sys
sys.path.append(str(Path(__file__).parent.parent))
from src.trip_planner.crew import TripPlanner

# Import security config (try local first, then parent)
try:
    from security_config import (
        MAX_TRIPS_PER_HOUR,
        MAX_TRIPS_PER_DAY,
        DAILY_COST_CAP_USD,
        ESTIMATED_COST_PER_TRIP,
        MAX_DESTINATION_LENGTH,
        MAX_DURATION_DAYS,
        MAX_SPECIAL_REQUIREMENTS_LENGTH,
        SUSPICIOUS_PATTERNS,
    )
except ImportError:
    # Fallback to parent directory
    sys.path.append(str(Path(__file__).parent.parent))
    from security_config import (
        MAX_TRIPS_PER_HOUR,
        MAX_TRIPS_PER_DAY,
        DAILY_COST_CAP_USD,
        ESTIMATED_COST_PER_TRIP,
        MAX_DESTINATION_LENGTH,
        MAX_DURATION_DAYS,
        MAX_SPECIAL_REQUIREMENTS_LENGTH,
        SUSPICIOUS_PATTERNS,
    )

app = FastAPI(
    title="AI Trip Planner API",
    description="Backend API for AI-powered trip planning with CrewAI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
trip_progress: Dict[str, Dict[str, Any]] = {}
trip_results: Dict[str, str] = {}
usage_tracking: Dict[str, Dict[str, Any]] = {}  # client_id -> usage stats


# ============================================================================
# Pydantic Models
# ============================================================================

class TripRequest(BaseModel):
    destination: str = Field(..., min_length=1, max_length=MAX_DESTINATION_LENGTH)
    duration: int = Field(..., ge=1, le=MAX_DURATION_DAYS)
    budget: Optional[str] = None
    travel_style: list[str] = Field(..., min_length=1, max_length=5)
    special_requirements: Optional[str] = Field(None, max_length=MAX_SPECIAL_REQUIREMENTS_LENGTH)
    client_id: Optional[str] = None


class TripResult(BaseModel):
    trip_id: str
    html_content: str


class UsageStats(BaseModel):
    client_id: str
    trips_today: int
    trips_this_hour: int
    daily_cost: float
    cost_cap: float
    can_create_trip: bool
    message: Optional[str] = None


# ============================================================================
# Security & Rate Limiting
# ============================================================================

def validate_input(text: str) -> bool:
    """Check for suspicious patterns"""
    import re
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    return True


def get_client_id(request_client_id: Optional[str] = None) -> str:
    """Get or create client ID for tracking"""
    if request_client_id:
        return request_client_id
    return f"client_{int(datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex[:8]}"


def check_rate_limits(client_id: str) -> tuple[bool, Optional[str]]:
    """Check if client can create a new trip"""
    now = datetime.now()
    today = now.date()
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    
    if client_id not in usage_tracking:
        usage_tracking[client_id] = {
            "trips_today": 0,
            "trips_this_hour": 0,
            "daily_cost": 0.0,
            "last_trip_time": None,
            "hour_start": hour_start,
        }
    
    usage = usage_tracking[client_id]
    
    # Reset hourly counter if new hour
    if usage["hour_start"] < hour_start:
        usage["trips_this_hour"] = 0
        usage["hour_start"] = hour_start
    
    # Check hourly limit
    if usage["trips_this_hour"] >= MAX_TRIPS_PER_HOUR:
        return False, f"Rate limit exceeded: Maximum {MAX_TRIPS_PER_HOUR} trips per hour"
    
    # Check daily limit
    if usage["trips_today"] >= MAX_TRIPS_PER_DAY:
        return False, f"Daily limit exceeded: Maximum {MAX_TRIPS_PER_DAY} trips per day"
    
    # Check cost cap
    if usage["daily_cost"] + ESTIMATED_COST_PER_TRIP > DAILY_COST_CAP_USD:
        return False, f"Daily cost cap exceeded: ${DAILY_COST_CAP_USD:.2f} limit reached"
    
    return True, None


def update_usage(client_id: str):
    """Update usage tracking after trip creation"""
    now = datetime.now()
    today = now.date()
    
    if client_id not in usage_tracking:
        usage_tracking[client_id] = {
            "trips_today": 0,
            "trips_this_hour": 0,
            "daily_cost": 0.0,
            "last_trip_time": None,
            "hour_start": now.replace(minute=0, second=0, microsecond=0),
        }
    
    usage = usage_tracking[client_id]
    
    # Reset daily counter if new day
    if usage.get("last_trip_time") and usage["last_trip_time"].date() < today:
        usage["trips_today"] = 0
        usage["daily_cost"] = 0.0
    
    usage["trips_today"] += 1
    usage["trips_this_hour"] += 1
    usage["daily_cost"] += ESTIMATED_COST_PER_TRIP
    usage["last_trip_time"] = now


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Trip Planner API", "status": "running"}


@app.get("/api/usage/{client_id}", response_model=UsageStats)
async def get_usage(client_id: str):
    """Get usage statistics for a client"""
    now = datetime.now()
    today = now.date()
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    
    if client_id not in usage_tracking:
        usage_tracking[client_id] = {
            "trips_today": 0,
            "trips_this_hour": 0,
            "daily_cost": 0.0,
            "last_trip_time": None,
            "hour_start": hour_start,
        }
    
    usage = usage_tracking[client_id]
    
    # Reset counters if needed
    if usage.get("last_trip_time") and usage["last_trip_time"].date() < today:
        usage["trips_today"] = 0
        usage["daily_cost"] = 0.0
    
    if usage["hour_start"] < hour_start:
        usage["trips_this_hour"] = 0
        usage["hour_start"] = hour_start
    
    can_create, message = check_rate_limits(client_id)
    
    return UsageStats(
        client_id=client_id,
        trips_today=usage["trips_today"],
        trips_this_hour=usage["trips_this_hour"],
        daily_cost=usage["daily_cost"],
        cost_cap=DAILY_COST_CAP_USD,
        can_create_trip=can_create,
        message=message,
    )


def run_crew_sync(trip_id: str, crew_inputs: Dict[str, Any], result_container: Dict[str, Any], progress_dict: Dict[str, Dict[str, Any]]):
    """Run CrewAI crew synchronously with real-time progress tracking"""
    try:
        # Create crew instance
        crew_instance = TripPlanner()
        crew = crew_instance.crew()
        
        print(f"\n{'='*60}")
        print(f"[{trip_id}] 🚀 Starting crew execution...")
        print(f"{'='*60}")
        
        # Log crew configuration
        print(f"[{trip_id}] 📋 Crew Configuration:")
        print(f"  - Agents: {len(crew.agents)}")
        print(f"  - Tasks: {len(crew.tasks)}")
        print(f"  - Process: {crew.process}")
        
        # Log agent details
        print(f"\n[{trip_id}] 👥 Agents:")
        for i, agent in enumerate(crew.agents):
            agent_name = getattr(agent, 'role', f'Agent {i+1}')
            print(f"  {i+1}. {agent_name}")
            print(f"     - Max Iterations: {getattr(agent, 'max_iter', 'N/A')}")
            print(f"     - Max RPM: {getattr(agent, 'max_rpm', 'N/A')}")
            print(f"     - Tools: {len(getattr(agent, 'tools', []))}")
        
        # Log task details
        print(f"\n[{trip_id}] 📝 Tasks:")
        task_agent_map = {
            0: ("trip_researcher", "Research Agent", "research_task", 20, 45),
            1: ("trip_reviewer", "Review Agent", "review_task", 45, 70),
            2: ("trip_planner", "Planning Agent", "planning_task", 70, 95),
        }
        
        for i, task in enumerate(crew.tasks):
            task_desc = getattr(task, 'description', f'Task {i+1}')
            assigned_agent = getattr(task, 'agent', None)
            agent_name = getattr(assigned_agent, 'role', 'Unassigned') if assigned_agent else 'Unassigned'
            
            if i < len(task_agent_map):
                agent_id, agent_display_name, task_name, _, _ = task_agent_map[i]
                print(f"  {i+1}. {task_name} → Assigned to: {agent_display_name} ({agent_id})")
                print(f"     Status: ⏳ Waiting")
            else:
                print(f"  {i+1}. {task_desc} → Assigned to: {agent_name}")
                print(f"     Status: ⏳ Waiting")
        
        print(f"{'='*60}\n")
        
        # Track task execution order (sequential process)
        tasks_completed = []
        
        # Run crew with streaming if available, otherwise use regular execution
        try:
            # Try streaming first
            stream_result = crew.kickoff(inputs=crew_inputs, stream=True)
            
            current_task_idx = 0
            for chunk in stream_result:
                # Parse chunk to determine current task/agent
                chunk_str = str(chunk).lower()
                
                # Update based on task completion detection
                if current_task_idx < len(task_agent_map):
                    agent_id, agent_name, task_name, progress_start, progress_end = task_agent_map[current_task_idx]
                    
                    # Log task start
                    if current_task_idx == 0 or "task" in chunk_str:
                        print(f"\n[{trip_id}] 🔄 Task {current_task_idx + 1}/3: {task_name}")
                        print(f"  → Assigned to: {agent_name} ({agent_id})")
                        print(f"  → Status: 🔄 Working...")
                    
                    # Calculate progress within current task
                    task_progress = progress_start + int((progress_end - progress_start) * 0.5)
                    
                    progress_dict[trip_id].update({
                        "current_agent": agent_id,
                        "progress": task_progress,
                        "message": f"{agent_name} is working...",
                    })
                
                # Check if we can detect task completion from chunk
                if "task" in chunk_str and "complete" in chunk_str:
                    if current_task_idx < len(task_agent_map):
                        agent_id, agent_name, task_name, _, _ = task_agent_map[current_task_idx]
                        print(f"[{trip_id}] ✅ Task {current_task_idx + 1}/3: {task_name} - COMPLETE")
                        print(f"  → Agent: {agent_name} ({agent_id})")
                        print(f"  → Status: ✅ Complete")
                    current_task_idx += 1
                    
        except (TypeError, AttributeError):
            # Streaming not available or not supported, use regular execution with monitoring
            print(f"[{trip_id}] ⚠️  Streaming not available, using regular execution")
            import time
            start_time = time.time()
            
            # Log each task before execution
            print(f"\n[{trip_id}] 📋 Executing tasks sequentially:")
            for i, task in enumerate(crew.tasks):
                if i < len(task_agent_map):
                    agent_id, agent_name, task_name, _, _ = task_agent_map[i]
                    print(f"  {i+1}. {task_name} → {agent_name} ({agent_id})")
            
            # Run crew (blocking)
            print(f"\n[{trip_id}] 🚀 Starting crew.kickoff()...")
            result = crew.kickoff(inputs=crew_inputs)
            
            # Since we can't get real-time updates, we'll update progress based on elapsed time
            # This is a fallback - the async function will handle progress updates
            elapsed = time.time() - start_time
            
            print(f"\n[{trip_id}] ✅ Crew execution completed in {elapsed:.2f} seconds")
            print(f"[{trip_id}] 📊 All tasks completed successfully")
            
            result_container["result"] = result
            result_container["success"] = True
            result_container["elapsed_time"] = elapsed
            return
        
        # Get final result (if streaming was used)
        print(f"\n[{trip_id}] 🔄 Getting final result...")
        result = crew.kickoff(inputs=crew_inputs)
        print(f"[{trip_id}] ✅ Crew execution completed")
        print(f"[{trip_id}] 📊 All tasks completed successfully")
        result_container["result"] = result
        result_container["success"] = True
        
    except Exception as e:
        print(f"[{trip_id}] Crew execution error: {e}")
        import traceback
        traceback.print_exc()
        result_container["error"] = str(e)
        result_container["success"] = False


async def run_crew_async(trip_id: str, inputs: Dict[str, Any]):
    """Run CrewAI crew asynchronously with progress tracking"""
    try:
        # Check for required environment variables
        if not os.getenv('OPENAI_API_KEY'):
            raise Exception("OPENAI_API_KEY is required. Please set it in your .env file.")
        if not os.getenv('SERPER_API_KEY'):
            raise Exception("SERPER_API_KEY is required. Please set it in your .env file.")
        
        # Prepare inputs
        crew_inputs = {
            "destination": inputs["destination"],
            "duration": inputs["duration"],
            "budget": inputs.get("budget", "moderate"),
            "travel_style": ", ".join(inputs.get("travel_style", [])),
            "special_requirements": inputs.get("special_requirements", ""),
        }
        
        # Update progress - Research phase start
        print(f"\n[{trip_id}] 🎯 Initializing Step 1/3: Research Task")
        print(f"  → Task: research_task")
        print(f"  → Assigned to: Research Agent (trip_researcher)")
        print(f"  → Status: 🔄 Starting...")
        
        trip_progress[trip_id].update({
            "current_agent": "trip_researcher",
            "current_step": 1,
            "total_steps": 3,
            "progress": 10,
            "message": "Starting research agent...",
        })
        await asyncio.sleep(0.2)
        
        trip_progress[trip_id].update({
            "current_agent": "trip_researcher",
            "current_step": 1,
            "total_steps": 3,
            "progress": 15,
            "message": "Researching destination and gathering information...",
        })
        print(f"[{trip_id}]  → Status: 🔄 Working...")
        await asyncio.sleep(0.2)
        
        # Start crew in a separate thread with shared progress dictionary
        result_container = {"result": None, "success": False, "error": None, "elapsed_time": 0}
        crew_thread = threading.Thread(
            target=run_crew_sync,
            args=(trip_id, crew_inputs, result_container, trip_progress),
            daemon=True
        )
        crew_thread.start()
        
        # Monitor progress in real-time during crew execution
        # Since CrewAI runs sequentially, we track progress through tasks
        import time
        start_time = time.time()
        task_durations = [40, 30, 50]  # Estimated durations for each task in seconds
        task_names = [
            ("trip_researcher", "Research Agent"),
            ("trip_reviewer", "Review Agent"),
            ("trip_planner", "Planning Agent")
        ]
        
        current_task = 0
        last_update_time = start_time
        
        while crew_thread.is_alive():
            elapsed = time.time() - start_time
            total_estimated = sum(task_durations)
            
            # Determine which task should be running based on elapsed time
            cumulative_time = 0
            for i, duration in enumerate(task_durations):
                if elapsed < cumulative_time + duration:
                    current_task = i
                    break
                cumulative_time += duration
            else:
                current_task = len(task_durations) - 1  # Last task
            
            # Calculate progress within current task
            task_start_time = sum(task_durations[:current_task])
            task_elapsed = max(0, elapsed - task_start_time)
            task_progress_pct = min(1.0, task_elapsed / task_durations[current_task] if current_task < len(task_durations) else 1.0)
            
            # Calculate overall progress
            base_progress = [0, 33, 66][current_task] if current_task < 3 else 95
            task_progress = int(task_progress_pct * 33)  # Each task is ~33% of total
            overall_progress = min(95, base_progress + task_progress)
            
            # Get agent info
            agent_id, agent_name = task_names[current_task] if current_task < len(task_names) else task_names[-1]
            
            # Update progress every 2 seconds or if significant change
            if time.time() - last_update_time >= 2:
                # Determine current step (1-based)
                current_step = current_task + 1
                total_steps = len(task_names)
                
                # Determine message based on current step
                if current_step == 1:
                    message = "Researching destination and gathering information..."
                elif current_step == 2:
                    message = "Reviewing and analyzing recommendations..."
                elif current_step == 3:
                    message = "Creating your personalized itinerary..."
                else:
                    message = f"{agent_name} is working... ({overall_progress}% complete)"
                
                # Debug logging
                task_name = task_names[current_task][1] if current_task < len(task_names) else "Unknown"
                print(f"[{trip_id}] 📊 Progress Update:")
                print(f"  → Step: {current_step}/{total_steps}")
                print(f"  → Task: {task_name}")
                print(f"  → Agent: {agent_name} ({agent_id})")
                print(f"  → Status: 🔄 Working")
                print(f"  → Progress: {overall_progress}%")
                print(f"  → Elapsed: {int(elapsed)}s | Remaining: ~{int(total_estimated - elapsed)}s")
                
                trip_progress[trip_id].update({
                    "current_agent": agent_id,
                    "current_step": current_step,
                    "total_steps": total_steps,
                    "progress": overall_progress,
                    "message": message,
                    "estimated_time_remaining": max(0, int(total_estimated - elapsed)),
                })
                last_update_time = time.time()
            
            await asyncio.sleep(1)  # Check every second
        
        # Wait for thread to complete
        crew_thread.join(timeout=5)
        
        # Check if crew completed successfully
        if not result_container["success"]:
            raise Exception(result_container.get("error", "Crew execution failed"))
        
        # Update progress - Planning phase completion
        print(f"\n[{trip_id}] 🎯 Finalizing Step 3/3: Planning Task")
        print(f"  → Task: planning_task")
        print(f"  → Assigned to: Planning Agent (trip_planner)")
        print(f"  → Status: 🔄 Processing final itinerary...")
        
        trip_progress[trip_id].update({
            "current_agent": "trip_planner",
            "current_step": 3,
            "total_steps": 3,
            "progress": 90,
            "message": "Processing final itinerary...",
        })
        await asyncio.sleep(0.2)
        
        # Read the output file (check both relative and absolute paths)
        output_file = Path("output/trip_plan.html")
        if not output_file.exists():
            # Try parent directory
            output_file = Path(__file__).parent.parent / "output" / "trip_plan.html"
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Clean HTML content
            html_content = html_content.strip()
            if html_content.startswith('```html'):
                html_content = html_content[7:]
            if html_content.startswith('```'):
                html_content = html_content[3:]
            if html_content.endswith('```'):
                html_content = html_content[:-3]
            html_content = html_content.strip()
            
            # Store result
            trip_results[trip_id] = html_content
            print(f"[{trip_id}] Stored result ({len(html_content)} characters)")
            
            # Update progress - Complete
            print(f"\n[{trip_id}] ✅ All Tasks Completed Successfully!")
            print(f"  → Task 1: research_task → ✅ Complete (Research Agent)")
            print(f"  → Task 2: review_task → ✅ Complete (Review Agent)")
            print(f"  → Task 3: planning_task → ✅ Complete (Planning Agent)")
            print(f"  → Final Status: ✅ All agents completed")
            
            trip_progress[trip_id].update({
                "status": "completed",
                "current_agent": None,
                "current_step": 3,
                "total_steps": 3,
                "progress": 100,
                "message": "Trip planning completed successfully!",
                "estimated_time_remaining": 0
            })
            print(f"[{trip_id}] ✅ Trip planning completed successfully!")
            print(f"{'='*60}\n")
        else:
            raise Exception(f"Output file not found at {output_file}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n[{trip_id}] ❌ ERROR OCCURRED!")
        print(f"  → Error Message: {error_msg}")
        print(f"  → Status: ❌ Failed")
        print(f"{'='*60}\n")
        trip_progress[trip_id].update({
            "status": "error",
            "message": f"Error: {error_msg}",
            "progress": 0,
        })


@app.post("/api/trips")
async def create_trip(request: TripRequest, background_tasks: BackgroundTasks):
    """Create a new trip planning request"""
    # Check for required environment variables first
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(
            status_code=500, 
            detail="OPENAI_API_KEY is not configured. Please set it in your .env file."
        )
    if not os.getenv('SERPER_API_KEY'):
        raise HTTPException(
            status_code=500, 
            detail="SERPER_API_KEY is not configured. Please set it in your .env file."
        )
    
    # Validate input
    if not validate_input(request.destination):
        raise HTTPException(status_code=400, detail="Invalid input detected")
    
    if request.special_requirements and not validate_input(request.special_requirements):
        raise HTTPException(status_code=400, detail="Invalid input in special requirements")
    
    # Get client ID
    client_id = get_client_id(request.client_id)
    
    # Check rate limits
    can_create, error_message = check_rate_limits(client_id)
    if not can_create:
        raise HTTPException(status_code=429, detail=error_message)
    
    # Generate trip ID
    trip_id = f"trip_{uuid.uuid4().hex[:12]}"
    
    # Initialize progress immediately so frontend can start tracking
    trip_progress[trip_id] = {
        "status": "running",
        "current_agent": None,
        "current_step": 0,
        "total_steps": 3,
        "progress": 0,
        "message": "Initializing trip planning...",
        "estimated_time_remaining": 120,
    }
    
    # Prepare inputs
    inputs = {
        "destination": request.destination,
        "duration": request.duration,
        "budget": request.budget or "moderate",
        "travel_style": request.travel_style,
        "special_requirements": request.special_requirements or "",
    }
    
    # Start background task
    background_tasks.add_task(run_crew_async, trip_id, inputs)
    
    # Update usage tracking
    update_usage(client_id)
    
    return {
        "trip_id": trip_id,
        "client_id": client_id,
        "status": "started",
        "message": "Trip planning started. Use the progress endpoint to track status."
    }


@app.get("/api/trips/{trip_id}/progress")
async def get_progress(trip_id: str):
    """Get progress of a trip planning request"""
    if trip_id not in trip_progress:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return trip_progress[trip_id]


@app.get("/api/trips/{trip_id}/progress/stream")
async def stream_progress(trip_id: str):
    """Stream progress updates using Server-Sent Events (SSE)"""
    async def event_generator():
        last_progress = None
        last_agent = None
        consecutive_same_updates = 0
        
        # Send initial connection message
        yield f"data: {json.dumps({'status': 'connected', 'trip_id': trip_id})}\n\n"
        
        while True:
            if trip_id not in trip_progress:
                yield f"data: {json.dumps({'error': 'Trip not found'})}\n\n"
                break
            
            current_progress = trip_progress[trip_id]
            current_status = current_progress["status"]
            current_agent = current_progress.get("current_agent")
            
            # Check if anything changed
            progress_changed = (
                last_progress != current_progress.get("progress") or
                last_agent != current_agent or
                current_progress.get("message") != (last_progress.get("message") if last_progress else None)
            )
            
            # Send update if something changed, or every 1 second if running
            if progress_changed or current_status == "running":
                yield f"data: {json.dumps(current_progress)}\n\n"
                last_progress = current_progress.copy() if isinstance(current_progress, dict) else current_progress
                last_agent = current_agent
                consecutive_same_updates = 0
                
                if current_status in ["completed", "error"]:
                    # Send final update
                    yield f"data: {json.dumps(current_progress)}\n\n"
                    break
            else:
                consecutive_same_updates += 1
                # Still send periodic updates even if nothing changed (every 3 seconds)
                if consecutive_same_updates >= 3:
                    yield f"data: {json.dumps(current_progress)}\n\n"
                    consecutive_same_updates = 0
            
            await asyncio.sleep(1)  # Check every second for more responsive updates
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
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
    )


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

