"""
CrewAI Tools for Google Places API Integration
"""

from crewai.tools import tool
from typing import Optional
from .google_places import GooglePlacesAPI, PlaceDetails, format_place_for_itinerary
import json
import os


@tool("Search Verified Places")
def google_places_search_tool(
    query: str,
    location: Optional[str] = None,
    place_type: Optional[str] = None,
    max_results: int = 5
) -> str:
    """
    Search for verified restaurants, attractions, and hotels using Google Places API.
    Returns verified place information including:
    - Name and formatted address
    - Phone number and website
    - Google Maps URL
    - Rating and review count
    - Business status (open/closed)
    - Opening hours
    
    Use this instead of web search for finding real businesses and attractions.
    
    Args:
        query: Search query for places (e.g., 'restaurants in Traverse City')
        location: Optional location context (e.g., 'Traverse City, Michigan')
        place_type: Optional type filter: restaurant, tourist_attraction, lodging, etc.
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        JSON string with verified place information
    """
    try:
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            return "Google Places API key not configured. Please set GOOGLE_PLACES_API_KEY environment variable."
        
        places_api = GooglePlacesAPI(api_key=api_key)
        places = places_api.text_search(
            query=query,
            location=location,
            type_filter=place_type,
            max_results=max_results
        )
        
        if not places:
            return "No verified places found matching your search."
        
        results = []
        for place in places:
            result = {
                "name": place.name,
                "address": place.formatted_address,
                "rating": place.rating,
                "reviews": place.user_ratings_total,
                "status": place.business_status,
                "maps_url": place.google_maps_url,
                "website": place.website,
                "phone": place.phone_number,
                "place_id": place.place_id,  # Include place_id for debugging
                "types": place.types  # Include types for debugging
            }
            results.append(result)
            
            # Log the URL being returned to the agent
            print(f"[Google Places Tool] 📍 Returning place: {place.name}")
            print(f"  Place ID: {place.place_id}")
            print(f"  Maps URL: {place.google_maps_url}")
            print(f"  Types: {', '.join(place.types[:3]) if place.types else 'N/A'}")
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        return f"Error searching places: {str(e)}"


@tool("Autocomplete Destination")
def google_places_autocomplete_tool(
    input_text: str,
    location: Optional[str] = None
) -> str:
    """
    Use Google Places Autocomplete API to interpret vague entries or match user-input destinations exactly.
    Helps resolve ambiguous location names to verified places.
    
    Args:
        input_text: User input text to autocomplete (e.g., 'Traverse City' or 'TC Michigan')
        location: Optional location bias for better results
    
    Returns:
        JSON string with autocomplete suggestions
    """
    try:
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            return "Google Places API key not configured. Please set GOOGLE_PLACES_API_KEY environment variable."
        
        places_api = GooglePlacesAPI(api_key=api_key)
        suggestions = places_api.autocomplete(
            input_text=input_text,
            location=location
        )
        
        if not suggestions:
            return f"No suggestions found for '{input_text}'"
        
        results = []
        for suggestion in suggestions:
            results.append({
                "description": suggestion["description"],
                "place_id": suggestion["place_id"],
                "types": suggestion.get("types", [])
            })
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        return f"Error autocompleting: {str(e)}"


@tool("Get Place Details")
def google_place_details_tool(place_id: str) -> str:
    """
    Get comprehensive details about a specific place using its Google Place ID.
    Returns full information including address, phone, website, rating, reviews, and opening hours.
    
    Args:
        place_id: Google Place ID to get details for
    
    Returns:
        JSON string with place details
    """
    try:
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            return "Google Places API key not configured. Please set GOOGLE_PLACES_API_KEY environment variable."
        
        places_api = GooglePlacesAPI(api_key=api_key)
        place = places_api.get_place_details(place_id)
        
        if not place:
            return f"No details found for place ID: {place_id}"
        
        result = {
            "name": place.name,
            "address": place.formatted_address,
            "phone": place.phone_number,
            "website": place.website,
            "maps_url": place.google_maps_url,
            "rating": place.rating,
            "reviews": place.user_ratings_total,
            "status": place.business_status,
            "opening_hours": place.opening_hours,
            "types": place.types,
            "place_id": place.place_id  # Include place_id for debugging
        }
        
        # Log the details being returned
        print(f"[Google Places Tool] 📍 Place Details Retrieved:")
        print(f"  Name: {place.name}")
        print(f"  Place ID: {place.place_id}")
        print(f"  Maps URL: {place.google_maps_url}")
        print(f"  Types: {', '.join(place.types[:5]) if place.types else 'N/A'}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error getting place details: {str(e)}"

