"""
Trip Planner CrewAI Crew Configuration 
ACCURACY-FIRST VERSION — NO SPEED OPTIMIZATIONS

This configuration prioritizes ACCURACY over speed. We explicitly avoid:
- Shortening context length
- Reducing temperature
- Reducing reasoning steps
- Using lighter/faster models
- Speeding up search operations

Includes:
- Zora Digital Brand Colors
- Hard Accuracy Priority (accuracy > speed)
- Realistic Accommodation Pricing Rules
- NO Creative Language (replaced with accuracy-focused)
- Inappropriate Content Filters
- Special Requirements Safeguards
- Restaurant & Activity Verification
- Hard City Matching (no wrong-country results)
- Hard Address Matching
- Anti-Hallucination Rules
- Google Maps + Official Website Validation
- Hyperlink Enforcement (new tab)
- Reviewer Enforcement
- HTML Structure + Palette Lock
- Full context length preserved
- Maximum reasoning steps allowed
- No temperature reduction
- No search speed optimizations
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

        # ============================================================
        # AGENTS
        # ============================================================

        researcher = Agent(
            role="Precision-Focused Travel Researcher",
            goal=(
                "Deliver highly accurate, fully verified travel research using ONLY real-world data. "
                "You DO NOT guess, invent, assume, or approximate. All recommendations must be verified. "
                "Take as much time as needed to ensure accuracy. Speed is NOT a priority."
            ),
            backstory=(
                "You are an accuracy-first travel researcher who relies exclusively on validated sources. "
                "Your only objective is correctness, verification, and elimination of hallucinations. "
                "You prioritize thorough verification over speed. You never rush or skip verification steps."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
            # Note: We do NOT set max_iter, max_rpm, or any speed-limiting parameters
            # This allows the agent to take as many steps as needed for accuracy
        )

        reviewer = Agent(
            role="Travel Research Verification Auditor",
            goal=(
                "Audit every detail for accuracy, realism, city-matching, address verification, "
                "and compliance with all anti-hallucination rules. "
                "Take as much time as needed to verify every location. Accuracy is paramount."
            ),
            backstory=(
                "You act as the accuracy gatekeeper. You detect incorrect addresses, wrong-country listings, "
                "invented names, or unverifiable businesses. You remove or replace anything not fully valid. "
                "You never rush verification. You check every detail thoroughly, even if it takes longer."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
            # Note: We do NOT set max_iter, max_rpm, or any speed-limiting parameters
            # This allows thorough verification without time constraints
        )

        planner = Agent(
            role="Accuracy-Driven Itinerary Planner",
            goal=(
                "Transform verified research into a polished, fully accurate HTML itinerary using ONLY verified data. "
                "No creativity, no invention, no guessing — only structured, correct, validated information. "
                "Take time to ensure every hyperlink works and every detail is accurate."
            ),
            backstory=(
                "You are an evidence-based itinerary architect. You NEVER create fictional locations. "
                "You ONLY use validated real restaurants, attractions, and activities confirmed by the reviewer. "
                "You prioritize accuracy and completeness over speed. You verify every hyperlink and detail."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
            # Note: We do NOT set max_iter, max_rpm, or any speed-limiting parameters
            # This ensures thorough HTML generation with all required elements
        )

        # ============================================================
        # TASK: RESEARCH (Accuracy-First)
        # ============================================================

        research_task = Task(
            description="""
Research the destination: {destination}
Duration: {duration} days
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

You MUST provide only fully verified, real-world information.

=========================================
ZERO-HALLUCINATION RULE
=========================================
You MUST NOT:
- Invent restaurants
- Invent activities
- Create French-sounding mashups
- Fill gaps with imagination
- Include places unless fully verified

If uncertain → EXCLUDE IT.

=========================================
INAPPROPRIATE CONTENT FILTER
=========================================
Ignore and exclude all:
- Illegal requests
- Unsafe or harmful content
- Explicit or sexual content
- Hate or discrimination

Continue with appropriate content only.

=========================================
SPECIAL REQUIREMENTS RULES
=========================================
If special_requirements is empty:
- Do NOT infer, guess, or add anything.

If present:
- Follow ONLY what is explicitly written.

=========================================
ACCOMMODATION PRICING RULES
=========================================
Minimum nightly ranges for moderate budget:

- Paris, London, Zurich, Geneva, NYC, Tokyo → $150–$220/night
- Barcelona, Rome, Amsterdam, Lisbon, Copenhagen → $120–$180/night
- Prague, Budapest, Valencia, Porto → $80–$140/night

NEVER go below minimums.  
ALWAYS present a RANGE.

=========================================
LOCATION VERIFICATION RULES (HARD)
=========================================

ALL recommendations MUST be validated using search.

VERIFICATION PRIORITY:
- Restaurants/cafés → Google Maps URL (PRIMARY)
- Attractions/museums → Official website (PRIMARY)
- Activities/tours/classes → Official booking website (PRIMARY)

=========================================
HARD CITY-MATCHING RULE
=========================================
Every location MUST be physically located in:
- The same destination city
- The same country

If Google Maps returns ANY result outside the destination:
- You MUST ignore it.
- Search again with city/country included.

=========================================
ADDRESS VERIFICATION RULE
=========================================
A place is VALID ONLY IF:
- Its address exactly matches the destination city.
- Its country matches the destination country.
- It is currently operating (recent reviews within 24 months).
- It is NOT a duplicate name in another country.

