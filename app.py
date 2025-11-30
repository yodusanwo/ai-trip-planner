import streamlit as st
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import hashlib
import re

# Load environment variables
load_dotenv()

# Import the TripPlanner crew
from src.trip_planner.crew import TripPlanner

# Page configuration
st.set_page_config(
    page_title="AI Trip Planner - Plan Your Perfect Trip with AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Zora-Digital/trip_planner',
        'Report a bug': 'https://github.com/Zora-Digital/trip_planner/issues',
        'About': '''
        # AI Trip Planner
        
        Created by **Zora Digital** as a showcase of AI Agent capabilities.
        
        Plan your perfect trip with AI-powered research and recommendations.
        
        **Features:**
        - 🤖 Multi-agent AI system
        - ⚡ Fast execution (45s - 2.5min)
        - 📄 Beautiful HTML itineraries
        - 🔒 Enterprise-grade security
        
        Built with CrewAI and Streamlit.
        
        © 2024 Zora Digital
        '''
    }
)

# Add meta tags for SEO and social media
st.markdown("""
<meta name="description" content="AI Trip Planner by Zora Digital - A showcase of AI Agent capabilities. Plan your perfect trip with AI-powered agents. Get personalized day-by-day itineraries in 45 seconds to 2.5 minutes.">
<meta name="keywords" content="AI trip planner, travel itinerary, trip planning, AI travel agent, vacation planner, travel AI, CrewAI, automated trip planning, Zora Digital, AI agents, multi-agent system">
<meta name="author" content="Zora Digital">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:title" content="AI Trip Planner by Zora Digital - AI Agent Showcase">
<meta property="og:description" content="A showcase of AI Agent capabilities. Get personalized day-by-day travel itineraries powered by multi-agent AI system. Built by Zora Digital with CrewAI.">
<meta property="og:image" content="https://raw.githubusercontent.com/Zora-Digital/trip_planner/main/assets/og-image.png">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="AI Trip Planner by Zora Digital - AI Agent Showcase">
<meta name="twitter:description" content="A showcase of AI Agent capabilities. Get personalized day-by-day travel itineraries powered by multi-agent AI system. Built by Zora Digital.">
<meta name="twitter:image" content="https://raw.githubusercontent.com/Zora-Digital/trip_planner/main/assets/twitter-image.png">
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        border: none;
    }
    .agent-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 4px solid #667eea;
    }
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
        border-top: 1px solid #eee;
        margin-top: 3rem;
    }
    .footer-content {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    
    /* Mobile-specific fixes */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .sub-header {
            font-size: 1rem;
        }
        /* Ensure HTML preview content is responsive */
        iframe {
            width: 100% !important;
            max-width: 100% !important;
        }
    }
    
    /* Scroll to progress section on mobile */
    #progress-anchor {
        scroll-margin-top: 20px;
    }
</style>

<script>
    // Auto-scroll to progress section when trip planning starts
    function scrollToProgress() {
        const progressSection = document.getElementById('progress-anchor');
        if (progressSection) {
            progressSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
</script>
""", unsafe_allow_html=True)

# ============================================================================
# SECURITY FEATURES
# ============================================================================

# Configuration
MAX_TRIPS_PER_HOUR = 5
MAX_TRIPS_PER_DAY = 50
MAX_TRIPS_PER_WEEK = 100
WEEKLY_COST_CAP_USD = 10.0  # Maximum weekly spending
ESTIMATED_COST_PER_TRIP = 0.03  # Average cost per trip in USD

# Input validation limits
MAX_DESTINATION_LENGTH = 100
MAX_DURATION_DAYS = 30
MAX_SPECIAL_REQUIREMENTS_LENGTH = 500

