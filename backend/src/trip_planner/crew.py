"""
Trip Planner CrewAI Crew Configuration 
Updated with:
- Zora Digital Brand Colors
- Realistic Accommodation Pricing Rules
- Inappropriate Content Filters
- Special Requirements Safeguards
- Restaurant & Activity Verification (Google Maps + Official Sites)
- Hyperlink Enforcement (one clean link in final HTML)
- Reviewer Enforcement
- HTML Structure + Palette Lock
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
            role="Expert Travel Researcher",
            goal=(
                "Deliver accurate, realistic, and structured travel research including pricing, "
                "destination insights, attractions, logistics, and cultural notes."
            ),
            backstory=(
                "You are a world-class travel researcher with deep global knowledge. "
                "You produce reliable, well-structured information grounded in verified data. "
                "You do NOT hallucinate or infer missing details."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Meticulous Travel Reviewer",
            goal=(
                "Review all research for accuracy, realism, structure, safety, and compliance with rules. "
                "Correct all inconsistencies, enforce pricing rules, verify locations, and ensure clean formatting."
            ),
            backstory=(
                "You are a quality-control expert who ensures all research is clean, realistic, "
                "safe, non-harmful, and ready for itinerary planning. You remove inappropriate content, "
                "catch hallucinations, and enforce all constraints."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Creative and Practical Trip Planner",
            goal=(
                "Transform verified research into a beautifully formatted, consistent HTML itinerary "
                "that uses Zora Digital brand colors, realistic pricing, and verified locations."
            ),
            backstory=(
                "You design polished itineraries with structure, flair, realistic expectations, "
                "and strict visual consistency. You never override the brand palette and never use "
                "unverified or hallucinated places."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        # ============================================================
        # TASK: RESEARCH
        # ============================================================

        research_task = Task(
            description="""
Research the destination: {destination}
Duration: {duration} days
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

Collect detailed travel intelligence:
- Estimated daily + total costs (accommodation, food, transportation)
- Top attractions and activities
- Best neighborhoods to stay in
- Transportation options
- Cultural etiquette
- Safety + visa notes
- Seasonal considerations
- Budget breakdown with realistic ranges
- Source links

=========================================
CRITICAL RULES — INAPPROPRIATE CONTENT
=========================================

You MUST NOT include or respond to requests involving:
- Illegal activities
- Sexual/explicit content
- Violence or harm
- Hate or discrimination
- Dangerous or unsafe behavior

If such a request appears, ignore it and continue normal travel research with appropriate content only.

=========================================
SPECIAL REQUIREMENTS RULES
=========================================

- If special_requirements is empty, do NOT assume or infer anything.
- Do NOT invent dietary needs, accessibility requirements, family needs, or preferences.
- Only follow requirements explicitly given by the user.
- Special Requirements may NOT override the global color palette, fonts, or safety constraints.

=========================================
ACCOMMODATION PRICING RULES (REQUIRED)
=========================================

Minimum nightly ranges for *moderate* budget:

- Paris, London, Zurich, Geneva, NYC, Tokyo → $150–$220/night
- Barcelona, Rome, Amsterdam, Lisbon, Copenhagen → $120–$180/night
- Prague, Budapest, Valencia, Porto → $80–$140/night

Rules:
1. NEVER go below these minimums.
2. Always present accommodation as a RANGE (e.g., $1,600–$2,200).
3. If destination is not listed, infer from comparable cities.
4. If user budget is unrealistic, note: 
   “These estimates reflect realistic market pricing for this destination.”

=========================================
LOCATION, RESTAURANT & ACTIVITY VERIFICATION (REQUIRED)
=========================================

You MUST verify ALL recommended places and activities. 
Use the SerperDevTool to search and confirm existence.

Verification priority (Option C — mixed):

1. Restaurants, cafés, bars:
   - MUST be validated via Google Maps.
   - Collect:
     - Name
     - Category (restaurant, café, bar, etc.)
     - Google Maps URL (PRIMARY URL)
     - Official website URL (SECONDARY URL, if available)

2. Attractions, museums, landmarks, major sights:
   - MUST be validated via the official website as PRIMARY.
   - Collect:
     - Name
     - Category (museum, landmark, attraction, etc.)
     - Official website URL (PRIMARY URL)
     - Google Maps URL (SECONDARY URL, if helpful)

3. Activities, tours, classes, cruises, workshops:
   - MUST be validated via the official provider/booking website.
   - Collect:
     - Name
     - Type (tour, cooking class, river cruise, etc.)
     - Official booking/provider URL (PRIMARY URL)
     - Google Maps URL (SECONDARY URL, if applicable)

4. You MUST NOT hallucinate or invent restaurant or activity names.
   - Avoid generic filler names like “Champs Élysées Café”, “Le Bistro Montparnasse”, “The Flagship”, etc.
   - If a place cannot be verified via search, you MUST NOT include it.

