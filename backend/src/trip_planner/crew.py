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

        # ==========================
        # AGENTS
        # ==========================

        researcher = Agent(
            role="Precision Travel Researcher",
            goal="Provide only verified, real-world travel data using exact matches from official websites and Google Maps. No creativity, no filler, no guessing.",
            backstory="You are an accuracy-first researcher. You verify everything. You never invent restaurants, addresses, activities, or locations. You only use real-world validated sources.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Travel Verification Auditor",
            goal="Audit every detail for correctness, real-world validity, address accuracy, and compliance with all anti-hallucination rules. Reject anything unverifiable.",
            backstory="You act as the final line of defense. You eliminate ALL hallucinations, wrong addresses, generic suggestions, and unverifiable items.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Evidence-Based Itinerary Planner",
            goal="Transform validated research into a structured, realistic, HTML-formatted itinerary. Use only verified locations. No creativity, no rewriting, no invented content.",
            backstory="You build accurate, professional itineraries using ONLY the reviewed data. You NEVER invent any names or content. If data is missing, you say: 'Free time or explore nearby options.' Accuracy is more important than completeness. You output clean, branded HTML using only facts that have been explicitly validated.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        # ==========================
        # TASKS
        # ==========================

        research_task = Task(
            description="""
Research the destination: {destination}
Duration: {duration} days
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

ZERO-HALLUCINATION RULE:
- Do NOT invent restaurants or activities.
- Use ONLY verified businesses on Google Maps or official websites.
- If something is missing, leave it out.

RESTAURANT & ACTIVITY VERIFICATION:
- Must appear in Google Maps or on an official website
- Must have real, current reviews (last 24 months)
- Must match the destination city exactly
- MUST include exact copied address

ACCOMMODATION:
- Research and include 3 hotel/accommodation options with:
  - Name, category, exact address, price/night, Google Maps link
  - Do not suggest fewer than 3

DISALLOWED:
- Artistic or French-sounding mashups
- Generic placeholders (“local bistro,” “historic museum”)
- Locations without valid providers, addresses, or websites

Output: Structured, bullet-point research ONLY with verified information.
""",
            agent=researcher,
            expected_output="Verified research with zero hallucinations and 3 hotel options."
        )

        review_task = Task(
            description="""
Review the research for: {destination}

RE-VERIFICATION:
- Check that all addresses, names, and links match Google Maps or the official website.
- Validate each restaurant and activity with a fresh Google search.
- Remove any unverified or mislocated entries.

ACCOMMODATION:
- Ensure 3 valid hotel options are included.
- Each must have valid pricing, link, and matching address.

REJECT ANY:
- Invented names
- Address mismatches
- Alternate-city locations
- Generic or placeholder text
- Venues with no official presence

Output: Clean, validated research only with real and current information.
""",
            agent=reviewer,
            expected_output="Cleaned research with 3 verified hotel options and zero hallucinations."
        )

        planning_task = Task(
            description="""
Create a detailed {duration}-day itinerary using ONLY the validated research.

ACCOMMODATION:
- Provide exactly THREE hotel options at the top.
- Use this format:
  <h2>Accommodation Options</h2>
  <ul>
    <li><strong>Option 1: [Hotel Name]</strong> - [Description with pricing]</li>
    ...
  </ul>

NO-INVENTION RULE:
- Use ONLY the reviewed research.
- NEVER make up restaurants, activities, or descriptions.
- Do NOT fill missing data with guesses.

MISSING DATA BEHAVIOR (CRITICAL):
If something is missing from the research:
→ Do NOT invent it.
→ Instead, write: "Free time or explore nearby options."

FORMAT FOR EACH DAY:
<h2>Day X: [Title]</h2>
<p><strong>Morning:</strong> [Specific activity]</p>
<p><strong>Afternoon:</strong> [Specific activity]</p>
<p><strong>Evening:</strong> [Specific restaurant/activity]</p>
<p><strong>Estimated Costs:</strong></p>
<ul>
  <li>Transportation: $X</li>
  <li>Food: $X</li>
  <li>Activities: $X</li>
  <li><strong>Total: $X</strong></li>
</ul>

DEPARTURE DAY:
- Must include morning and afternoon activities (not just checkout)
- Use real places or fallback phrase if nothing is available

STYLE:
- Output in full HTML
- Include this <style> block in the <head>:

<style>
  body { font-family: Arial; color: #3D3D3D; }
  h1 { color: #0F0F0F; }
  h2 { color: #1C1C1C; }
  p, li { color: #3D3D3D; line-height: 1.6; }
  a { color: #2C7EF4; font-weight: 600; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>

HYPERLINK FORMAT:
- Every location name must be a link:
  <a href="URL" target="_blank" rel="noopener noreferrer">Name</a>
""",
            agent=planner,
            expected_output="Fully formatted HTML itinerary with verified data only, 3 hotels, no hallucinations."
        )

        return Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",
            verbose=True,
        )

# ==========================
# VALIDATION FUNCTION
# ==========================

def validate_itinerary_output(itinerary_text: str):
    errors = []

    # Check for known hallucinated or filler names
    hallucinated_entries = [
        "Civilians", "1800 Chicago", "Sample Restaurant",
        "Dinner at Local Restaurant", "Local Bistro"
    ]
    for entry in hallucinated_entries:
        if entry.lower() in itinerary_text.lower():
            errors.append(f"❌ Suspected hallucinated/filler entry: '{entry}'")

    # Check for duplicate restaurants
    restaurant_patterns = [
        r'Dinner at ([A-Za-z0-9\'’\-&., ]+)',
        r'Lunch at ([A-Za-z0-9\'’\-&., ]+)',
        r'Breakfast at ([A-Za-z0-9\'’\-&., ]+)',
    ]
    restaurants = []
    for pattern in restaurant_patterns:
        restaurants += re.findall(pattern, itinerary_text, re.IGNORECASE)
    dupes = [item for item, count in Counter(restaurants).items() if count > 1]
    if dupes:
        errors.append(f"⚠️ Repeated restaurants: {', '.join(dupes[:5])}")

    # Check for generic fallback phrases
    fallback_phrases = [
        "Free time in", "Explore neighborhoods", "Visit local attractions",
        "Dinner at Local Restaurant", "Sample Restaurant", "TBD"
    ]
    for phrase in fallback_phrases:
        if re.search(phrase, itinerary_text, re.IGNORECASE):
            errors.append(f"⚠️ Generic fallback detected: '{phrase}'")

    # Check hotel option count
    hotel_options = re.findall(r'Option \d: ([^\n]+)', itinerary_text, re.IGNORECASE)
    if len(hotel_options) != 3:
        errors.append(f"⚠️ Expected 3 hotel options, found {len(hotel_options)}.")

    # Check for minimal activity on departure day
    if 'Day' in itinerary_text and 'Departure' in itinerary_text:
        if not re.search(r'Morning:.*(Visit|Breakfast|Explore)', itinerary_text, re.IGNORECASE):
            errors.append("⚠️ Departure day missing activities before checkout.")

    return "✅ Itinerary passed all validation checks." if not errors else "\n".join(errors)