def get_session_id():
    """Generate a unique session ID based on Streamlit session"""
    if 'session_id' not in st.session_state:
        # Use Streamlit's session ID if available, otherwise create one
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def validate_input(destination, duration, special_requirements):
    """Validate user inputs to prevent abuse and attacks"""
    errors = []
    
    # Validate destination
    if len(destination) > MAX_DESTINATION_LENGTH:
        errors.append(f"Destination must be less than {MAX_DESTINATION_LENGTH} characters")
    
    # Check for suspicious patterns (basic SQL injection prevention)
    suspicious_patterns = [
        r'(\bSELECT\b|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)',  # SQL keywords
        r'(<script|javascript:|onerror=)',  # XSS attempts
        r'(\.\.\/|\.\.\\)',  # Path traversal
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, destination, re.IGNORECASE) or \
           re.search(pattern, special_requirements, re.IGNORECASE):
            errors.append("Invalid characters detected in input")
            break
    
    # Validate duration
    duration_numbers = re.findall(r'\d+', duration)
    if duration_numbers:
        days = int(duration_numbers[0])
        if 'week' in duration.lower():
            days *= 7
        if days > MAX_DURATION_DAYS:
            errors.append(f"Trip duration cannot exceed {MAX_DURATION_DAYS} days")
    
    # Validate special requirements length
    if len(special_requirements) > MAX_SPECIAL_REQUIREMENTS_LENGTH:
        errors.append(f"Special requirements must be less than {MAX_SPECIAL_REQUIREMENTS_LENGTH} characters")
    
    return errors

def check_rate_limit():
    """Check if user has exceeded rate limits"""
    session_id = get_session_id()
    current_time = datetime.now()
    
    # Initialize rate limiting data
    if 'rate_limit_data' not in st.session_state:
        st.session_state.rate_limit_data = {
            'trips': [],
            'weekly_cost': 0.0,
            'last_reset': current_time.date(),
            'week_start': current_time.date() - timedelta(days=current_time.weekday())
        }
    
    rate_data = st.session_state.rate_limit_data
    
    # Calculate current week start (Monday)
    current_week_start = current_time.date() - timedelta(days=current_time.weekday())
    
    # Reset weekly counters if it's a new week
    if rate_data.get('week_start') != current_week_start:
        rate_data['trips'] = []
        rate_data['weekly_cost'] = 0.0
        rate_data['week_start'] = current_week_start
        rate_data['last_reset'] = current_time.date()
    
    # Remove trips older than 1 week
    one_week_ago = current_time - timedelta(days=7)
    rate_data['trips'] = [t for t in rate_data['trips'] if t > one_week_ago]
    
    # Check hourly limit
    one_hour_ago = current_time - timedelta(hours=1)
    trips_last_hour = len([t for t in rate_data['trips'] if t > one_hour_ago])
    if trips_last_hour >= MAX_TRIPS_PER_HOUR:
        return False, f"Rate limit exceeded: Maximum {MAX_TRIPS_PER_HOUR} trips per hour. Please try again later."
    
    # Check daily limit
    trips_today = len([t for t in rate_data['trips'] if t.date() == current_time.date()])
    if trips_today >= MAX_TRIPS_PER_DAY:
        return False, f"Daily limit exceeded: Maximum {MAX_TRIPS_PER_DAY} trips per day. Please try again tomorrow."
    
    # Check weekly limit
    trips_this_week = len(rate_data['trips'])
    if trips_this_week >= MAX_TRIPS_PER_WEEK:
        return False, f"Weekly limit exceeded: Maximum {MAX_TRIPS_PER_WEEK} trips per week. Resets on Monday."
    
    # Check weekly cost cap
    estimated_new_cost = rate_data['weekly_cost'] + ESTIMATED_COST_PER_TRIP
    if estimated_new_cost > WEEKLY_COST_CAP_USD:
        return False, f"Weekly cost cap reached (${WEEKLY_COST_CAP_USD:.2f}). Service will resume next Monday."
    
    return True, None

def record_trip():
    """Record a trip for rate limiting"""
    current_time = datetime.now()
    if 'rate_limit_data' not in st.session_state:
        st.session_state.rate_limit_data = {
            'trips': [],
            'weekly_cost': 0.0,
            'last_reset': current_time.date(),
            'week_start': current_time.date() - timedelta(days=current_time.weekday())
        }
    
    st.session_state.rate_limit_data['trips'].append(current_time)
    st.session_state.rate_limit_data['weekly_cost'] += ESTIMATED_COST_PER_TRIP

