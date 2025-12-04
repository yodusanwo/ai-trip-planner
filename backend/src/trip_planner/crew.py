"""
Trip Planner CrewAI Configuration — ACCURACY-FIRST EDITION
Zora Digital Travel Planning System

Includes:
- Accuracy over speed (strict verification)
- Hard restaurant verification rules
- Hard activity provider verification rules
- City + country matching enforcement
- Address validation
- No hallucinated names / generic placeholders
- Mandatory hyperlink rules
- Zora Digital brand colors
- Accommodation realism rules
- Inappropriate request filtering
- No creative generation
"""
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool


class TripPlanner:
    def __init__(self):
        self._crew = None

    def crew(self) -> Crew:
        if self._crew is None:
            self._crew = self._create_crew()
        return self._crew

    def _create_crew(self) -> Crew:
        search_tool = SerperDevTool()

        # ============================================================
        # AGENTS — ACCURACY-FOCUSED
        # ============================================================

        researcher = Agent(
            role="Precision Travel Researcher",
            goal=(
                "Provide only fully verified, real-world travel data. "
                "No creativity, no guessing, no assumptions — accuracy only."
            ),
            backstory=(
                "You are an accuracy-first researcher who relies exclusively on validated sources. "
                "You never invent businesses, activities, or restaurants."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Travel Verification Auditor",
            goal=(
                "Audit every detail for correctness, real-world validity, address accuracy, "
                "and strict compliance with all anti-hallucination rules."
            ),
            backstory=(
                "You act as the final verification layer. You remove or replace anything not fully validated."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Evidence-Based Itinerary Planner",
            goal=(
                "Create a structured, realistic, visually polished itinerary using ONLY verified data. "
                "No creative additions, no fictional names, no filler."
            ),
            backstory=(
                "You turn validated research into a complete itinerary. You NEVER invent places."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        # ============================================================
        # TASK 1 — RESEARCH
        # ============================================================

        research_task = Task(
            description="""
Research destination: {destination}
Duration: {duration} days
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

=========================================================
ZERO-HALLUCINATION RULE
=========================================================
You MUST NOT:
- Invent restaurants
- Invent activities
- Create French-sounding mashups
- Recommend generic placeholders (“wine tasting event”)
- Guess or assume anything
- Fill gaps creatively

If uncertain → EXCLUDE IT.

=========================================================
INAPPROPRIATE CONTENT FILTER
=========================================================
Ignore all requests involving:
- Illegal actions
- Harm or danger
- Explicit/sexual content
- Hate or discrimination

Do NOT reference disallowed content.

=========================================================
SPECIAL REQUIREMENTS RULE
=========================================================
Only follow explicitly stated requirements.
Do NOT infer or add unstated needs.

=========================================================
ACCOMMODATION PRICING RULES (MODERATE BUDGET)
=========================================================
Minimum realistic ranges:
- Paris, London, Zurich, NYC → $150–$220/night
- Barcelona, Rome, Lisbon → $120–$180/night
- Prague, Budapest, Porto → $80–$140/night

Never go below these values.

=========================================================
RESTAURANT VERIFICATION RULES (HARD)
=========================================================
A restaurant is valid ONLY IF:
- It appears on Google Maps (PRIMARY)
- Has an address in the destination city + country
- Has recent reviews (24 months)
- Is not duplicated in another country
- Is not a generic or invented name

EXCLUDE immediately:
- “La Marmite des Artistes”
- “Bistro Montparnasse”
- Any mashup names
- Names not found in Maps

=========================================================
ACTIVITY PROVIDER VERIFICATION (HARD)
=========================================================
ALL activities MUST:
- Be tied to a specific real provider
- Provider must have an official website (PRIMARY)
- Provider must be located in the destination city
- Provider must show credible online presence

Disallowed generic activities:
- “Wine tasting event”
- “Dinner at a riverside restaurant”
- “Advanced cooking class”
- “Food tour in [district]”
- “Spa day at the Ritz Escoffier” (incorrect combo)

If no valid provider exists → EXCLUDE IT.

=========================================================
ADDRESS VERIFICATION RULE (HARD)
=========================================================
EVERY location must:
- Have a verifiable address
- Be in the correct city AND country
- Match the itinerary destination exactly

If address mismatch → Reject.

=========================================================
MULTI-COUNTRY AMBIGUITY RULE
=========================================================
If name exists in multiple locations:
- Explicitly search “NAME + DESTINATION CITY + COUNTRY”
- Accept ONLY the match in the correct city/country

If ambiguous → Reject.

=========================================================
RESEARCH OUTPUT FORMAT
=========================================================
For each verified location include:
- Name
- Category
- Address
- Official website OR Google Maps link (PRIMARY)
- Secondary link if available
- Short factual description

DO NOT use HTML.
""",
            agent=researcher,
            expected_output="Verified, accurate research with NO hallucinations"
        )

        # ============================================================
        # TASK 2 — REVIEW (THE GATEKEEPER)
        # ============================================================

        review_task = Task(
            description="""
Review the research for destination: {destination}

You MUST:
- Validate every restaurant and provider
- Remove anything not in the correct city + country
- Reject invented or generic names
- Reject businesses with no confirmed website/Maps listing
- Reject ambiguous multi-location names
- Confirm activities have real providers
- Confirm restaurants have Google Maps URLs
- Confirm attractions have official websites
- Confirm businesses are active (recent reviews)
- Remove any unverifiable locations

Your job is to eliminate ALL hallucinations.

Output: fully validated research.
""",
            agent=reviewer,
            expected_output="Verified, hallucination-free research"
        )

        # ============================================================
        # TASK 3 — PLANNING (HTML OUTPUT)
        # ============================================================

        planning_task = Task(
            description="""
Create a detailed {duration}-day itinerary using ONLY the validated research.

=========================================================
ZORA DIGITAL BRAND COLORS (REQUIRED)
=========================================================
Insert EXACT <style> block inside <head>:

<style>
  body { font-family: Arial; color: #3D3D3D; }
  h1 { color: #0F0F0F; }
  h2 { color: #1C1C1C; }
  p, li { color: #3D3D3D; line-height: 1.6; }
  a { color: #2C7EF4; font-weight: 600; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>

=========================================================
HYPERLINK RULES — NEW TAB REQUIRED
=========================================================
ALL hyperlinks MUST be formatted EXACTLY:

<a href="PRIMARY_URL" target="_blank" rel="noopener noreferrer">Name</a>

Rules:
- Restaurants → Google Maps link only
- Attractions → Official website only
- Activities → Official provider website only
- No plain text names
- No missing links

=========================================================
STRICT NO-INVENTION RULE
=========================================================
You MUST NOT:
- Create fictional restaurants
- Create fictional activities/events
- Suggest generic placeholders
- Invent names or locations
- Add anything not in the reviewer output

=========================================================
HTML STRUCTURE (REQUIRED)
=========================================================
[Use the same Day-by-Day structure from your existing itinerary rules. Omitted here for length.]
""",
            agent=planner,
            expected_output="Accurate HTML itinerary with verified links"
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
