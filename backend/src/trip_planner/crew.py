from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from collections import defaultdict
import re


class TripPlanner:
    def __init__(self):
        self._crew = None

    def crew(self) -> Crew:
        if self._crew is None:
            self._crew = self._create_crew()
        return self._crew

    def _create_crew(self) -> Crew:
        search_tool = SerperDevTool()

        # === AGENTS ===

        researcher = Agent(
            role="Precision Travel Researcher",
            goal="Gather verified travel data. Use only trustworthy sources (Google Maps, official websites, or curated travel blogs). Never invent names or locations.",
            backstory="You are a highly accurate researcher. If you can't find a verifiable activity, you provide a real blog link from a trusted source that matches the user's travel style.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Travel Research Auditor",
            goal="Verify all entries for accuracy, remove hallucinations, and check blog category correctness.",
            backstory="You ensure that all listings are real, addresses match sources, and blog suggestions match their assigned category.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Itinerary Builder",
            goal="Use validated research to generate a clean, day-by-day HTML itinerary. Add blog suggestions (1 per category) at the end if some entries are missing.",
            backstory="You turn reviewed research into a structured itinerary with clear formatting and one blog suggestion per missing activity category.",
            tools=[search_tool],
            verbose=True,
            allow_delegation=False,
        )

        # === TASKS ===

        research_task = Task(
            description="""
Research destination: {destination}
Duration: {duration} days
Budget: {budget}
Travel Style: {travel_style}
Special Requirements: {special_requirements}

🚫 Do NOT invent places.
✅ Use Google Maps, official websites, or curated blog sources.

🏨 Hotels: Provide 3 verified hotel options. Include name, price range, location, and primary URL.

📚 Fallback blog requirement:
If specific restaurants, attractions, or activities are not verifiable, search for one high-quality blog per category based on travel style.

Blog matching rules:
- Adventure → "Outdoor Activities in [destination]"
- Relaxation → "Top Spas and Wellness in [destination]"
- Cultural → "Best Museums or Cultural Attractions in [destination]"
- Food & Dining → "Top Restaurants or Food Tours in [destination]"
- Nature & Outdoors → "Parks or Outdoor Spaces in [destination]"
- Nightlife → "Bars or Clubs in [destination]"
- Family-Friendly → "Things to Do with Kids in [destination]"

Each blog must include:
- Title
- URL
- 1-sentence summary
- Source (TimeOut, Lonely Planet, etc.)
""",
            agent=researcher,
            expected_output="Verified list of activities, 3 hotels, and blog fallback links"
        )

        review_task = Task(
            description="""
Review travel research for: {destination}

🧹 You must:
- Remove fake listings
- Validate each activity, hotel, and restaurant
- Check that each blog matches its assigned category using title/content

Examples:
- If blog is labeled "Cultural" but it's about outdoor parks → Reject
- If hotel URLs are broken → Replace or remove

Ensure 3 hotel options are included.
""",
            agent=reviewer,
            expected_output="Cleaned and validated travel data"
        )

        planning_task = Task(
            description="""
Create an HTML-formatted {duration}-day itinerary for {destination}.

🏨 Hotels:
Start with <h2>Accommodation Options</h2> listing 3 verified hotels.

📅 Daily format:
<h2>Day X: [Title]</h2>
<p><strong>Morning:</strong> Activity</p>
<p><strong>Afternoon:</strong> Activity</p>
<p><strong>Evening:</strong> Activity</p>
<p><strong>Estimated Costs:</strong></p>
<ul>
  <li>Transportation: $X</li>
  <li>Food: $X</li>
  <li>Activities: $X</li>
  <li><strong>Total: $X</strong></li>
</ul>

📚 Suggestions & Resources Section:
If activities, restaurants, or experiences are missing → include fallback blog links (1 per category max) in a final section.

<h2>Suggestions & Resources</h2>
<ul>
  <li><strong>[Category]:</strong> <a href="URL" target="_blank" rel="noopener noreferrer">Blog Title</a></li>
</ul>

💡 CATEGORY VALIDATION:
Only assign a blog to a category if:
- Cultural: mentions museums, history, art
- Food & Dining: includes "restaurants," "eateries"
- Nightlife: mentions bars, clubs
- Outdoors: mentions parks, nature, hiking
- Family-Friendly: says "with kids," "child-friendly"

🎨 Style (HTML):
Insert in <head>:
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
            expected_output="Clean HTML itinerary with blog fallbacks grouped at the end"
        )

        return Crew(
            agents=[researcher, reviewer, planner],
            tasks=[research_task, review_task, planning_task],
            process="sequential",
            verbose=True,
        )


# === VALIDATION FUNCTION ===

def validate_itinerary_output(itinerary_text: str, travel_style: str = ""):
    errors = []
    blog_links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', itinerary_text)

    # Validate Suggestions section presence
    if "Suggestions & Resources" not in itinerary_text:
        errors.append("⚠️ Missing Suggestions & Resources section")

    # Check for duplicate blog links
    urls = [url for url, _ in blog_links]
    if len(set(urls)) < len(urls):
        errors.append("⚠️ Duplicate blog URLs found in suggestions")

    # Check for mismatched blog categories
    if travel_style.lower() == "cultural":
        for _, title in blog_links:
            if "outdoor" in title.lower():
                errors.append("❌ Outdoor blog incorrectly labeled as Cultural")
                break

    # Ensure 3 hotel options
    hotel_count = len(re.findall(r'Option \d: ', itinerary_text))
    if hotel_count != 3:
        errors.append(f"⚠️ Found {hotel_count} hotel options. Expected 3.")

    return "✅ Itinerary passed all checks" if not errors else "\n".join(errors)
