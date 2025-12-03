"""
Trip Planner CrewAI Crew Configuration — Updated with Zora Digital Palette + Realistic Pricing Rules
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

        # -----------------------------------------
        # AGENTS
        # -----------------------------------------

        researcher = Agent(
            role="Expert Travel Researcher",
            goal=(
                "Deliver detailed, accurate, and up-to-date travel research for global destinations, "
                "including pricing, logistics, attractions, cultural insights, and practical tips."
            ),
            backstory=(
                "You are a world-class travel researcher with a deep understanding of global destinations. "
                "Your insights are realistic, verified, structured, and grounded in real-world pricing standards."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Meticulous Travel Reviewer",
            goal=(
                "Ensure all research is accurate, structured, realistic, aligned with pricing rules, "
                "and formatted cleanly for itinerary planning."
            ),
            backstory=(
                "You are a detail-oriented travel specialist who verifies facts, corrects errors, "
                "enforces pricing rules, ensures consistency, and prepares research for planning."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Creative and Practical Trip Planner",
            goal=(
                "Transform verified research into a polished, detailed, HTML-formatted itinerary "
                "that reflects user preferences and uses the Zora Digital brand palette consistently."
            ),
            backstory=(
                "You are a travel itinerary architect with strong design instincts. You deliver structured, "
                "engaging itineraries with consistent styling and realistic pricing."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        # -----------------------------------------
        # TASKS — Research
        # -----------------------------------------

        research_task = Task(
            description="""
Research the destination: {destination}
Duration: {duration} days
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

Collect detailed travel intelligence:

- Estimated daily + total costs (accommodation, food, transportation)
- Top attractions and unique activities
- Best neighborhoods to stay in
- Local transportation options
- Cultural insights, etiquette, customs
- Seasonal/weather considerations
- Safety and visa notes
- Budget breakdown with ranges
- Source links

=========================================
MANDATORY ACCOMMODATION PRICING RULES
=========================================

You MUST follow these minimum nightly ranges for moderate budgets:

1. Moderate Budget Definition:
   - Clean 2–3 star hotels OR private apartments
   - Safe, central or semi-central areas
   - Private rooms (NO hostels)

2. Minimum Nightly Price Ranges:
   - Paris, London, Zurich, Geneva, NYC, Tokyo → $150–$220/night
   - Barcelona, Rome, Amsterdam, Lisbon, Copenhagen → $120–$180/night
   - Prague, Budapest, Valencia, Porto → $80–$140/night

3. For unspecified destinations:
   - Infer from comparable cities.

4. Accommodation MUST be given as a RANGE:
   Example: “10 nights in Paris: $1,600–$2,200.”

5. If user budget does not match real pricing:
   Add note: “This reflects realistic market pricing for this destination.”

Output: A clean, structured research report.
""",
            agent=researcher,
            expected_output="Structured research report with accurate pricing and details."
        )

        # -----------------------------------------
        # TASKS — Review
        # -----------------------------------------

        review_task = Task(
            description="""
Review the research findings for: {destination}

You MUST:

- Confirm all sections are complete and accurate.
- Verify accommodation pricing follows the mandatory nightly ranges.
- Correct any unrealistic or outdated info.
- Ensure costs are expressed as realistic ranges.
- Improve clarity, structure, and flow.
- Ensure the report is ready for itinerary planning.

Output: Refined, corrected, validated research report.
""",
            agent=reviewer,
            expected_output="Clean, validated research report ready for planning."
        )

        # -----------------------------------------
        # TASKS — Planning
        # -----------------------------------------

        planning_task = Task(
            description="""
Create a detailed {duration}-day itinerary for {destination}
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

The itinerary MUST include:

- Morning, afternoon, evening activities for each day
- Restaurants, attractions, accommodations
- Transportation details
- Estimated daily costs
- Final budget summary

=========================================
ZORA DIGITAL BRAND COLOR PALETTE — REQUIRED
=========================================

Every HTML output MUST include this exact <style> block in the <head>:

<style>
  body {
    font-family: Arial, Helvetica, sans-serif;
    color: #3D3D3D;
  }
  h1 {
    color: #0F0F0F;
  }
  h2 {
    color: #1C1C1C;
  }
  p, li {
    color: #3D3D3D;
    line-height: 1.6;
  }
  a {
    color: #2C7EF4;
    text-decoration: none;
  }
</style>

You MUST NOT override these colors anywhere else.
All headings and text MUST use these colors exactly.

=========================================
HTML OUTPUT FORMAT — REQUIRED
=========================================

You MUST output a complete HTML document containing:

<html>
<head>…</head>
<body>
<h1>{duration}-Day {travel_style}-Friendly Itinerary in {destination}</h1>

<h2>Day 1: [Title]</h2>
<p><strong>Morning:</strong> …</p>
<p><strong>Afternoon:</strong> …</p>
<p><strong>Evening:</strong> …</p>
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

=========================================
MANDATORY BUDGET RULES
=========================================

- You MUST adhere to the accommodation pricing rules.
- You MUST present accommodation as a RANGE.
- Avoid unrealistic, lowball pricing.
- Total budgets MUST incorporate corrected accommodation ranges.

Output: A complete HTML itinerary with inline CSS using the Zora Digital palette.
""",
            agent=planner,
            expected_output="Complete HTML itinerary with consistent Zora Digital colors."
        )

        # -----------------------------------------
        # CREW SEQUENCE
        # -----------------------------------------

        crew = Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",
            verbose=True,
        )

        return crew
