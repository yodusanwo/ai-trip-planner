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
- Automated validation function for quality assurance

PROMPT LENGTH METRICS (as of latest update):
- Research task: ~3,900 characters
- Review task: ~1,000 characters
- Planning task: ~1,800 characters
- Total: ~6,700 characters

Note: Prompt length is monitored to balance detail with efficiency.
Too long = increased costs, slower processing, reduced focus.
Too short = missed requirements, hallucinations, inconsistent output.
"""
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
import re
from collections import Counter


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
ACCOMMODATION RESEARCH REQUIREMENT
=========================================================
You MUST research and provide AT LEAST 3 verified hotel/accommodation options.

For each hotel, include:
- Hotel name (verified on Google Maps or official website)
- Category (budget/moderate/luxury)
- EXACT address (copied verbatim)
- Price range per night
- PRIMARY URL (Google Maps or official booking website)
- Description and key features
- Neighborhood/location

You MUST provide at least 3 options to give the planner choices.

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
            expected_output="Verified research with zero hallucinations, including at least 3 hotel options."
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
   "[Business Name] [Street Address] [City] [Country]"
2. Confirm:
   - Business exists
   - Business is active
   - Address EXACTLY matches the verified source
   - Maps + Website are consistent
   - The branch is in the correct city

If ANY mismatch → REMOVE the location.

=========================================================
ACCOMMODATION VERIFICATION REQUIREMENT
=========================================================
You MUST ensure the research includes AT LEAST 3 verified hotel options.

For each hotel, verify:
- Hotel exists on Google Maps or official website
- Address matches destination city exactly
- Price information is realistic and matches budget level
- Booking website or Maps link is valid

If fewer than 3 hotels are provided → Search for and add verified alternatives until you have at least 3.

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

Output: fully validated research with at least 3 hotel options.
""",
            agent=reviewer,
            expected_output="Clean, validated, hallucination-free research with at least 3 verified hotel options."
        )

        # ============================================================
        # TASK 3 — PLANNING (STRICT HTML OUTPUT)
        # ============================================================

        planning_task = Task(
            description="""
Create a detailed {duration}-day itinerary using ONLY the validated research.

=========================================================
ACCOMMODATION RULES (MANDATORY)
=========================================================
You MUST provide EXACTLY THREE hotel options at the beginning of the itinerary.

Format:
<h2>Accommodation Options</h2>
<ul>
  <li><strong>Option 1: [Hotel Name]</strong> - [Description with pricing]</li>
  <li><strong>Option 2: [Hotel Name]</strong> - [Description with pricing]</li>
  <li><strong>Option 3: [Hotel Name]</strong> - [Description with pricing]</li>
</ul>

Each option MUST include:
- Specific hotel name (from verified research)
- Description
- Price range per night
- Location/neighborhood

You MUST NOT:
- Provide only 1 or 2 options
- Provide more than 3 options
- Use generic placeholders like "local hotel" or "budget accommodation"
- Repeat the same hotel in multiple options

=========================================================
NO GENERIC DESCRIPTIONS RULE (CRITICAL)
=========================================================
EVERY activity MUST have a SPECIFIC, NAMED place or activity.

FORBIDDEN generic descriptions:
- "Exploration of the local art galleries" → Use: "Visit [Specific Gallery Name]"
- "Free time in the Arts District" → Use: "Explore [Specific Museum/Gallery Name] in the Arts District"
- "Visit local attractions" → Use: "Visit [Specific Attraction Name]"
- "More city exploration" → Use: "Visit [Specific Place Name]"
- "Explore neighborhoods" → Use: "Explore [Specific Neighborhood Name] and visit [Specific Place]"

REQUIRED format:
- Morning: Visit [Specific Museum/Gallery/Attraction Name]
- Afternoon: Explore [Specific Neighborhood Name] and visit [Specific Place Name]
- Evening: Dinner at [Specific Restaurant Name]

If you cannot find a specific named place for an activity → EXCLUDE that activity and use a different verified location from the research.

=========================================================
DEPARTURE DAY REQUIREMENTS (MANDATORY)
=========================================================
Day {duration} (Departure) MUST include actual activities, not just check-out.

REQUIRED structure:
<h2>Day {duration}: Departure</h2>
<p><strong>Morning:</strong> [Specific activity - e.g., "Visit [Museum Name]" or "Breakfast at [Restaurant Name]" or "Final shopping at [Market/Store Name]"]</p>
<p><strong>Afternoon:</strong> [Specific activity - e.g., "Last-minute exploration of [Place Name]" or "Lunch at [Restaurant Name]"]</p>
<p><strong>Evening:</strong> Check-out from hotel and departure to airport</p>
<p><strong>Estimated Costs:</strong></p>
<ul>
  <li>Transportation: $X</li>
  <li>Food: $X</li>
  <li><strong>Total: $X</strong></li>
</ul>

You MUST NOT:
- Write only "Check-out and departure"
- Use generic descriptions like "Free time" or "Last-minute shopping"
- Skip activities on departure day

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
- Use generic descriptions without specific names

=========================================================
HTML STRUCTURE (MANDATORY)
=========================================================
Follow this EXACT structure:

<h1>{duration}-Day {travel_style}-Friendly Itinerary in {destination}</h1>

<h2>Accommodation Options</h2>
[Three hotel options as specified above]

<h2>Day 1: [Title]</h2>
<p><strong>Morning:</strong> [Specific named activity]</p>
<p><strong>Afternoon:</strong> [Specific named activity]</p>
<p><strong>Evening:</strong> [Specific named activity]</p>
<p><strong>Estimated Costs:</strong></p>
<ul>
  <li>Transportation: $X</li>
  <li>Food: $X</li>
  <li>Activities: $X</li>
  <li><strong>Total: $X</strong></li>
</ul>

[Repeat for Days 2 through {duration}-1]

<h2>Day {duration}: Departure</h2>
[Include actual activities as specified above]

<h2>Total Estimated Budget Summary</h2>
<ul>
  <li>Accommodation ({duration} nights): $X–$Y</li>
  <li>Total Food & Drink: $X</li>
  <li>Total Attractions: $X</li>
  <li>Total Transportation: $X</li>
  <li><strong>Grand Total: ~$X–$Y</strong></li>
</ul>
""",
            agent=planner,
            expected_output="Accurate, fully verified HTML itinerary with three hotel options and specific named activities for all days including departure."
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


# ------------------- Validation Function -------------------

def validate_itinerary_output(itinerary_text: str):
    """
    Check final output for repeated restaurants, repeated activities, and inconsistent accommodations.
    
    Args:
        itinerary_text: The itinerary text to validate
        
    Returns:
        String with validation results (✅ if passed, ⚠️ warnings if issues found)
    """
    errors = []
    
    # Extract restaurants and activities using multiple patterns
    restaurants = []
    activities = []
    
    # Find restaurants (various patterns)
    restaurant_patterns = [
        r'Dinner at ([A-Za-z0-9\'’\-&., ]+)',
        r'Lunch at ([A-Za-z0-9\'’\-&., ]+)',
        r'Breakfast at ([A-Za-z0-9\'’\-&., ]+)',
        r'Restaurant: ([A-Za-z0-9\'’\-&., ]+)',
        r'Dine at ([A-Za-z0-9\'’\-&., ]+)',
    ]
    
    for pattern in restaurant_patterns:
        restaurants.extend(re.findall(pattern, itinerary_text, re.IGNORECASE))
    
    # Find activities (various patterns)
    activity_patterns = [
        r'Visit ([A-Za-z0-9\'’\-&., ]+)',
        r'Explore ([A-Za-z0-9\'’\-&., ]+)',
        r'Tour ([A-Za-z0-9\'’\-&., ]+)',
        r'See ([A-Za-z0-9\'’\-&., ]+)',
        r'Activity: ([A-Za-z0-9\'’\-&., ]+)',
    ]
    
    for pattern in activity_patterns:
        activities.extend(re.findall(pattern, itinerary_text, re.IGNORECASE))
    
    # Check for repeated restaurants
    if restaurants:
        restaurant_counts = Counter(restaurants)
        duplicates = [item for item, count in restaurant_counts.items() if count > 1]
        if duplicates:
            errors.append(f"⚠️ Repeated restaurants: {', '.join(duplicates[:5])}")  # Limit to first 5
    
    # Check for repeated activities
    if activities:
        activity_counts = Counter(activities)
        duplicates = [item for item, count in activity_counts.items() if count > 1]
        if duplicates:
            errors.append(f"⚠️ Repeated activities: {', '.join(duplicates[:5])}")  # Limit to first 5
    
    # Accommodation consistency check
    accommodation_patterns = [
        r'(Stay at|Accommodation:|Hotel:)\s*([^\n]+)',
        r'Accommodation[:\s]+([^\n]+)',
        r'Hotel[:\s]+([^\n]+)',
    ]
    
    accommodations = []
    for pattern in accommodation_patterns:
        matches = re.findall(pattern, itinerary_text, re.IGNORECASE)
        if matches:
            if isinstance(matches[0], tuple):
                accommodations.extend([acc[1].strip() if len(acc) > 1 else acc[0].strip() for acc in matches])
            else:
                accommodations.extend([acc.strip() for acc in matches])
    
    if len(accommodations) > 1:
        unique_hotels = set(accommodations)
        if len(unique_hotels) > 1:
            errors.append(f"⚠️ Multiple accommodations found: {', '.join(list(unique_hotels)[:3])}")
    
    # Check for hotel options format (Option 1, Option 2, Option 3) - MUST be exactly 3
    hotel_options = re.findall(r'Option\s*\d+[:\s]+([^\n]+)', itinerary_text, re.IGNORECASE)
    if hotel_options:
        if len(hotel_options) != 3:
            errors.append(f"⚠️ {len(hotel_options)} hotel options found; MUST be exactly 3 options.")
    else:
        # Check if accommodations section exists but doesn't use Option format
        if 'Accommodation' in itinerary_text or 'Hotel' in itinerary_text:
            errors.append("⚠️ Accommodation section found but not in 'Option 1/2/3' format. Must provide exactly 3 hotel options.")
    
    # Check for generic descriptions (common patterns that indicate lack of specific names)
    generic_patterns = [
        r'Exploration of the local',
        r'Free time in',
        r'Visit local attractions',
        r'More city exploration',
        r'Explore neighborhoods',
        r'local art galleries',
        r'local attractions',
    ]
    
    for pattern in generic_patterns:
        if re.search(pattern, itinerary_text, re.IGNORECASE):
            errors.append(f"⚠️ Generic description detected: '{pattern}'. All activities must have specific named places.")
            break
    
    # Check that departure day has actual activities (not just check-out)
    departure_patterns = [
        r'Day\s*\d+[:\s]*[Dd]eparture',
        r'Day\s*\d+[:\s]*[Cc]heck[- ]out',
    ]
    
    has_departure_activities = False
    for pattern in departure_patterns:
        match = re.search(pattern, itinerary_text, re.IGNORECASE)
        if match:
            # Check if there are activities after departure header
            start_pos = match.end()
            departure_section = itinerary_text[start_pos:start_pos+500]  # Check next 500 chars
            # Look for morning/afternoon activities (not just check-out)
            if re.search(r'(Morning|Afternoon)[:\s]+(?!.*check[- ]out|.*departure)', departure_section, re.IGNORECASE):
                has_departure_activities = True
            break
    
    if not has_departure_activities and any(re.search(p, itinerary_text, re.IGNORECASE) for p in departure_patterns):
        errors.append("⚠️ Departure day appears to only have check-out. Must include actual activities (morning/afternoon) before departure.")
    
    if not errors:
        return "✅ Itinerary passed all validation checks."
    
    return "\n".join(errors)
