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
            role="Trip Researcher",
            goal="Research destinations, local costs, attractions, and travel information",
            backstory="""You are an expert travel researcher with extensive knowledge of 
            destinations worldwide. You gather comprehensive information about locations, 
            including costs, attractions, local customs, and practical travel details.""",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )
        
        reviewer = Agent(
            role="Trip Reviewer",
            goal="Review and refine research findings, ensuring accuracy and completeness",
            backstory="""You are a meticulous travel reviewer who ensures all research 
            is accurate, complete, and well-organized. You review findings and prepare 
            them for the planning phase.""",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )
        
        planner = Agent(
            role="Trip Planner",
            goal="Create a comprehensive, detailed trip itinerary based on research",
            backstory="""You are an expert travel planner who creates detailed, 
            day-by-day itineraries. You combine research findings with user preferences 
            to create personalized travel plans that are practical and enjoyable.""",
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
            - Local costs (accommodation, food, transportation)
            - Top attractions and activities
            - Best areas to stay
            - Transportation options
            - Local customs and tips
            - Budget breakdown
            
            Provide detailed research findings including a budget overview.""",
            agent=researcher,
            expected_output="Comprehensive research report with destination information and budget overview"
        )
        
        review_task = Task(
            description="""Review and refine the research findings for: {destination}
            Ensure all information is accurate, complete, and well-organized.
            Verify budget estimates and highlight key attractions.""",
            agent=reviewer,
            expected_output="Reviewed and refined research report"
        )
        
        planning_task = Task(
            description="""Create a detailed {duration}-day itinerary for {destination}
            Budget: {budget}
            Travel Style: {travel_style}
            Special Requirements: {special_requirements}
            
            Based on the research findings, create a comprehensive day-by-day itinerary 
            that includes:
            - Daily schedule with activities
            - Recommended accommodations
            - Restaurant suggestions
            - Transportation details
            - Budget breakdown
            - Tips and recommendations
            
            Format the output as a well-structured HTML document.""",
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

