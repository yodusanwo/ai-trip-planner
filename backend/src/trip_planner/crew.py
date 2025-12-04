"""
Trip Planner CrewAI Configuration — ACCURACY-FIRST EDITION
Zora Digital Travel Planning System

Includes:
- Accuracy > Speed (strict verification)
- Hard restaurant verification
- Hard activity provider verification
- Hard address matching (verbatim source copy)
- Exact city + country matching
- Eliminates hallucinations
- Mandatory hyperlink rules
- Zora Digital brand styling
- Realistic accommodation pricing
- Full inappropriate-content filtering
- No creativity or guessing allowed
- Structured HTML output for itinerary
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
        # AGENTS — ACCURACY-FOCUSED (NO CREATIVITY)
        # ============================================================

        researcher = Agent(
            role="Precision Travel Researcher",
            goal=(
                "Provide only verified, real-world travel data using exact matches from official websites "
                "and Google Maps. No creativity, no filler, no guessing."
            ),
            backstory=(
                "You are an accuracy-first researcher. You verify everything. You never invent restaurants, "
                "addresses, activities, or locations. You only use real-world validated sources."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Travel Verification Auditor",
            goal=(
                "Audit every detail for correctness, real-world validity, address accuracy, "
                "and compliance with all anti-hallucination rules. Reject anything unverifiable."
            ),
            backstory=(
                "You act as the final line of defense. You eliminate ALL hallucinations, wrong addresses, "
                "generic suggestions, and unverifiable items."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Evidence-Based Itinerary Planner",
            goal=(
                "Transform validated research into a structured, realistic, HTML-formatted itinerary. "
                "Use only verified locations. No creativity, no rewriting, no invented content."
            ),
            backstory=(
                "You build accurate, professional itineraries using ONLY the reviewed data. You output "
                "clean, branded HTML with correct hyperlinks."
            ),
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        # ============================================================
        # TASK 1 — RESEARCH (STRICT VERIFICATION)
        # ============================================================

        research_task = Task(
            description="""
Research the destination: {destination}
Duration: {duration} days
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

=========================================================
ZERO-HALLUCINATION RULE
=========================================================
You MUST NOT:
- Invent restaurants or activities
- Create French-sounding mashups
- Add generic placeholders (“local bistro,” “wine tasting event”)
- Fill gaps with creativity
- Assume or guess any detail

If uncertain → EXCLUDE IT.

=========================================================
INAPPROPRIATE CONTENT FILTER
=========================================================
Do NOT include:
- Illegal activities
- Unsafe or harmful behavior
- Explicit or sexual content
- Hate or discrimination

=========================================================
SPECIAL REQUIREMENTS RULE
=========================================================
Only follow what is explicitly provided.
Never infer or add unstated preferences.

=========================================================
ACCOMMODATION PRICING RULES (MODERATE BUDGET)
=========================================================
Minimum realistic nightly ranges:
- Paris, London, Zurich, NYC → $150–$220/night
- Barcelona, Rome, Lisbon → $120–$180/night
- Prague, Budapest, Porto → $80–$140/night

You MUST NOT go below these numbers.

=========================================================
CITY + COUNTRY EXACT MATCH (HARD RULE)
=========================================================
A location is valid ONLY IF:
- It is located in the destination city, AND
- It is located in the correct country.

Reject immediately if:
- The Google Maps result belongs to another city
- The name exists in multiple cities or countries
- Address mismatch occurs

=========================================================
ADDRESS VERIFICATION RULES (HARD)
=========================================================
A location is VALID ONLY IF its street address is copied
EXACTLY, character-for-character, from:

- Google Maps → Restaurants & Cafés  
- Official Website → Museums, Attractions, Tours, Activities

You MUST NOT:
- Rewrite or reformat the address
- Guess street numbers or arrondissement
- Translate or shorten
- Infer components of the address

If the exact address cannot be verified → REJECT.

=========================================================
BRANCH & MULTI-LOCATION RULE
=========================================================
If multiple branches exist:
- You MUST choose the branch in the itinerary destination city
- Reject all others

