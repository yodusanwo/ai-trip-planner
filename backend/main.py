"""
FastAPI Backend for AI Trip Planner
Provides REST API and SSE endpoints for the Next.js frontend
"""

import os
import sys
import asyncio
import uuid
import json
import threading
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Set library path for WeasyPrint on macOS
if sys.platform == 'darwin':
    homebrew_lib_path = '/opt/homebrew/lib'
    if os.path.exists(homebrew_lib_path):
        current_dyld = os.environ.get('DYLD_LIBRARY_PATH', '')
        if homebrew_lib_path not in current_dyld:
            os.environ['DYLD_LIBRARY_PATH'] = f'{homebrew_lib_path}:{current_dyld}'.strip(':')

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field
import uvicorn
from io import BytesIO

# Lazy import WeasyPrint - only import when needed to avoid startup crashes
# WeasyPrint requires system libraries that may not be available on all platforms
WEASYPRINT_AVAILABLE = False
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"⚠️  WeasyPrint not available: {e}")
    print("⚠️  PDF generation will be disabled. The app will still run normally.")
    HTML = None

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
# Note: In Docker, src/ is in the same directory as main.py (backend/)
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
# Allow origins from environment variable or default to localhost
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Can be set via CORS_ORIGINS env var (comma-separated)
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


class SpellCheckRequest(BaseModel):
    text: str = Field(..., min_length=1)


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


def spell_check_text(text: str) -> Dict[str, Any]:
    """Check spelling and return suggestions for misspelled words"""
    try:
        from spellchecker import SpellChecker
        
        spell = SpellChecker()
        
        # Split text into words (handle punctuation and preserve case for display)
        words_lower = re.findall(r'\b\w+\b', text.lower())
        words_original = re.findall(r'\b\w+\b', text)
        
        # Find misspelled words (using lowercase for checking)
        misspelled_lower = spell.unknown(words_lower)
        
        # Map back to original case
        word_map = {word.lower(): word for word in words_original}
        misspelled_original = [word_map.get(word, word) for word in misspelled_lower]
        
        suggestions = {}
        for word_lower in misspelled_lower:
            # Get suggestions (top 3)
            candidates = list(spell.candidates(word_lower))[:3] if spell.candidates(word_lower) else []
            # Use original case for the key
            word_original = word_map.get(word_lower, word_lower)
            suggestions[word_original] = candidates
        
        result = {
            "has_errors": len(misspelled_lower) > 0,
            "misspelled_words": misspelled_original,
            "suggestions": suggestions,
            "original_text": text
        }
        
        print(f"[Spell Check] Found {len(misspelled_lower)} misspelled words: {misspelled_original}")
        return result
        
    except ImportError as e:
        print(f"[Spell Check] ImportError: {e}")
        # Fallback if spellchecker not available
        return {
            "has_errors": False,
            "misspelled_words": [],
            "suggestions": {},
            "original_text": text,
            "error": "Spell checker not available. Please install pyspellchecker."
        }
    except Exception as e:
        print(f"[Spell Check] Exception: {e}")
        import traceback
        traceback.print_exc()
        return {
            "has_errors": False,
            "misspelled_words": [],
            "suggestions": {},
            "original_text": text,
            "error": str(e)
        }


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


def extract_budget_overview(research_output: str) -> Optional[Dict[str, Any]]:
    """Extract budget overview from researcher agent output"""
    try:
        # Look for BUDGET OVERVIEW section
        budget_pattern = r'BUDGET OVERVIEW:?\s*(.*?)(?=\n\n|\n[A-Z]|$)'
        match = re.search(budget_pattern, research_output, re.IGNORECASE | re.DOTALL)
        
        if not match:
            return None
        
        budget_text = match.group(1).strip()
        
        # Extract overall budget
        overall_match = re.search(r'Overall Budget:\s*\$?([\d,]+)\s*-\s*\$?([\d,]+)/day', budget_text, re.IGNORECASE)
        overall_min = overall_match.group(1).replace(',', '') if overall_match else None
        overall_max = overall_match.group(2).replace(',', '') if overall_match else None
        
        # Extract accommodation
        acc_match = re.search(r'Accommodation:\s*\$?([\d,]+)-?\$?([\d,]+)?', budget_text, re.IGNORECASE)
        acc_min = acc_match.group(1).replace(',', '') if acc_match else None
        acc_max = acc_match.group(2).replace(',', '') if acc_match and acc_match.group(2) else acc_min
        
        # Extract food
        food_match = re.search(r'Food:\s*\$?([\d,]+)-?\$?([\d,]+)?', budget_text, re.IGNORECASE)
        food_min = food_match.group(1).replace(',', '') if food_match else None
        food_max = food_match.group(2).replace(',', '') if food_match and food_match.group(2) else food_min
        
        # Extract transportation
        trans_match = re.search(r'Transportation:\s*\$?([\d,]+)-?\$?([\d,]+)?', budget_text, re.IGNORECASE)
        trans_min = trans_match.group(1).replace(',', '') if trans_match else None
        trans_max = trans_match.group(2).replace(',', '') if trans_match and trans_match.group(2) else trans_min
        
        # Build budget overview dict
        budget_overview = {}
        
        if overall_min and overall_max:
            budget_overview['overall'] = f"${overall_min} - ${overall_max}/day"
        
        if acc_min:
            if acc_max and acc_max != acc_min:
                budget_overview['accommodation'] = f"${acc_min}-${acc_max}"
            else:
                budget_overview['accommodation'] = f"${acc_min}"
        
        if food_min:
            if food_max and food_max != food_min:
                budget_overview['food'] = f"${food_min}-${food_max}"
            else:
                budget_overview['food'] = f"${food_min}"
        
        if trans_min:
            # Check for special notes (like rail passes)
            trans_note_match = re.search(r'Transportation:.*?\((.*?)\)', budget_text, re.IGNORECASE)
            if trans_note_match:
                budget_overview['transportation'] = f"${trans_min}-${trans_max}" if trans_max and trans_max != trans_min else f"${trans_min}"
                budget_overview['transportation_note'] = trans_note_match.group(1)
            else:
                budget_overview['transportation'] = f"${trans_min}-${trans_max}" if trans_max and trans_max != trans_min else f"${trans_min}"
        
        return budget_overview if budget_overview else None
        
    except Exception as e:
        print(f"Error extracting budget overview: {e}")
        return None