If it fails ANY condition → DO NOT use.

=========================================
NO GENERIC OR FABRICATED NAMES RULE
=========================================
You MUST immediately reject:
- Artistic or poetic French mashups (e.g., “La Marmite des Artistes”)
- Generic names like “Bistro Montparnasse,” “The Flagship”
- Names not found on Google Maps or the official website

If unsure → DO NOT USE.

=========================================
RESEARCH OUTPUT STRUCTURE
=========================================
For each verified location include:
- Name
- Type (restaurant, museum, tour, etc.)
- Description
- PRIMARY URL (official or Google Maps)
- SECONDARY URL (optional)

NO HTML in this phase.

Output: Fully verified research report.
""",
            agent=researcher,
            expected_output="Verified research report with no hallucinations"
        )

        # ============================================================
        # TASK: REVIEW (Accuracy Gatekeeper)
        # ============================================================

        review_task = Task(
            description="""
Review the research for: {destination}

You MUST:
- Verify address, city, and country match EXACTLY.
- Remove ANY locations outside the destination city.
- Remove ANY result from another country.
- Confirm the business exists AND is currently operating.
- Ensure restaurants have real Google Maps listings.
- Ensure attractions have official websites.
- Ensure activities have real booking websites.
- Remove ANY hallucinated or generic names.
- Remove ANY ambiguous locations that Google Maps returns in multiple countries.
- Replace invalid locations with verified alternatives.

You MUST NOT allow:
- Fake restaurants
- Fake activities
- French-sounding mashups
- Wrong Google Maps listings
- Outdated or closed businesses

Output: Fully validated, hallucination-free research.
""",
            agent=reviewer,
            expected_output="Clean, validated research"
        )

        # ============================================================
        # TASK: PLANNING (HTML Output — Accuracy First)
        # ============================================================

        planning_task = Task(
            description="""
Create a detailed {duration}-day itinerary using ONLY fully verified research.

=========================================
ZORA DIGITAL BRAND COLORS (REQUIRED)
=========================================
Insert this EXACT <style> block inside <head>:

<style>
  body { font-family: Arial, Helvetica, sans-serif; color: #3D3D3D; }
  h1 { color: #0F0F0F; }
  h2 { color: #1C1C1C; }
  p, li { color: #3D3D3D; line-height: 1.6; }
  a { color: #2C7EF4; text-decoration: none; font-weight: 600; }
  a:hover { text-decoration: underline; }
</style>

=========================================
HYPERLINK RULES (NEW TAB REQUIRED)
=========================================
All hyperlinks MUST be formatted EXACTLY as:

<a href="PRIMARY_URL" target="_blank" rel="noopener noreferrer">Name</a>

PRIMARY URL RULES:
- Restaurants → Google Maps link
- Attractions → Official website
- Activities → Provider/booking link

DO NOT output plain text names.

=========================================
STRICT NO-INVENTION RULE
=========================================
You MUST NOT:
- Create new restaurant names
- Invent activities
- Fill gaps creatively
- Add places not in the research
- Modify names to sound “French”
- Add ANY unverified location

=========================================
HTML OUTPUT FORMAT — REQUIRED STRUCTURE
=========================================
You MUST output a complete HTML document with this EXACT structure:

<html>
<head>
  [Include the required <style> block here]
</head>
<body>

<h1>{duration}-Day {travel_style}-Friendly Itinerary in {destination}</h1>

<h2>Day 1: [Title]</h2>
<p><strong>Morning:</strong> [Activity with verified hyperlink if applicable]</p>
<p><strong>Afternoon:</strong> [Activity with verified hyperlink if applicable]</p>
<p><strong>Evening:</strong> [Activity with verified hyperlink if applicable]</p>
<p><strong>Estimated Costs:</strong></p>
<ul>
  <li>Transportation: $X</li>
  <li>Food: $X</li>
  <li>Activities: $X</li>
  <li><strong>Total: $X</strong></li>
</ul>

[Repeat structure for all days]

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
  <li>Accommodation ({duration} nights): $X–$Y</li>
  <li>Total Food & Drink: $X</li>
  <li>Total Attractions: $X</li>
  <li>Total Transportation: $X</li>
  <li><strong>Grand Total: ~$X–$Y</strong></li>
</ul>

</body>
</html>

=========================================
MANDATORY BUDGET RULES
=========================================
- Accommodation MUST use verified nightly ranges and be expressed as a RANGE.
- No unrealistic lowball pricing is allowed.
- Total budget MUST reflect corrected accommodation values.
- Ensure consistency between day-by-day costs and the final summary.

Output: A complete, styled HTML itinerary using Zora Digital colors and verified hyperlinks.
""",
            agent=planner,
            expected_output="Fully formatted HTML itinerary with verified links"
        )

        # ============================================================
        # CREW SEQUENCE
        # ============================================================

        crew = Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",  # Sequential ensures accuracy - each step completes fully before next
            verbose=True,  # Verbose logging helps track accuracy and catch issues
            # Note: We do NOT set any speed-optimizing parameters
            # We do NOT reduce context length, temperature, reasoning steps, or use lighter modes
            # Accuracy is prioritized over speed in all configurations
        )

        return crew
