from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from .google_places_tools import (
    google_places_search_tool,
    google_place_details_tool,
    google_places_autocomplete_tool
)
import requests
import re
import os
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
        # Initialize Google Places API tools
        google_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        
        # Primary tools: Google Places (verified places)
        # These are function-based tools created with @tool decorator
        places_tools = []
        if google_api_key:
            places_tools = [
                google_places_search_tool,
                google_place_details_tool,
                google_places_autocomplete_tool
            ]
        
        # Fallback tool: SerperDevTool (for blogs and general web search)
        web_search_tool = SerperDevTool()
        
        # Combine tools - prioritize Google Places, fallback to web search
        researcher_tools = places_tools + [web_search_tool] if places_tools else [web_search_tool]
        reviewer_tools = places_tools + [web_search_tool] if places_tools else [web_search_tool]
        planner_tools = places_tools + [web_search_tool] if places_tools else [web_search_tool]

        # ---------------------
        # Agents
        # ---------------------
        researcher = Agent(
            role="Verified Travel Researcher",
            goal="Gather real, verified travel listings using Google Places API. Prioritize verified businesses with ratings and reviews. Use web search only for travel blogs as fallback.",
            backstory="You find reliable listings using Google Places API which provides verified businesses with real addresses, phone numbers, ratings, and Google Maps links. You prioritize places with good ratings (4.0+) and multiple reviews. Only use web search for finding travel blog articles when specific places aren't available.",
            tools=researcher_tools,
            verbose=True,
            allow_delegation=False,
        )

        reviewer = Agent(
            role="Travel Accuracy Auditor",
            goal="Verify all places using Google Places API. Reject places with bad ratings (<3.5), closed status, or missing critical information. Ensure all places have valid Google Maps URLs.",
            backstory="You audit listings using Google Places API to verify business status, ratings, and availability. You reject places that are permanently closed, have poor ratings, or lack essential information. You ensure all places have valid Google Maps URLs for user navigation.",
            tools=reviewer_tools,
            verbose=True,
            allow_delegation=False,
        )

        planner = Agent(
            role="Clean Itinerary Formatter",
            goal="Generate a structured HTML itinerary using verified Google Places data. Always use Google Maps URLs from Place Details. Include ratings and addresses from verified sources.",
            backstory="You format verified place information into clean HTML itineraries. You use Google Maps URLs and formatted addresses from Google Places API. You include ratings and review counts to help users make informed decisions. Only use web search results for travel blog fallbacks.",
            tools=planner_tools,
            verbose=True,
            allow_delegation=False,
        )

        # ---------------------
        # Tasks
        # ---------------------
        research_task = Task(
            description="""
Research {destination} for a {duration}-day {travel_style}-style trip.

🔍 TOOL USAGE PRIORITY:
1. FIRST: Use "Search Verified Places" tool with Google Places API
   - For restaurants: query="restaurants in {destination}", place_type="restaurant"
   - For attractions: query="tourist attractions in {destination}", place_type="tourist_attraction"
   - For hotels: query="hotels in {destination}", place_type="lodging"
   - Always include location="{destination}" parameter

2. THEN: Use "Get Place Details" tool to enrich results with:
   - Full address, phone, website
   - Google Maps URL
   - Rating and review count
   - Opening hours
   - Business status

3. FALLBACK: Use web search ONLY for travel blogs if no verified places found

✅ Find verified listings:
- Restaurants: Use Google Places, prioritize 4.0+ ratings, 50+ reviews
- Attractions: Use Google Places, prioritize 4.0+ ratings
- Hotels: Use Google Places, find 3 options with different price ranges

❌ REJECT places with:
- Rating < 3.5 stars
- Business status: "CLOSED_PERMANENTLY"
- Missing Google Maps URL
- Placeholders like 'Detroit Market', 'local café'

📚 If no verified places found, use web search for travel blogs:
- One blog per category only
- Must be full article (not homepage)
""",
            agent=researcher,
            expected_output="Verified Google Places listings with ratings, addresses, and Maps URLs + fallback blog links (if needed)"
        )

        review_task = Task(
            description="""
Validate listings for: {destination} using Google Places API.

🔍 VALIDATION STEPS:
1. Use "Get Place Details" tool to verify each place:
   - Check business_status: REJECT if "CLOSED_PERMANENTLY"
   - Check rating: REJECT if < 3.5 stars
   - Verify Google Maps URL exists
   - Ensure formatted_address is present

2. Check for invalid names:
   - Reject generic names like 'local eatery', 'Detroit Market'
   - Reject placeholders without real addresses

3. Ensure 3 verified hotels with:
   - Valid Google Maps URLs
   - Ratings 3.5+ stars
   - Business status: "OPERATIONAL"

4. Validate all URLs:
   - Google Maps URLs must be from Google Places API
   - Website URLs must return status 200

5. Limit blogs to 1 per category (only if no verified places available)

If any place fails validation → remove and find replacement using Google Places API.
""",
            agent=reviewer,
            expected_output="Validated Google Places listings with verified status, ratings, and Maps URLs"
        )

        planning_task = Task(
            description="""
Using verified Google Places research only, create a {duration}-day itinerary for {destination}.

🔴 CRITICAL: URL COPYING RULES
- The research data contains a "maps_url" field for each place in JSON format
- You MUST copy the EXACT URL from the "maps_url" field - do NOT modify, shorten, or reconstruct it
- Each place has a unique "maps_url" - match the place name to its exact "maps_url" from the research
- Example JSON structure from research:
  {
    "name": "Musée d'Orsay",
    "address": "1 Rue de la Légion d'Honneur, 75007 Paris, France",
    "maps_url": "https://www.google.com/maps/search/?api=1&query=Musée+d'Orsay&query_place_id=ChIJ...",
    "rating": 4.8,
    "reviews": 85771
  }
- When creating the HTML, copy the EXACT "maps_url" value: "https://www.google.com/maps/search/?api=1&query=Musée+d'Orsay&query_place_id=ChIJ..."
- NEVER create your own URLs or use placeholders
- NEVER reuse a URL from a different place
- NEVER modify the URL (don't remove parameters, don't shorten it, don't change the format)

🏨 Section: <h2>Accommodation Options</h2>
List 3 hotel options from Google Places:
- Name (copy exactly from research "name" field)
- Formatted address (copy exactly from research "address" field)
- Rating: ⭐ X.X/5 (X reviews) - copy from research "rating" and "reviews" fields
- Hyperlink: Copy the EXACT URL from research "maps_url" field
  Format: <a href="[EXACT maps_url FROM RESEARCH]" target="_blank" rel="noopener noreferrer">View on Google Maps</a>

📅 Daily Structure (MUST follow this exact format for ALL days):
<h2>Day X: [Theme]</h2>
<p><strong>Morning:</strong> Visit <a href="[EXACT maps_url FROM RESEARCH FOR THIS PLACE]" target="_blank">[Place Name]</a> - [Address] ⭐ [Rating]/5 ([Review Count] reviews)</p>
<p><strong>Afternoon:</strong> Explore <a href="[EXACT maps_url FROM RESEARCH FOR THIS PLACE]" target="_blank">[Attraction Name]</a> - [Address] ⭐ [Rating]/5 ([Review Count] reviews)</p>
<p><strong>Evening:</strong> Dinner at <a href="[EXACT maps_url FROM RESEARCH FOR THIS PLACE]" target="_blank">[Restaurant Name]</a> - [Address] ⭐ [Rating]/5 ([Review Count] reviews)</p>

🔴 CRITICAL RULES:
1. Copy the EXACT "maps_url" from research - do NOT modify it
2. Match each place name to its corresponding "maps_url" from the research JSON
3. Verify URL-place name match: If place is "Musée d'Orsay", find "Musée d'Orsay" in research and copy its exact "maps_url"
4. Each place MUST have its OWN unique Google Maps URL - NEVER reuse a URL from a different place
5. Maintain proper HTML structure: Each day must have exactly 3 paragraphs (Morning, Afternoon, Evening)
6. Keep days in sequential order (Day 1, Day 2, Day 3... Day {duration})
7. Each place must appear only once per itinerary (no duplicates)

✅ REQUIRED for each place:
- Copy EXACT "maps_url" from research (do not modify or reconstruct)
- Copy exact "name" from research
- Copy exact "address" from research
- Copy exact "rating" and "reviews" from research

⚠️ Do NOT:
- Modify, shorten, or reconstruct URLs - copy them exactly as provided
- Reuse Google Maps URLs from different places
- Use Conciergerie's URL for Musée d'Orsay (or any other place)
- Mix up place names with wrong URLs
- Create malformed HTML (broken tags, wrong order)
- Include generic names like "local bistro", "Detroit Market"
- Include unlinked place names
- Use URLs not from Google Places API research
- Include places without addresses

📚 Fallbacks (only if no verified places available):
<h2>Suggestions & Resources</h2>
<ul>
  <li><strong>[Category]:</strong> <a href="VALID_URL" target="_blank" rel="noopener noreferrer">[Blog Title]</a> – Short description</li>
</ul>

✅ One blog per category only.

🔍 Before finalizing, verify:
- Each place name has its correct, unique Google Maps URL
- No URL is used twice for different places
- HTML structure is valid and properly formatted
- All days are complete with Morning, Afternoon, and Evening activities
""",
            agent=planner,
            expected_output="HTML-formatted itinerary with unique Google Maps URLs (one per place), addresses, and ratings from verified Google Places data"
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
    google_maps_count = 0
    google_maps_urls = []
    
    for url in links:
        # Prefer Google Maps URLs (they're always valid)
        if "maps.google.com" in url or "google.com/maps" in url:
            google_maps_count += 1
            google_maps_urls.append(url)
        elif not is_valid_url(url):
            errors.append(f"❌ Broken or invalid URL: {url}")
    
    # Check for duplicate Google Maps URLs (indicates URL reuse)
    if len(google_maps_urls) > len(set(google_maps_urls)):
        duplicates = [url for url in set(google_maps_urls) if google_maps_urls.count(url) > 1]
        errors.append(f"⚠️ Duplicate Google Maps URLs detected: {len(duplicates)} URL(s) used for multiple places. Each place must have a unique URL.")
    
    # Encourage use of Google Maps URLs
    if google_maps_count == 0 and len(links) > 0:
        errors.append("⚠️ No Google Maps URLs found. Prefer Google Places API URLs for better user experience.")

    # Check blog section duplicates
    if itinerary_text.count("Suggestions & Resources") > 1:
        errors.append("⚠️ Suggestions section appears more than once")

    # Hotel count check
    hotel_count = len(re.findall(r'Option \d:', itinerary_text))
    if hotel_count != 3:
        errors.append(f"⚠️ Found {hotel_count} hotel options. Expected 3.")
    
    # Check HTML structure - ensure proper day formatting
    day_pattern = r'<h2>Day \d+'
    days_found = len(re.findall(day_pattern, itinerary_text))
    if days_found == 0:
        errors.append("⚠️ No day sections found in HTML structure")
    
    # Check for malformed HTML (unclosed tags, broken structure)
    open_p_tags = itinerary_text.count('<p>')
    close_p_tags = itinerary_text.count('</p>')
    if open_p_tags != close_p_tags:
        errors.append(f"⚠️ HTML structure issue: {open_p_tags} opening <p> tags but {close_p_tags} closing </p> tags")

    return "✅ Passed all validation checks" if not errors else "\n".join(errors)
