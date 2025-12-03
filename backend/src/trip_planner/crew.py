"""
Trip Planner CrewAI Crew Configuration
"""
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool


class TripPlanner:
    """CrewAI crew for planning trips"""
    
    def __init__(self):
        """Initialize the TripPlanner crew"""
        self._crew = None
    
    def crew(self) -> Crew:
        """Create and return the CrewAI crew"""
        if self._crew is None:
            self._crew = self._create_crew()
        return self._crew
    
    def _create_crew(self) -> Crew:
        """Create the CrewAI crew with agents and tasks"""
        
        # Initialize tools
        search_tool = SerperDevTool()
        
        # Create agents
        researcher = Agent(
            role="Expert Travel Researcher",
            goal="Deliver detailed and up-to-date travel research for global destinations,"
                "covering budget estimates, key attractions, logistics, local culture, and practical tips.",
            backstory="""You are a world-class travel researcher with deep knowledge of international destinations.
                Your insights help travelers make informed decisions. You specialize in curating accurate,
                current, and comprehensive data from trusted sources. Your output is structured, reliable, and ready for review.""",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )
        
        reviewer = Agent(
            role="Meticulous Travel Reviewer",
            goal="Ensure the research findings are accurate, complete, logically structured,"
                "and formatted for easy consumption by the trip planner.",
            backstory="""You are a detail-oriented travel expert with a critical eye. Your role is to verify the accuracy,
                completeness, and usability of the researcher's findings. You cross-check facts, fix inconsistencies, 
                and optimize the structure of the report for clear planning handoff.""",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )
        
        planner = Agent(
            role="Creative and Practical Trip Planner",
            goal="Craft personalized, engaging, and highly detailed trip itineraries based on verified travel research "
                "and the traveler's preferences.",
            backstory="""You are an expert itinerary designer who transforms research into engaging, day-by-day travel plans.
                You integrate user preferences, logistical realities, and creative flair to produce well-balanced, 
                budget-aware, and delightful travel experiences.
                **You are highly skilled at adapting every element of the itinerary to match the traveler's preferred travel style.""",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )
        
        # Create tasks
        research_task = Task(
            description="""Research the destination: {destination}
            Duration: {duration} days
            Budget: {budget}
            Travel Style: {travel_style}
            Special Requirements: {special_requirements}
            
            Gather comprehensive information about:
            - Estimated daily and total costs (accommodation, food, transportation)
            - Top attractions and activities
            - Best areas to neighborhoods to stay in
            - Local Transportation options
            - Cultural customs and tips
            - Safety, visas, and seasonal info
            - Budget breakdown
            **Output:** A well-organized, bullet-pointed research report with budget breakdowns and source links
            Provide detailed research findings including a budget overview.""",
            agent=researcher,
            expected_output="Structured research report with all requested data and budget summary."
        )
        
        review_task = Task(
            description="""Review and refine the research findings for: {destination}
            Confirm completeness of all sections.
            Verify accuracy and remove outdated or misleading info.
            Ensure that report is logically organized and easy to read.
            Highlight standout attractions and clarify budget sections.""",
            agent=reviewer,
            expected_output="Validated and improved research report, optimized for planning handoff."
        )
        
        planning_task = Task(
            description="""Create a detailed {duration}-day itinerary for {destination}
            Budget: {budget}
            Travel Style: {travel_style}
            Special Requirements: {special_requirements}
            
            Based on the research findings, create a comprehensive day-by-day itinerary 
            that includes:
            - Daily activity plan (morning, afternoon, evening)
            - Recommended accommodations and restaurants
            - Transportation details (local travel, airport transfers, etc.)
            - Estimated daily costs and total budget summary
            - Practical tips and cultural insights
            **CRITICAL REQUIREMENTS:**
            
            1. **Travel Style Integration:** Every aspect of the trip MUST reflect the chosen **travel style** ({travel_style}). 
               This includes:
               - Type of activities (e.g., adventure activities for "Adventure", museums for "Cultural", beaches for "Relaxation")
               - Accommodation style (e.g., luxury resorts for "Luxury", hostels for "Budget-Friendly", family hotels for "Family-Friendly")
               - Pacing and schedule (e.g., relaxed for "Relaxation", packed for "Adventure")
               - Transportation mode (e.g., private transfers for "Luxury", public transport for "Budget-Friendly")
               - Dining options (e.g., fine dining for "Luxury", street food for "Food & Dining", family restaurants for "Family-Friendly")
            
            2. **HTML Output Format:** You MUST output a complete, valid HTML document. The HTML should contain the itinerary 
               structured as shown below. Use proper HTML tags (<html>, <head>, <body>, <h1>, <h2>, <p>, <ul>, <li>, etc.) 
               with inline CSS styling for visual appeal.
            
            3. **Required Structure:** Follow this exact structure within your HTML output:
            
            =============================
            
            <h1>{duration}-Day {travel_style}-Friendly Itinerary in {destination}</h1>
            
            <h2>Day 1: [Title of the Day]</h2>
            <p><strong>Morning:</strong> [Activity with specific details]</p>
            <p><strong>Afternoon:</strong> [Activity with specific details]</p>
            <p><strong>Evening:</strong> [Activity with specific details]</p>
            <p><strong>Estimated Costs:</strong></p>
            <ul>
                <li>Transportation: $X</li>
                <li>Food: $X</li>
                <li>Activities: $X</li>
                <li><strong>Total: $X</strong></li>
            </ul>
            
            <h2>Day 2: [Title of the Day]</h2>
            [Repeat structure for each day]
            
            <h2>Day {duration}: Departure</h2>
            <p><strong>Morning:</strong> [Departure summary]</p>
            <p><strong>Afternoon:</strong> [Any last activity or shopping]</p>
            <p><strong>Evening:</strong> [Transport to airport]</p>
            <p><strong>Estimated Costs:</strong></p>
            <ul>
                <li>Transportation: $X</li>
                <li>Food: $X</li>
                <li><strong>Total: $X</strong></li>
            </ul>
            
            <h2>Total Estimated Budget Summary</h2>
            <ul>
                <li>Accommodation ({duration} nights): $XXXX</li>
                <li>Total Food & Drink: $XXX</li>
                <li>Total Attractions: $XXX</li>
                <li>Total Transportation: $XX</li>
                <li><strong>Grand Total: ~$XXXX</strong></li>
            </ul>
            
            =============================
            
            **MANDATORY INSTRUCTIONS:**
            - Output the COMPLETE HTML code directly in your response. Do NOT write references like "The itinerary is provided in the HTML document above."
            - Keep all sections present and in the exact order shown.
            - Use HTML tags with inline CSS for styling (colors, fonts, spacing, etc.) to make it visually appealing.
            - Include specific restaurant names, activity names, and transportation details.
            - Use realistic and consistent pricing that matches the budget level ({budget}).
            - Ensure the travel style ({travel_style}) influences EVERY element: activities, accommodations, pacing, transportation, and dining.
            - Always end with the complete "Total Estimated Budget Summary" section in the exact format shown above.
            - Do NOT change the structure. Keep all headers (e.g., "Day 1:", "Estimated Costs") and formatting consistent.
""",
            agent=planner,
            expected_output="Complete HTML-formatted trip itinerary"
        )
        
        # Create crew with sequential process
        crew = Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",  # Tasks run one after another
            verbose=True,
        )
        
        return crew