def html_to_pdf(html_content: str) -> bytes:
    """Convert HTML content to PDF bytes"""
    if not WEASYPRINT_AVAILABLE or HTML is None:
        raise Exception(
            "PDF generation is not available. WeasyPrint requires system libraries "
            "that are not installed. Please install system dependencies or use HTML download instead."
        )
    
    try:
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()
        return pdf_bytes
    except Exception as e:
        print(f"Error converting HTML to PDF: {e}")
        raise Exception(f"Failed to generate PDF: {str(e)}")


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
            
            # Extract budget overview from research task output
            try:
                research_output = ""
                if hasattr(result, 'tasks_output') and result.tasks_output:
                    for task_output in result.tasks_output:
                        if hasattr(task_output, 'task') and 'research' in str(task_output.task).lower():
                            research_output = str(task_output.raw) if hasattr(task_output, 'raw') else str(task_output)
                            break
                elif hasattr(result, 'raw'):
                    research_output = str(result.raw)
                else:
                    research_output = str(result)
                
                budget_overview = extract_budget_overview(research_output)
                if budget_overview:
                    print(f"[{trip_id}] 💰 Extracted budget overview: {budget_overview}")
                    result_container["budget_overview"] = budget_overview
            except Exception as e:
                print(f"[{trip_id}] ⚠️  Error extracting budget overview: {e}")
            
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
        
        # Extract budget overview from research task output
        try:
            # Get research task output from crew result
            research_output = ""
            if hasattr(result, 'tasks_output') and result.tasks_output:
                # Try to find research task output
                for task_output in result.tasks_output:
                    if hasattr(task_output, 'task') and 'research' in str(task_output.task).lower():
                        research_output = str(task_output.raw) if hasattr(task_output, 'raw') else str(task_output)
                        break
            elif hasattr(result, 'raw'):
                research_output = str(result.raw)
            else:
                research_output = str(result)
            
            # Extract budget overview
            budget_overview = extract_budget_overview(research_output)
            if budget_overview:
                print(f"[{trip_id}] 💰 Extracted budget overview: {budget_overview}")
                result_container["budget_overview"] = budget_overview
            else:
                print(f"[{trip_id}] ⚠️  Could not extract budget overview from research output")
        except Exception as e:
            print(f"[{trip_id}] ⚠️  Error extracting budget overview: {e}")
        
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
        trip_progress[trip_id].update({
            "current_agent": "trip_researcher",
            "current_step": 1,
            "total_steps": 3,
            "progress": 10,
            "message": "Starting research agent...",
            "debug": {
                "current_task": 1,
                "task_name": "research_task",
                "assigned_agent": "Research Agent (trip_researcher)",
                "agent_status": "starting",
            }
        })
        await asyncio.sleep(0.2)
        
        trip_progress[trip_id].update({
            "current_agent": "trip_researcher",
            "current_step": 1,
            "total_steps": 3,
            "progress": 15,
            "message": "Researching destination and gathering information...",
            "debug": {
                "current_task": 1,
                "task_name": "research_task",
                "assigned_agent": "Research Agent (trip_researcher)",
                "agent_status": "working",
            }
        })
        await asyncio.sleep(0.2)
        
        # Start crew in a separate thread with shared progress dictionary
        result_container = {"result": None, "success": False, "error": None, "elapsed_time": 0, "budget_overview": None}
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
                    # Check if budget overview is available after research completes
                    if result_container.get("budget_overview"):
                        trip_progress[trip_id]["budget_overview"] = result_container["budget_overview"]
                elif current_step == 3:
                    message = "Creating your personalized itinerary..."
                else:
                    message = f"{agent_name} is working... ({overall_progress}% complete)"
                
                # Determine task name for debug info
                task_name_map = {
                    0: "research_task",
                    1: "review_task",
                    2: "planning_task",
                }
                task_name = task_name_map.get(current_task, "unknown_task")
                
                trip_progress[trip_id].update({
                    "current_agent": agent_id,
                    "current_step": current_step,
                    "total_steps": total_steps,
                    "progress": overall_progress,
                    "message": message,
                    "estimated_time_remaining": max(0, int(total_estimated - elapsed)),
                    "debug": {
                        "current_task": current_step,
                        "task_name": task_name,
                        "assigned_agent": f"{agent_name} ({agent_id})",
                        "agent_status": "working",
                        "elapsed_time": int(elapsed),
                        "remaining_time": int(total_estimated - elapsed),
                    }
                })
                last_update_time = time.time()
            
            await asyncio.sleep(1)  # Check every second
        
        # Wait for thread to complete
        crew_thread.join(timeout=5)
        
        # Check if crew completed successfully
        if not result_container["success"]:
            raise Exception(result_container.get("error", "Crew execution failed"))
        
        # Store budget overview if available (after research completes)
        if result_container.get("budget_overview"):
            trip_progress[trip_id]["budget_overview"] = result_container["budget_overview"]
            print(f"[{trip_id}] 💰 Budget overview stored in progress")
        
        # Update progress - Planning phase completion
        trip_progress[trip_id].update({
            "current_agent": "trip_planner",
            "current_step": 3,
            "total_steps": 3,
            "progress": 90,
            "message": "Processing final itinerary...",
            "debug": {
                "current_task": 3,
                "task_name": "planning_task",
                "assigned_agent": "Planning Agent (trip_planner)",
                "agent_status": "working",
            }
        })
        await asyncio.sleep(0.2)
        
        # Extract HTML content from CrewAI result
        # CrewAI returns results in memory, not as files
        html_content = None
        
        # Try to get result from the crew execution
        if result_container.get("result"):
            result = result_container["result"]
            
            # Extract HTML from the result object
            # CrewAI results can be accessed via various attributes
            if hasattr(result, 'tasks_output') and result.tasks_output:
                # Get the last task output (planning task)
                for task_output in reversed(result.tasks_output):
                    output_str = str(task_output.raw) if hasattr(task_output, 'raw') else str(task_output)
                    if output_str and len(output_str) > 100:  # Likely contains the HTML
                        html_content = output_str
                        break
            elif hasattr(result, 'raw'):
                html_content = str(result.raw)
            elif hasattr(result, 'output'):
                html_content = str(result.output)
            else:
                html_content = str(result)
        
        # Fallback: Try reading from file if result extraction didn't work
        if not html_content or len(html_content) < 100:
            output_file = Path("output/trip_plan.html")
            if not output_file.exists():
                output_file = Path(__file__).parent.parent / "output" / "trip_plan.html"
            if output_file.exists():
                with open(output_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
        
        if html_content and len(html_content) > 100:
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
            trip_progress[trip_id].update({
                "status": "completed",
                "current_agent": None,
                "current_step": 3,
                "total_steps": 3,
                "progress": 100,
                "message": "Trip planning completed successfully!",
                "estimated_time_remaining": 0,
                "debug": {
                    "current_task": 3,
                    "task_name": "planning_task",
                    "assigned_agent": "Planning Agent (trip_planner)",
                    "agent_status": "complete",
                    "all_tasks": [
                        {"task": "research_task", "agent": "Research Agent (trip_researcher)", "status": "complete"},
                        {"task": "review_task", "agent": "Review Agent (trip_reviewer)", "status": "complete"},
                        {"task": "planning_task", "agent": "Planning Agent (trip_planner)", "status": "complete"},
                    ]
                }
            })
            print(f"[{trip_id}] ✅ Trip planning completed successfully!")
        else:
            raise Exception(f"Could not extract HTML content from CrewAI result. Result container: {result_container}")
            
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
        "debug": {
            "current_task": None,
            "task_name": None,
            "assigned_agent": None,
            "agent_status": "waiting",
        }
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


@app.post("/api/spell-check")
async def spell_check(request: SpellCheckRequest):
    """Spell check text and return suggestions"""
    try:
        print(f"[Spell Check] Received request for text: '{request.text}'")
        result = spell_check_text(request.text)
        print(f"[Spell Check] Result: has_errors={result.get('has_errors')}, misspelled={result.get('misspelled_words')}")
        return result
    except Exception as e:
        print(f"[Spell Check] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Spell check failed: {str(e)}")


@app.get("/api/trips/{trip_id}/result/pdf")
async def get_result_pdf(trip_id: str):
    """Get the final trip plan as a PDF download"""
    if trip_id not in trip_results:
        # Check if still in progress
        if trip_id in trip_progress:
            status = trip_progress[trip_id]["status"]
            if status == "running":
                raise HTTPException(status_code=202, detail="Trip planning still in progress")
            elif status == "error":
                raise HTTPException(status_code=500, detail="Trip planning failed")
        
        raise HTTPException(status_code=404, detail="Trip result not found")
    
    try:
        html_content = trip_results[trip_id]
        pdf_bytes = html_to_pdf(html_content)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=trip_plan_{trip_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


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