=========================================================
RESTAURANT VERIFICATION RULES (HARD)
=========================================================
A restaurant is valid ONLY IF:
- It appears on Google Maps
- Address matches the destination EXACTLY
- It has recent reviews (last 24 months)
- The name is NOT generic or invented

Reject immediately:
- “La Marmite des Artistes”
- “Bistro Montparnasse”
- ANY artistic or French-sounding mashups
- ANY name not found on Google Maps

=========================================================
ACTIVITY PROVIDER VERIFICATION (HARD)
=========================================================
EVERY activity MUST have:
- A real provider
- A real physical address
- A real official website
- A confirmed presence in the destination city

Disallowed generics:
- “Wine tasting event”
- “Dinner at a riverside restaurant”
- “Local bistro”
- “Advanced French cooking class”
- ANY experience without a provider

=========================================================
RESEARCH OUTPUT FORMAT
=========================================================
For each verified location:
- Name
- Category
- EXACT address (copied verbatim)
- PRIMARY URL (Maps or official website)
- Secondary URL (optional)
- Short factual description

No HTML allowed.
""",
            agent=researcher,
            expected_output="Verified research with zero hallucinations."
        )

        # ============================================================
        # TASK 2 — REVIEW (THE ACCURACY GATEKEEPER)
        # ============================================================

        review_task = Task(
            description="""
Review the research for: {destination}

=========================================================
RE-VERIFICATION REQUIREMENTS
=========================================================
For EACH location, you MUST:
1. Perform a fresh Google Search:
   “[Business Name] [Street Address] [City] [Country]”
2. Confirm:
   - Business exists
   - Business is active
   - Address EXACTLY matches the verified source
   - Maps + Website are consistent
   - The branch is in the correct city

If ANY mismatch → REMOVE the location.

=========================================================
REJECT ALL:
=========================================================
- Wrong addresses
- Alternate-country results
- Ambiguous multi-location names
- Generic placeholders
- Invented or artistic mashups
- Activities without real providers
- Restaurants without Maps listings
- Attractions without official websites

If something is removed, replace it ONLY with a verified alternative.

Output: fully validated research.
""",
            agent=reviewer,
            expected_output="Clean, validated, hallucination-free research."
        )

        # ============================================================
        # TASK 3 — PLANNING (STRICT HTML OUTPUT)
        # ============================================================

        planning_task = Task(
            description="""
Create a detailed {duration}-day itinerary using ONLY the validated research.

=========================================================
ZORA DIGITAL BRAND COLORS (REQUIRED)
=========================================================
Insert EXACT <style> block into <head>:

<style>
  body { font-family: Arial; color: #3D3D3D; }
  h1 { color: #0F0F0F; }
  h2 { color: #1C1C1C; }
  p, li { color: #3D3D3D; line-height: 1.6; }
  a { color: #2C7EF4; font-weight: 600; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>

=========================================================
HYPERLINK RULES (NEW TAB REQUIRED)
=========================================================
EVERY location MUST include a hyperlink using EXACT format:

<a href="PRIMARY_URL" target="_blank" rel="noopener noreferrer">Name</a>

PRIMARY:
- Restaurants → Google Maps
- Attractions → Official website
- Activities → Provider website

No plain-text names.

=========================================================
ADDRESS OUTPUT RULE
=========================================================
You MUST output the address EXACTLY as provided by the reviewer.
Do NOT:
- Modify formatting
- Rewrite the street name
- Fix perceived typos
- Add arrondissement numbers
- Translate anything

If address is missing → EXCLUDE the location.

=========================================================
STRICT NO-INVENTION RULE
=========================================================
You MUST NOT:
- Add fictional places
- Add generic restaurants
- Suggest activities not in the research
- Add ANYTHING not reviewed

=========================================================
HTML STRUCTURE (MANDATORY)
=========================================================
Follow the exact Day-by-Day structure already in your itinerary spec.
""",
            agent=planner,
            expected_output="Accurate, fully verified HTML itinerary."
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
