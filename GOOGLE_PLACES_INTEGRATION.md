# Google Places API Integration

This document describes the Google Places API integration for the AI Trip Planner.

## Overview

The Google Places API integration replaces generic web search with verified place data, significantly improving the quality, accuracy, and trustworthiness of travel itinerary results.

## Features

### 1. Verified Places Search
- **Replaces**: Open Web Search
- **Uses**: Google Places Text Search API
- **Returns**: Verified businesses with real addresses, phone numbers, ratings, and Google Maps URLs

### 2. Place Details Enrichment
- **Full name**: Official business name
- **Formatted address**: Complete street address
- **Phone number**: Formatted phone number
- **Website**: Official website URL
- **Google Maps URL**: Direct link to Google Maps
- **Opening hours**: Weekly schedule
- **User rating**: Star rating (0-5)
- **Reviews**: Total review count
- **Business status**: Open/Closed/Permanently Closed

### 3. Quality Filters
- **Rating threshold**: Rejects places with < 3.5 stars
- **Status check**: Rejects permanently closed businesses
- **Review count**: Prioritizes places with multiple reviews
- **Address validation**: Ensures formatted addresses exist

### 4. Autocomplete API
- **Purpose**: Help interpret vague entries or match user-input destinations exactly
- **Use case**: Resolve ambiguous location names (e.g., "TC Michigan" → "Traverse City, Michigan")
- **Endpoint**: `/api/autocomplete`

## Implementation

### Files Created

1. **`backend/src/trip_planner/google_places.py`**
   - Core Google Places API wrapper
   - `GooglePlacesAPI` class with methods:
     - `text_search()`: Search for places
     - `get_place_details()`: Get detailed place information
     - `autocomplete()`: Autocomplete destination names
     - `search_nearby()`: Search places near a location

2. **`backend/src/trip_planner/google_places_tools.py`**
   - CrewAI-compatible tools:
     - `GooglePlacesSearchTool`: Search verified places
     - `GooglePlaceDetailsTool`: Get place details
     - `GooglePlacesAutocompleteTool`: Autocomplete destinations

### Files Modified

1. **`backend/src/trip_planner/crew.py`**
   - Updated agents to use Google Places tools
   - **Researcher Agent**: Prioritizes Google Places, falls back to web search for blogs
   - **Reviewer Agent**: Validates places using Google Places API
   - **Planner Agent**: Uses Google Maps URLs and verified addresses
   - Updated task descriptions with Google Places instructions
   - Enhanced validator to check for Google Maps URLs

2. **`backend/main.py`**
   - Added `/api/autocomplete` endpoint
   - Updated environment variable validation
   - Added `AutocompleteRequest` model

## Agent Workflow

### Research Agent
1. **Primary**: Use "Search Verified Places" tool with Google Places API
   - Restaurants: `place_type="restaurant"`
   - Attractions: `place_type="tourist_attraction"`
   - Hotels: `place_type="lodging"`
2. **Enrichment**: Use "Get Place Details" tool for each place
3. **Fallback**: Use web search only for travel blogs if no verified places found

### Review Agent
1. Verify each place using "Get Place Details" tool
2. Reject places with:
   - Rating < 3.5 stars
   - Business status: "CLOSED_PERMANENTLY"
   - Missing Google Maps URL
   - Generic/placeholder names
3. Ensure 3 verified hotels with valid data

### Planner Agent
1. Format verified Google Places data into HTML
2. Use Google Maps URLs from Place Details
3. Include ratings, addresses, and review counts
4. Only use web search results for blog fallbacks

## Environment Variables

Add to your `.env` file:

```bash
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
```

**Note**: Google Places API key is optional. If not provided, the system will fall back to web search (SerperDevTool).

## API Endpoints

### POST `/api/autocomplete`

Autocomplete destination names using Google Places API.

**Request:**
```json
{
  "input_text": "Traverse City",
  "location": "Michigan, USA"  // Optional
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "description": "Traverse City, MI, USA",
      "place_id": "ChIJ...",
      "types": ["locality", "political"]
    }
  ],
  "input_text": "Traverse City"
}
```

## Benefits

1. **Accuracy**: Verified business data from Google's database
2. **Trustworthiness**: Real addresses, phone numbers, and ratings
3. **User Experience**: Direct Google Maps links for navigation
4. **Quality Control**: Automatic filtering of closed or low-rated places
5. **Reliability**: No fake or placeholder business names

## Fallback Behavior

If `GOOGLE_PLACES_API_KEY` is not set:
- System falls back to SerperDevTool (web search)
- All existing functionality continues to work
- Warning message logged at startup

## Testing

To test the integration:

1. Set `GOOGLE_PLACES_API_KEY` in your `.env` file
2. Create a trip request with a destination
3. Check logs for Google Places API calls
4. Verify itinerary includes Google Maps URLs and ratings

## Next Steps

1. Add Google Places API key to Railway environment variables
2. Test with various destinations
3. Monitor API usage and costs
4. Consider caching place details to reduce API calls