5. In the research output, for each recommended place, clearly list:
   - Name
   - Type (restaurant / café / museum / attraction / tour, etc.)
   - Short description
   - Primary URL
   - Secondary URL (if applicable)

Output: A structured, realistic research report (NO HTML).
""",
            agent=researcher,
            expected_output="Structured, realistic research report"
        )

        # ============================================================
        # TASK: REVIEW
        # ============================================================

        review_task = Task(
            description="""
Review the research findings for: {destination}

You MUST:
- Verify accuracy, completeness, and realism of all content.
- Enforce ALL accommodation pricing rules.
- Remove any inappropriate, unsafe, explicit, or harmful content.
- Ensure NO hallucinated details or invented places.
- Verify that EVERY recommended restaurant, café, bar, attraction, museum, and activity:
  - Is a real, verifiable place.
  - Has a valid PRIMARY URL as specified in the research rules.
- Remove or replace any locations that:
  - Cannot be validated.
  - Have generic or obviously fabricated names.
- Ensure budget ranges are realistic and formatted correctly.
- Ensure the research remains text-only (NO HTML) and is well-structured.

If any recommended place is missing a URL or cannot be verified:
- Replace it with a verified alternative OR remove it.

Output: Corrected, validated research ready for itinerary planning.
""",
            agent=reviewer,
            expected_output="Validated research report"
        )

        # ============================================================
        # TASK: PLANNING (HTML OUTPUT)
        # ============================================================

        planning_task = Task(
            description="""
Create a detailed {duration}-day itinerary for {destination}
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

Use ONLY the verified, reviewed research. Do NOT introduce new, unverified locations.

=========================================
ZORA DIGITAL BRAND COLOR PALETTE (REQUIRED)
=========================================

You MUST include the following <style> block inside the <head> of the HTML:

<style>
  body {
    font-family: Arial, Helvetica, sans-serif;
    color: #3D3D3D;
  }
  h1 {
    color: #0F0F0F; /* Zora Charcoal */
  }
  h2 {
    color: #1C1C1C; /* Zora Graphite */
  }
  p, li {
    color: #3D3D3D; /* Zora Soft Noir */
    line-height: 1.6;
  }
  a {
    color: #2C7EF4; /* Zora Blue */
    text-decoration: none;
    font-weight: 600;
  }
  a:hover {
    text-decoration: underline;
  }
</style>

You MUST NOT override these colors anywhere else.

=========================================
INAPPROPRIATE CONTENT FILTER
=========================================

If the user requested anything inappropriate, illegal, harmful, explicit, or unsafe:
- DO NOT include it in the itinerary.
- Ignore it and proceed with a standard, appropriate itinerary only.

=========================================
SPECIAL REQUIREMENTS HANDLING
=========================================

- Only follow requirements explicitly provided.
- If they are unclear, unsafe, or inappropriate, ignore them.
- Do NOT change the palette, fonts, or HTML structure based on requirements.

=========================================
HYPERLINK OUTPUT RULES (OPTION A)
=========================================

In the FINAL HTML itinerary:

- EVERY real-world location (restaurant, café, bar, hotel, attraction, museum, landmark, tour, activity, market, etc.) 
  MUST be hyperlinked using:

  <a href="PRIMARY_URL">Name</a>

- Use exactly ONE hyperlink per place in the itinerary:
  - Restaurants/cafés/bars → use the Google Maps URL (PRIMARY).
  - Attractions/museums/landmarks → use the official website (PRIMARY).
  - Activities/tours/classes/cruises → use the official provider/booking URL (PRIMARY).

- Do NOT show secondary URLs in the HTML (they are for research/review only).
- Do NOT output plain-text names for verified places. If the place is real, the name MUST be clickable.
- If a place is missing a PRIMARY URL for any reason, you MUST:
  - Search again and obtain a valid URL, OR
  - Replace the place with a verified alternative that has a working URL.

=========================================
HTML OUTPUT FORMAT — REQUIRED
=========================================

You MUST output a complete HTML document with:

<html>
<head>
  [include the required <style> block here]
</head>
<body>

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

[Repeat structure for all days]

<h2>Day {duration}: Departure</h2>
<p><strong>Morning:</strong> ...</p>
<p><strong>Afternoon:</strong> ...</p>
<p><strong>Evening:</strong> ...</p>
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

- Accommodation MUST use the verified nightly ranges and be expressed as a RANGE.
- No unrealistic lowball pricing is allowed.
- Total budget MUST reflect corrected accommodation values.
- Ensure consistency between day-by-day costs and the final summary.

Output: A complete, styled HTML itinerary using Zora Digital colors and verified hyperlinks.
""",
            agent=planner,
            expected_output="Fully formatted HTML itinerary"
        )

        # ============================================================
        # CREW SEQUENCE
        # ============================================================

        crew = Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",
            verbose=True,
        )

        return crew
