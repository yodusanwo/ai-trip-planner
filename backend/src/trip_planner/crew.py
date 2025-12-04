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
        return response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', '')
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
            goal="Gather only real, verified travel listings. No fake names or placeholders. Use blog links only when necessary.",
            backstory="You are a no-hallucination researcher. You verify every listing using trusted sources. If something can't be confirmed, you find a matching travel blog.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Travel Quality Auditor",
            goal="Audit the research for correctness, validity, and clean blog category alignment. Remove hallucinated names like 'Detroit Market' and check all URLs.",
            backstory="You are the last line of defense. You catch fake places, broken links, and blog mismatches. You allow only factual listings.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Itinerary Generator",
            goal="Create a structured, clean HTML itinerary using verified entries. Move all blog fallback links to the end, and verify that links are working before including them.",
            backstory="You turn research into a clean itinerary. You validate all blog links and use one per category only if valid and useful.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        # ---------------------
        # Tasks
        # ---------------------

        research_task = Task(
            description="""
Research: {destination}
Travel Style: {travel_style}
Duration: {duration} days
Budget: {budget}
Special Requirements: {special_requirements}

✅ Use only verified listings from Google Maps or official sources.

❌ Do NOT use made-up names like 'Detroit Market', 'Local eatery', etc.

🏨 Provide 3 valid hotels with full names, price range, and address.

📚 If you cannot find enough restaurants, attractions, or nightlife:
→ Provide a blog article from a trusted travel source.

Each blog must be:
- A full article (not a category page)
- Relevant to one of the following:
  Adventure, Relaxation, Cultural, Family-Friendly, Food & Dining, Nature & Outdoors, Nightlife
- Include: Title, URL, short summary
""",
            agent=researcher,
            expected_output="Verified listings + fallback blog links if needed"
        )

        review_task = Task(
            description="""
Review the research results for:
- Broken or invalid URLs (must return HTTP 200)
- Made-up place names like 'Detroit Market', 'Local eatery'
- Blog links that don't match their assigned category
- Ensure 3 hotel options are valid

Reject:
- Homepages (like /food or /restaurants)
- Blogs that link to top-level directories
- Fake sounding names
""",
            agent=reviewer,
            expected_output="Cleaned, audited data with validated URLs and hotels"
        )

        planning_task = Task(
            description="""
Create a {duration}-day itinerary for {destination}.

🏨 Start with: <h2>Accommodation Options</h2>
Include 3 hotels, with:
- Name
- Price range
- Location
- Hyperlink (verified)

📅 For each day, use:
<h2>Day X: [Title]</h2>
<p><strong>Morning:</strong> Specific Activity</p>
<p><strong>Afternoon:</strong> Specific Activity</p>
<p><strong>Evening:</strong> Specific Restaurant or Activity</p>

⚠️ Do NOT include vague names like:
- 'Detroit Market'
- 'Local eatery'
- 'Shopping district'
- 'Downtown cafe'

📚 If specific restaurants/activities are missing:
→ At the end, include:

<h2>Suggestions & Resources</h2>
<ul>
  <li><strong>Category:</strong> <a href="VALID_URL" target="_blank" rel="noopener noreferrer">Blog Title</a> – Short summary</li>
</ul>

🎯 Only ONE blog per category.

✅ Use blog ONLY if valid (HTTP 200, HTML, travel source).
""",
            agent=planner,
            expected_output="Formatted HTML itinerary with blog links in final section only"
        )

        return Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",
            verbose=True,
        )


# ---------------------
# Validator
# ---------------------

def validate_itinerary_output(itinerary_text: str):
    errors = []

    # 1. Check for fake sounding names
    invalid_phrases = ['Detroit Market', 'local eatery', 'local bistro', 'shopping area']
    for phrase in invalid_phrases:
        if phrase.lower() in itinerary_text.lower():
            errors.append(f"❌ Invalid phrase found: '{phrase}'")

    # 2. Check blog links
    blog_links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', itinerary_text)
    for url, title in blog_links:
        if not is_valid_url(url):
            errors.append(f"❌ Blog URL not valid or reachable: {url}")

    # 3. Ensure blog section appears only once
    if itinerary_text.count("Suggestions & Resources") > 1:
        errors.append("⚠️ Suggestions section appears more than once")

    # 4. Check for hotel options
    hotel_count = len(re.findall(r'Option \d: ', itinerary_text))
    if hotel_count != 3:
        errors.append(f"⚠️ Found {hotel_count} hotel options. Expected 3.")

    return "✅ Passed all validation checks" if not errors else "\n".join(errors)