def get_usage_stats():
    """Get current usage statistics"""
    if 'rate_limit_data' not in st.session_state:
        return 0, 0, 0, 0.0
    
    rate_data = st.session_state.rate_limit_data
    current_time = datetime.now()
    
    # Trips in last hour
    one_hour_ago = current_time - timedelta(hours=1)
    trips_last_hour = len([t for t in rate_data['trips'] if t > one_hour_ago])
    
    # Trips today
    trips_today = len([t for t in rate_data['trips'] if t.date() == current_time.date()])
    
    # Trips this week
    trips_this_week = len(rate_data['trips'])
    
    # Cost this week
    cost_week = rate_data.get('weekly_cost', 0.0)
    
    return trips_last_hour, trips_today, trips_this_week, cost_week

# ============================================================================
# END SECURITY FEATURES
# ============================================================================

# Initialize session state
if 'crew_running' not in st.session_state:
    st.session_state.crew_running = False
if 'output_file' not in st.session_state:
    st.session_state.output_file = None

# Header
st.markdown('<h1 class="main-header">✈️ AI Trip Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plan your perfect trip with AI-powered research and recommendations</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🌟 Welcome!")
    
    st.markdown("""
    Our AI agents will help you plan the perfect trip:
    
    **🔍 Trip Researcher** - Finds the best attractions, restaurants, and activities
    
    **⭐ Trip Reviewer** - Analyzes and prioritizes recommendations
    
    **📋 Trip Planner** - Creates a beautiful day-by-day itinerary
    
    ---
    
    ### How to use:
    1. Enter your destination and trip duration
    2. Select your budget level and travel style
    3. Add any special requirements
    4. Click "Plan My Trip" and let our AI agents work their magic!
    
    Your personalized trip plan will be ready in **45 seconds to 2.5 minutes** depending on trip length! ⚡
    """)
    
    # Usage Statistics
    st.markdown("---")
    st.markdown("### 📊 Usage Stats")
    trips_hour, trips_day, trips_week, cost_week = get_usage_stats()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Trips (Hour)", f"{trips_hour}/{MAX_TRIPS_PER_HOUR}")
        st.metric("Trips (Day)", f"{trips_day}/{MAX_TRIPS_PER_DAY}")
    with col_b:
        st.metric("Trips (Week)", f"{trips_week}/{MAX_TRIPS_PER_WEEK}")
        remaining_budget = max(0, WEEKLY_COST_CAP_USD - cost_week)
        st.metric("Budget Left", f"${remaining_budget:.2f}")
    
    st.caption(f"Weekly cost: ${cost_week:.3f} / ${WEEKLY_COST_CAP_USD:.2f}")
    
    if trips_hour >= MAX_TRIPS_PER_HOUR * 0.8:
        st.warning("⚠️ Approaching hourly limit")
    if cost_week >= WEEKLY_COST_CAP_USD * 0.8:
        st.warning("⚠️ Approaching weekly cost cap")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Show form when not running and no output, OR when explicitly reset
    if not st.session_state.crew_running and st.session_state.output_file is None:
        st.header("⚙️ Trip Settings")
        
        with st.form("trip_form"):
            destination = st.text_input(
                "🌍 Destination",
                placeholder="e.g., Paris, France",
                help="Enter the city and country you want to visit"
            )
            
            duration = st.text_input(
                "📅 Duration",
                placeholder="e.g., 5 days",
                help="How long will your trip be?"
            )
            
            budget_level = st.select_slider(
                "💰 Budget Level",
                options=["Budget", "Mid-Range", "Luxury"],
                value="Mid-Range"
            )
            
            travel_style = st.multiselect(
                "🎨 Travel Style",
                ["Adventure", "Cultural", "Relaxation", "Food & Dining", "Shopping", "Nightlife"],
                default=["Cultural", "Food & Dining"]
            )
            
            special_requirements = st.text_area(
                "📝 Special Requirements",
                placeholder="e.g., vegetarian food, wheelchair accessible, family-friendly",
                help="Any specific needs or preferences?"
            )
            
            submitted = st.form_submit_button("🚀 Plan My Trip", use_container_width=True)
            
            if submitted:
                # Basic validation
                if not destination or not duration:
                    st.error("⚠️ Please fill in destination and duration!")
                elif not os.getenv("OPENAI_API_KEY") or not os.getenv("SERPER_API_KEY"):
                    st.error("⚠️ Please set OPENAI_API_KEY and SERPER_API_KEY in your .env file!")
                else:
                    # Security Check 1: Input Validation
                    validation_errors = validate_input(destination, duration, special_requirements)
                    if validation_errors:
                        for error in validation_errors:
                            st.error(f"🚫 {error}")
                    else:
                        # Security Check 2: Rate Limiting
                        rate_limit_ok, rate_limit_msg = check_rate_limit()
                        if not rate_limit_ok:
                            st.error(f"🚫 {rate_limit_msg}")
                            st.info("💡 Rate limits help us keep the service running smoothly for everyone!")
                        else:
                            # All checks passed - proceed with trip planning
                            # Record this trip for rate limiting
                            record_trip()
                            
                            # Store form data in session state
                            st.session_state.destination = destination
                            st.session_state.duration = duration
                            st.session_state.budget_level = budget_level
                            st.session_state.travel_style = travel_style
                            st.session_state.special_requirements = special_requirements
                            st.session_state.crew_running = True
                            st.session_state.scroll_to_progress = True
                            st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        ### 💡 Tips
        - Be specific with your destination
        - Include country name for clarity
        - Specify duration (e.g., "3 days", "1 week")
        - Add special requirements for personalized plans
        """)

with col2:
    if st.session_state.crew_running:
        st.header("🤖 Planning Your Trip...")
        st.markdown("Our AI agents are working on your itinerary...")
        
        # Auto-scroll to this section on mobile when planning starts
        if st.session_state.get('scroll_to_progress', False):
            st.markdown("""
            <script>
                // Scroll to progress section on mobile
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: true}, '*');
                setTimeout(function() {
                    window.scrollTo({top: 0, behavior: 'smooth'});
                    const mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                    if (mainContent && window.innerWidth <= 768) {
                        mainContent.scrollTop = mainContent.scrollHeight / 2;
                    }
                }, 100);
            </script>
            """, unsafe_allow_html=True)
            st.session_state.scroll_to_progress = False
        
        # Progress bar and status in the right column
        progress_bar = st.progress(0)
        status_text = st.empty()
        time_remaining = st.empty()
        
        st.markdown("---")
        
        # Agent status placeholders (stacked vertically in right column)
        agent1_status = st.empty()
        agent2_status = st.empty()
        agent3_status = st.empty()
    else:
        # Show static agent info when not running
        st.header("🤖 AI Agents")
        
        st.markdown("""
        <div class="agent-card">
            <h4>🔍 Trip Researcher</h4>
            <p style="color: #666; font-size: 0.9rem;">Researching destinations, attractions, and travel info</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h4>⭐ Trip Reviewer</h4>
            <p style="color: #666; font-size: 0.9rem;">Analyzing and prioritizing recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h4>📋 Trip Planner</h4>
            <p style="color: #666; font-size: 0.9rem;">Creating your beautiful HTML itinerary</p>
        </div>
        """, unsafe_allow_html=True)

# Execution Section (below the main columns)
if st.session_state.crew_running:
    
    try:
        # Estimate total time based on trip duration
        import time
        import re
        start_time = time.time()
        # Get data from session state
        destination = st.session_state.get('destination', '')
        duration = st.session_state.get('duration', '')
        budget_level = st.session_state.get('budget_level', 'Mid-Range')
        travel_style = st.session_state.get('travel_style', [])
        special_requirements = st.session_state.get('special_requirements', '')
        
        # Calculate estimated time based on trip duration
        def estimate_time(duration_str):
            """Estimate processing time based on trip duration"""
            # Extract number from duration string
            numbers = re.findall(r'\d+', duration_str)
            if numbers:
                days = int(numbers[0])
                # Convert weeks to days if needed
                if 'week' in duration_str.lower():
                    days = days * 7
                
                # Base time: 60 seconds for 1-2 days
                # Add 20 seconds per additional day
                if days <= 2:
                    min_time, max_time = 45, 75
                elif days <= 4:
                    min_time, max_time = 60, 90
                elif days <= 7:
                    min_time, max_time = 90, 120
                else:  # 8+ days
                    min_time, max_time = 120, 150
                
                return min_time, max_time
            return 60, 90  # Default
        
        min_est, max_est = estimate_time(duration)
        est_display = f"{min_est}-{max_est} sec" if max_est < 120 else f"{min_est//60}-{max_est//60} min"
        
        # Prepare inputs
        inputs = {
            'destination': destination,
            'duration': duration,
            'current_year': str(datetime.now().year)
        }
        
        # Add preferences to inputs if provided
        if special_requirements:
            inputs['special_requirements'] = special_requirements
        
        # Show initial status
        status_text.info("🚀 **Initializing AI agents...**")
        progress_bar.progress(5)
        time_remaining.info(f"⏱️ **Estimated time:** {est_display}")
        
        # Agent 1: Trip Researcher
        agent1_status.markdown("""
        <div style="background: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #856404; font-size: 1.1rem;">🔍 Trip Researcher</h4>
            <p style="margin: 5px 0 0 0; color: #856404; font-size: 0.9rem;">⏳ Working...</p>
        </div>
        """, unsafe_allow_html=True)
        agent2_status.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #dee2e6; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #6c757d; font-size: 1.1rem;">⭐ Trip Reviewer</h4>
            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 0.9rem;">⏸️ Waiting...</p>
        </div>
        """, unsafe_allow_html=True)
        agent3_status.markdown("""
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #dee2e6; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #6c757d; font-size: 1.1rem;">📋 Trip Planner</h4>
            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 0.9rem;">⏸️ Waiting...</p>
        </div>
        """, unsafe_allow_html=True)
        
        status_text.info("🔍 **Step 1/3:** Trip Researcher is searching for information...")
        progress_bar.progress(15)
        
        # Phase 1: Research
        phase_est = f"{min_est//3}-{max_est//3}s" if max_est < 120 else f"{min_est//180}-{max_est//180} min"
        time_remaining.warning(f"⏱️ **Phase 1/3 - Research** | Est. {phase_est} per phase")
        
        # Simulate research phase (this will be replaced by actual crew execution)
        time.sleep(1)
        progress_bar.progress(35)
        
        # Agent 1 complete, Agent 2 starts
        agent1_status.markdown("""
        <div style="background: #d4edda; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #155724; font-size: 1.1rem;">🔍 Trip Researcher</h4>
            <p style="margin: 5px 0 0 0; color: #155724; font-size: 0.9rem;">✅ Complete</p>
        </div>
        """, unsafe_allow_html=True)
        agent2_status.markdown("""
        <div style="background: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #856404; font-size: 1.1rem;">⭐ Trip Reviewer</h4>
            <p style="margin: 5px 0 0 0; color: #856404; font-size: 0.9rem;">⏳ Working...</p>
        </div>
        """, unsafe_allow_html=True)
        
        status_text.info("⭐ **Step 2/3:** Trip Reviewer is analyzing recommendations...")
        progress_bar.progress(55)
        
        # Phase 2: Review - Update time before crew execution
        time_remaining.warning(f"⏱️ **Phase 2/3 - Review** | Est. total: {est_display}")
        
        # Execute the crew (this is where the actual work happens)
        # Note: During crew execution, the display won't update until it completes
        with st.spinner(""):
            result = TripPlanner().crew().kickoff(inputs=inputs)
        
        # Agent 2 complete, Agent 3 starts
        agent2_status.markdown("""
        <div style="background: #d4edda; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #155724; font-size: 1.1rem;">⭐ Trip Reviewer</h4>
            <p style="margin: 5px 0 0 0; color: #155724; font-size: 0.9rem;">✅ Complete</p>
        </div>
        """, unsafe_allow_html=True)
        agent3_status.markdown("""
        <div style="background: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #856404; font-size: 1.1rem;">📋 Trip Planner</h4>
            <p style="margin: 5px 0 0 0; color: #856404; font-size: 0.9rem;">⏳ Working...</p>
        </div>
        """, unsafe_allow_html=True)
        
        status_text.info("📋 **Step 3/3:** Trip Planner is creating your HTML itinerary...")
        progress_bar.progress(85)
        
        # Phase 3: Planning - Show updated elapsed time
        time_remaining.warning(f"⏱️ **Phase 3/3 - Planning** | Finalizing your itinerary...")
        
        time.sleep(0.5)
        
        # All agents complete
        agent3_status.markdown("""
        <div style="background: #d4edda; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; margin-bottom: 10px;">
            <h4 style="margin: 0; color: #155724; font-size: 1.1rem;">📋 Trip Planner</h4>
            <p style="margin: 5px 0 0 0; color: #155724; font-size: 0.9rem;">✅ Complete</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar.progress(90)
        
        # Calculate actual time taken
        actual_time = int(time.time() - start_time)
        mins, secs = divmod(actual_time, 60)
        
        status_text.success("✅ Trip plan generated successfully!")
        time_remaining.success(f"✨ **Total time:** {mins}m {secs}s")
        
        # Find the output file
        output_dir = Path(__file__).parent / "output"
        output_file = output_dir / "trip_plan.html"
        
        if output_file.exists():
            st.session_state.output_file = str(output_file)
            progress_bar.progress(100)
        else:
            st.error("❌ Could not find the output file. Please try again.")
            
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)
        
    finally:
        st.session_state.crew_running = False

# Display Results Section (separate from execution)
if st.session_state.output_file is not None and not st.session_state.crew_running:
    output_file = Path(st.session_state.output_file)
    
    if output_file.exists():
        # Success message
        st.success("🎉 **Your trip plan is ready!**")
        
        # Display result
        st.divider()
        st.header("📄 Your Trip Plan")
        
        # Read HTML content
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Download button
        # Get destination from session state for filename
        dest_name = st.session_state.get('destination', 'trip').replace(',', '').replace(' ', '_')
        st.download_button(
            label="📥 Download Trip Plan",
            data=html_content,
            file_name=f"{dest_name}_trip_plan.html",
            mime="text/html",
            use_container_width=True,
            help="Download as HTML - Open in browser and print to PDF"
        )
        
        # Tip for PDF export
        st.markdown("""
        <div style="background: #e7f3ff; padding: 15px; border-radius: 10px; border-left: 4px solid #0066cc; margin: 10px 0;">
            <strong>💡 Tip:</strong> To get a PDF version, download the HTML file, open it in your browser, 
            and use "Print to PDF" (Ctrl+P or Cmd+P).
        </div>
        """, unsafe_allow_html=True)
        
        # Display the HTML content
        st.markdown("---")
        st.subheader("📋 Preview")
        
        # Add mobile-responsive wrapper to HTML content
        mobile_responsive_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    margin: 0;
                    padding: 10px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    overflow-x: hidden;
                }}
                * {{
                    max-width: 100%;
                    box-sizing: border-box;
                }}
                table {{
                    width: 100% !important;
                    display: block;
                    overflow-x: auto;
                    -webkit-overflow-scrolling: touch;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }}
                p, li, div {{
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }}
                @media (max-width: 768px) {{
                    body {{
                        font-size: 14px;
                        padding: 5px;
                    }}
                    h1 {{
                        font-size: 1.5rem !important;
                    }}
                    h2 {{
                        font-size: 1.3rem !important;
                    }}
                    h3 {{
                        font-size: 1.1rem !important;
                    }}
                    table {{
                        font-size: 12px;
                    }}
                    /* Make schedule items stack better on mobile */
                    .schedule-item, .activity {{
                        display: block !important;
                        margin-bottom: 10px !important;
                    }}
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Display HTML in an iframe-like component
        st.components.v1.html(mobile_responsive_html, height=800, scrolling=True)
        
        # Reset button after preview
        st.markdown("---")
        if st.button("🔄 Plan Another Trip", use_container_width=True, type="primary"):
            # Clear all session state related to the trip
            st.session_state.output_file = None
            st.session_state.crew_running = False
            if 'destination' in st.session_state:
                del st.session_state.destination
            if 'duration' in st.session_state:
                del st.session_state.duration
            if 'budget_level' in st.session_state:
                del st.session_state.budget_level
            if 'travel_style' in st.session_state:
                del st.session_state.travel_style
            if 'special_requirements' in st.session_state:
                del st.session_state.special_requirements
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <div class="footer-content">
        <h3>About</h3>
        <p>AI Trip Planner uses advanced AI agents powered by CrewAI to research, review, and plan your perfect trip.</p>
        <p style="margin-top: 1rem;">© 2024 AI Trip Planner. Built with ❤️ using Streamlit and CrewAI.</p>
    </div>
</div>
""", unsafe_allow_html=True)

