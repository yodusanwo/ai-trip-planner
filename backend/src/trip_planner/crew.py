"""
Trip Planner CrewAI Crew Configuration — Updated with Realistic Accommodation Pricing Rules
"""
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool


class TripPlanner:
    """CrewAI crew for planning trips"""
    
    def __init__(self):
        self._crew = None
    
    def crew(self) -> Crew:
        if self._crew is None:
            self._crew = self._create_crew()
        return self._crew
    
    def _create_crew(self) -> Crew:
        search_tool = SerperDevTool()

        # ----------------------------
        # AGENTS
        # ----------------------------

        researcher = Agent(
            role="Expert Travel Researcher",
            goal=(
                "Deliver detailed and up-to-date travel research for global destinations, "
                "covering budget estimates, key attractions, logistics, local culture, and practical tips."
            ),
            backstory=(
                "You are a world-class travel researcher with deep knowledge of international destinations. "
                "You specialize in accurate, current, and comprehensive travel intelligence. "
                "Your outputs are structured, realistic, and designed for seamless handoff."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Meticulous Travel Reviewer",
            goal=(
                "Ensure research findings are accurate, complete, logically structured, "
                "and optimized for use in itinerary planning."
            ),
            backstory=(
                "You are a detail-focused travel specialist. You verify accuracy, correct inconsistencies, "
                "ensure realism—especially around budgets—and guarantee the final research is reliable and user-ready."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Creative and Practical Trip Planner",
            goal=(
                "Craft personalized, engaging, and highly detailed trip itineraries using verified research "
                "and the traveler's preferences."
            ),
            backstory=(
                "You are an expert itinerary designer. You blend creativity with logistics to produce balanced, "
                "budget-aware, style-matched travel experiences. Every plan reflects the traveler’s preferences "
                "and adheres strictly to realistic market pricing."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )


        # ----------------------------
        # TASKS
        # ----------------------------

        research_task = Task(
            description="""
Research the destination: {destination}
Duration: {duration} days
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

Gather comprehensive information about:
- Estimated daily and total costs (accommodation, food, transportation)
- Top attractions and activities
- Best neighborhoods to stay in
- Local transportation options
- Cultural customs and tips
- Safety, visas, and seasonal info
- Budget breakdown

==============================
MANDATORY ACCOMMODATION PRICING RULES
==============================

You MUST follow these city-specific pricing rules:

1. Always use realistic, market-based accommodation pricing.
2. For *moderate budget* (default unless otherwise specified):
   - Assume clean 2–3 star hotels OR private apartments.
   - Central or semi-central safe neighborhoods.
   - NEVER hostel/shared rooms for moderate budget.
3. Minimum nightly ranges (DO NOT go below these):
   - Paris, London, Zurich, Geneva, NYC, Tokyo → $150–$220/night
   - Barcelona, Rome, Amsterdam, Lisbon, Copenhagen → $120–$180/night
   - Prague, Budapest, Valencia, Porto → $80–$140/night
4. If destination is not listed, infer pricing from comparable cities.
5. Always present accommodation costs as a *range* (e.g., $1,600–$2,200 for 10 nights).
6. If user budget conflicts with real-world pricing:
   Add: “This reflects realistic market prices for a moderate budget in this city.”

==============================

Output: 
A clear, bullet-pointed research report with budget ranges and source links.
""",
            agent=researcher,
            expected_output="Structured research report with accurate pricing and complete details."
        )

        review_task = Task(
            description="""
Review and refine all research findings for: {destination}

Requirements:
- Confirm completeness across all sections.
- Verify accommodation pricing follows the required minimum nightly ranges.
- Correct any unrealistic or unusually low estimates.
- Ensure information is accurate, updated, and logically organized.
- Highlight standout attractions and clarify all budget sections.

Output:
Validated and improved research report, ready for itinerary planning.
""",
            agent=reviewer,
            expected_output="Reviewed, corrected, and optimized research report."
        )

        planning_task = Task(
            description="""
Create a detailed {duration}-day itinerary for {destination}
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

Based on verified research, produce a complete day-by-day itinerary including:
- Detailed morning, afternoon, evening activities
- Accommodation, restaurant, and attraction recommendations
- Transportation and logistics guidance
- Estimated daily costs + total budget summary
- Cultural insights and practical tips

==============================
CRITICAL REQUIREMENTS
==============================

1. Travel Style Integration
Every element MUST reflect the travel style ({travel_style}):
- Activity types
- Accommodation category
- Pacing
- Meal choices
- Transportation mode

2. HTML Output Format
You MUST output a complete HTML document using:
<html>, <head>, <body>, <h1>, <h2>, <p>, <ul>, <li>, etc.
Include clean inline CSS styling.

3. Required Structure (Do NOT modify)
<h1>{duration}-Day {travel_style}-Friendly Itinerary in {destination}</h1>

<h2>Day 1: [Title]</h2>
<p><strong>Morning:</strong> ...</p>
<p><strong>Afternoon:</strong> ...</p>
<p><strong>Evening:</strong> ...</p>
<p><strong>Estimated Costs:</strong></p>
<ul>
  <li>Transportation: $X</li>
  <li>Food: $X</li>
  <li>Activities: $X</li>
  <li><strong>Total: $X</strong></li>
</ul>

[Repeat for each day]

<h2>Total Estimated Budget Summary</h2>
<ul>
  <li>Accommodation ({duration} nights): $X–$Y</li>
  <li>Total Food & Drink: $X</li>
  <li>Total Attractions: $X</li>
  <li>Total Transportation: $X</li>
  <li><strong>Grand Total: ~$X–$Y</strong></li>
</ul>

==============================
MANDATORY BUDGET RULES (NEW)
==============================

- You MUST follow the accommodation pricing rules defined in the research phase.
- NEVER estimate nightly rates below realistic market minimums.
- ALWAYS express accommodation as a range (e.g., $1,600–$2,200 for Paris, 10 nights).
- All total budget numbers MUST reflect these corrected accommodation costs.

==============================

Output must be a complete HTML document with inline CSS.
""",
            agent=planner,
            expected_output="Complete HTML-formatted itinerary with realistic budget ranges."
        )


        # ----------------------------
        # CREW SEQUENCE
        # ----------------------------

        crew = Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",
            verbose=True,
        )

        return crew
