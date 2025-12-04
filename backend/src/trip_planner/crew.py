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

        # ------------------ AGENTS ------------------

        researcher = Agent(
            role="Precision Travel Researcher",
            goal="Research real-world data for a specific travel style and destination. Use only verifiable sources (Google Maps, official websites, and curated blogs).",
            backstory="You are a research expert focused on accuracy. You never guess or fabricate. You always verify restaurants, attractions, and hotels. If an item cannot be found, you provide a blog link instead.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Travel Data Auditor",
            goal="Validate and clean the research data for accuracy. Remove hallucinations, invented names, or unverifiable items. Ensure at least 3 hotel options exist.",
            backstory="You ensure that the travel data is accurate, properly sourced, and safe for use. You reject generic placeholders and double-check all URLs, addresses, and business names.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="HTML Itinerary Builder",
            goal="Turn validated research into a clean HTML travel itinerary. Format consistently. Use real names only. If any items are missing, insert a blog fallback based on travel style at the bottom of the day.",
            backstory="You build accurate itineraries with verified names only. When something is missing, you insert ONE blog fallback per day that matches the travel style. You never reuse blogs across days or categories.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        # ------------------ TASKS ------------------

        research_task = Task(
            description="""
Research the destination: {destination}
Duration: {duration} days
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

🔒 HALLUCINATION BLOCKING:
- Do NOT invent names
- Only use businesses with verified presence in the destination (Google Maps, official sites)
- Use copy-paste address accuracy
- Never reuse results from different cities

🏨 ACCOMMODATION RULES:
- You MUST provide 3 hotel/accommodation options
- Each must include:
  - Name
  - Price range per night
  - Category (budget/moderate/luxury)
  - Neighborhood
  - Google Maps or official URL

📚 BLOG FALLBACK RULES:
If you cannot verify specific restaurants, activities, or attractions:
→ Search for a curated blog or article matching the {travel_style}

CATEGORY MAPPING:
- Adventure → “Outdoor Adventure Activities in {destination}”
- Relaxation → “Best Spas and Wellness in {destination}”
- Cultural → “Must-See Museums & Historic Spots in {destination}”
- Food & Dining → “Top Restaurants in {destination}”
- Nature & Outdoors → “Best Nature Trails and Parks in {destination}”
- Nightlife → “Top Bars, Clubs, and Nightlife in {destination}”
- Family-Friendly → “Things to Do with Kids in {destination}”

✅ Each blog must include:
- Blog title
- Direct link
- Source (e.g., Eater, TimeOut, Lonely Planet)
- 1-line summary
""",
            agent=researcher,
            expected_output="Verified data with 3 hotels and curated blog links if needed."
        )

        review_task = Task(
            description="""
Audit all research for: {destination}

☑️ You MUST:
- Verify all restaurants/activities exist and are in the correct city
- Ensure addresses match sources exactly
- Confirm blogs are real, recent, and match the {travel_style}

❌ REJECT:
- Fake or invented names
- Mislocated businesses
- Blogs that don’t match the category (e.g., family blog used for nightlife)

✅ Ensure exactly 3 valid accommodations are present
""",
            agent=reviewer,
            expected_output="Cleaned, verified research with 3 hotels and valid blog fallback links"
        )

        planning_task = Task(
            description="""
Create a structured, fully HTML-formatted {duration}-day itinerary for {destination} using validated research.

🏨 HOTEL SECTION:
- List 3 hotel options at top
- Include name, price, category, location
- Use bullet list

📅 DAILY STRUCTURE:
Each day must follow this format:
<h2>Day X: [Title]</h2>
<p><strong>Morning:</strong> [Specific activity]</p>
<p><strong>Afternoon:</strong> [Specific activity]</p>
<p><strong>Evening:</strong> [Specific activity or restaurant]</p>
<p><strong>Estimated Costs:</strong></p>
<ul>
  <li>Transportation: $X</li>
  <li>Food: $X</li>
  <li>Activities: $X</li>
  <li><strong>Total: $X</strong></li>
</ul>

🧠 IF MISSING DATA (NO VALID RESTAURANT OR ACTIVITY):
→ INSERT ONE blog link at the end of the day:
<p><strong>Suggestions:</strong> 
<a href="{blog_url}" target="_blank" rel="noopener noreferrer">{blog_title}</a></p>

The blog MUST match {travel_style} using this mapping:
- Adventure → Activities blog
- Food & Dining → Restaurant blog
- Nightlife → Bars & clubs blog
- Family-Friendly → Kid-friendly attractions blog

DO NOT repeat the same blog across multiple days.

🎨 BRAND STYLE (HTML HEAD):
Include:
<style>
  body { font-family: Arial; color: #3D3D3D; }
  h1 { color: #0F0F0F; }
  h2 { color: #1C1C1C; }
  p, li { color: #3D3D3D; line-height: 1.6; }
  a { color: #2C7EF4; font-weight: 600; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
""",
            agent=planner,
            expected_output="HTML-formatted itinerary with one blog fallback per day if needed."
        )

        return Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",
            verbose=True,
        )


# ------------------ VALIDATION FUNCTION ------------------

def validate_itinerary_output(itinerary_text: str, travel_style: str = ""):
    errors = []

    # Blog reuse detection
    blog_links = re.findall(r'href="([^"]+)"', itinerary_text)
    if len(set(blog_links)) < len(blog_links) // 2:
        errors.append("⚠️ Blog links are reused excessively across different days.")

    # Style mismatch detection
    if travel_style and "family" in "".join(blog_links).lower() and "food" in travel_style.lower():
        errors.append("❌ A 'Family' blog link was incorrectly used for a Food & Dining trip.")

    # Check hotel count
    hotel_options = re.findall(r'Option \d: ([^\n<]+)', itinerary_text)
    if len(hotel_options) != 3:
        errors.append(f"⚠️ Expected 3 hotel options, found {len(hotel_options)}.")

    return "✅ Itinerary passed all validation checks." if not errors else "\n".join(errors)
