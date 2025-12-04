from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
import requests
import re
from collections import Counter

# -----------------------
# Utility: URL Validator
# -----------------------
def is_valid_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return (
            response.status_code == 200 and
            'text/html' in response.headers.get('Content-Type', '')
        )
    except requests.RequestException:
        return False


class TripPlanner:
    def __init__(self):
        self._crew = None

    def crew(self) -> Crew:
        if self._crew is None:
            self._crew = self._create_crew()
        return self._crew

    def _create_crew(self) -> Crew:
        search_tool = SerperDevTool()

        # ---------------------
        # Agents
        # ---------------------
        researcher = Agent(
            role="Verified Travel Researcher",
            goal="Gather real, verified travel listings. No placeholder names. Include fallback blogs if needed.",
            backstory="You find reliable listings for restaurants, attractions, and hotels. If nothing verifiable is found, return a relevant travel blog article instead.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Travel Accuracy Auditor",
            goal="Check for hallucinations, generic names, and broken links. Verify all data. Replace vague entries with verified blogs if needed.",
            backstory="You audit listings for accuracy, validate URLs, and ensure correct formatting. You eliminate fake names like 'Detroit Market'.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Clean Itinerary Formatter",
            goal="Generate a structured HTML itinerary using verified listings and blog fallbacks when needed. Ensure all names are linked and real.",
            backstory="You turn research into clean itineraries. If a location can't be verified, link to a helpful blog instead and place all blogs in a 'Suggestions' section at the end.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        # ---------------------
        # Tasks
        # ---------------------
        research_task = Task(
            description="""
Research {destination} for a {duration}-day {travel_style}-style trip.

✅ Find real-world listings:
- Restaurants, attractions, and 3 hotel options
- Copy names and links exactly from Maps or official websites

❌ DO NOT include:
- Placeholders like 'Detroit Market', 'local café', or 'downtown eats'
- Generic suggestions

📚 If nothing valid is found in a category, find a relevant travel blog:
- Title, URL, short summary
- One blog per category (e.g., Top Family Attractions in Detroit)

⚠️ Blog must be:
- A full article, not a homepage or directory
- Valid URL (status 200, HTML page)
""",
            agent=researcher,
            expected_output="Verified listings + fallback blog links (if needed)"
        )

        review_task = Task(
            description="""
Validate listings for: {destination}

1. Check for invalid names like 'local eatery', 'Detroit Market'
2. Make sure all URLs are valid (status 200 + content-type: HTML)
3. Ensure 3 hotels are included
4. Limit blogs to 1 per category

If any blog or place fails validation → remove or replace with a valid one.
""",
            agent=reviewer,
            expected_output="Cleaned research with valid links and no hallucinations"
        )

        planning_task = Task(
            description="""
Using verified research only, create a {duration}-day itinerary for {destination}.

🏨 Section: <h2>Accommodation Options</h2>
List 3 hotel options:
- Name
- Price range
- Location
- Hyperlink as: <a href="..." target="_blank" rel="noopener noreferrer">Book Here</a>

📅 Daily Structure:
<h2>Day X: [Theme]</h2>
<p><strong>Morning:</strong> Visit <a href="..." target="_blank">[Place]</a></p>
<p><strong>Afternoon:</strong> Explore <a href="..." target="_blank">[Attraction]</a></p>
<p><strong>Evening:</strong> Dinner at <a href="..." target="_blank">[Restaurant]</a></p>

⚠️ Do NOT include:
- Generic names like "local bistro", "Detroit Market"
- Unlinked names
- Broken blog or business URLs

📚 Fallbacks (if needed):
<h2>Suggestions & Resources</h2>
<ul>
  <li><strong>[Category]:</strong> <a href="VALID_URL" target="_blank" rel="noopener noreferrer">[Blog Title]</a> – Short description</li>
</ul>

✅ One blog per category only.
""",
            agent=planner,
            expected_output="HTML-formatted itinerary with verified links and blog fallback section"
        )

        return Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",
            verbose=True,
        )


# ---------------------
# Validator Function
# ---------------------
def validate_itinerary_output(itinerary_text: str):
    errors = []

    # Invalid place phrases
    forbidden = ['Detroit Market', 'local eatery', 'local bistro', 'downtown market']
    for phrase in forbidden:
        if phrase.lower() in itinerary_text.lower():
            errors.append(f"❌ Invalid phrase found: '{phrase}'")

    # Find all links and validate
    links = re.findall(r'href="([^"]+)"', itinerary_text)
    for url in links:
        if not is_valid_url(url):
            errors.append(f"❌ Broken or invalid URL: {url}")

    # Check blog section duplicates
    if itinerary_text.count("Suggestions & Resources") > 1:
        errors.append("⚠️ Suggestions section appears more than once")

    # Hotel count check
    hotel_count = len(re.findall(r'Option \d:', itinerary_text))
    if hotel_count != 3:
        errors.append(f"⚠️ Found {hotel_count} hotel options. Expected 3.")

    return "✅ Passed all validation checks" if not errors else "\n".join(errors)
