import streamlit as st
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the TripPlanner crew
from src.trip_planner.crew import TripPlanner

# Page configuration
st.set_page_config(
    page_title="AI Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
</style>
""", unsafe_allow_html=True)

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
                if not destination or not duration:
                    st.error("⚠️ Please fill in destination and duration!")
                elif not os.getenv("OPENAI_API_KEY") or not os.getenv("SERPER_API_KEY"):
                    st.error("⚠️ Please set OPENAI_API_KEY and SERPER_API_KEY in your .env file!")
                else:
                    # Store form data in session state
                    st.session_state.destination = destination
                    st.session_state.duration = duration
                    st.session_state.budget_level = budget_level
                    st.session_state.travel_style = travel_style
                    st.session_state.special_requirements = special_requirements
                    st.session_state.crew_running = True
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
        
        # Display HTML in an iframe-like component
        st.components.v1.html(html_content, height=800, scrolling=True)
        
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

