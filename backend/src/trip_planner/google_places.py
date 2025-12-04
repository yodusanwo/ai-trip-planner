"""
Google Places API Integration for Trip Planner

Provides verified place data including:
- Place names, addresses, phone numbers
- Google Maps URLs
- Ratings and reviews
- Opening hours
- Business status
"""

import os
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class PlaceDetails:
    """Structured place information from Google Places API"""
    name: str
    formatted_address: str
    phone_number: Optional[str] = None
    website: Optional[str] = None
    google_maps_url: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    business_status: Optional[str] = None
    opening_hours: Optional[List[str]] = None
    place_id: Optional[str] = None
    types: Optional[List[str]] = None


class GooglePlacesAPI:
    """Wrapper for Google Places API calls"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_PLACES_API_KEY environment variable is required")
        
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def text_search(self, query: str, location: Optional[str] = None, 
                   type_filter: Optional[str] = None, max_results: int = 5) -> List[PlaceDetails]:
        """
        Search for places using Text Search API
        
        Args:
            query: Search query (e.g., "restaurants in Traverse City")
            location: Optional location bias (e.g., "Traverse City, Michigan")
            type_filter: Optional type filter (restaurant, tourist_attraction, lodging, etc.)
            max_results: Maximum number of results to return
        
        Returns:
            List of PlaceDetails objects
        """
        endpoint = f"{self.base_url}/textsearch/json"
        params = {
            "query": query,
            "key": self.api_key,
        }
        
        if location:
            params["location"] = location
        
        if type_filter:
            params["type"] = type_filter
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                print(f"⚠️ Google Places API error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                return []
            
            places = []
            for result in data.get("results", [])[:max_results]:
                place_id = result.get("place_id")
                if place_id:
                    # Get detailed information
                    details = self.get_place_details(place_id)
                    if details:
                        places.append(details)
            
            return places
            
        except requests.RequestException as e:
            print(f"❌ Error calling Google Places API: {e}")
            return []
    
    def get_place_details(self, place_id: str) -> Optional[PlaceDetails]:
        """
        Get detailed information about a place using Place Details API
        
        Args:
            place_id: Google Place ID
        
        Returns:
            PlaceDetails object or None if error
        """
        endpoint = f"{self.base_url}/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,business_status,opening_hours,types,url",
            "key": self.api_key,
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                print(f"⚠️ Place Details API error: {data.get('status')}")
                return None
            
            result = data.get("result", {})
            
            # Extract opening hours
            opening_hours = None
            if "opening_hours" in result:
                opening_hours = result["opening_hours"].get("weekday_text", [])
            
            # Construct proper Google Maps URL using Place ID
            # The API returns CID URLs (maps.google.com/?cid=...) which are unreliable
            # For all place types (businesses, parks, monuments, attractions), use the search format
            # with query_place_id, which is the most reliable method per Google's documentation
            place_name = result.get("name", "")
            formatted_address = result.get("formatted_address", "")
            
            # Use the search format with query_place_id - works for all place types
            # Format: https://www.google.com/maps/search/?api=1&query=PlaceName&query_place_id=PLACE_ID
            # This format is recommended by Google for linking to places using Place IDs
            from urllib.parse import quote_plus
            
            if place_name:
                # Use search format with place name and query_place_id
                # This works reliably for businesses, parks, monuments, attractions, islands, etc.
                encoded_name = quote_plus(place_name)
                proper_maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_name}&query_place_id={place_id}"
            else:
                # Fallback if name is missing - still use query_place_id
                proper_maps_url = f"https://www.google.com/maps/search/?api=1&query_place_id={place_id}"
            
            return PlaceDetails(
                name=place_name,
                formatted_address=formatted_address,
                phone_number=result.get("formatted_phone_number"),
                website=result.get("website"),
                google_maps_url=proper_maps_url,  # Use constructed URL instead of API's CID URL
                rating=result.get("rating"),
                user_ratings_total=result.get("user_ratings_total"),
                business_status=result.get("business_status"),
                opening_hours=opening_hours,
                place_id=place_id,
                types=result.get("types", [])
            )
            
        except requests.RequestException as e:
            print(f"❌ Error getting place details: {e}")
            return None
    
    def autocomplete(self, input_text: str, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Use Autocomplete API to help interpret vague entries or match user-input destinations
        
        Args:
            input_text: User input (e.g., "Traverse City" or "TC Michigan")
            location: Optional location bias
        
        Returns:
            List of autocomplete suggestions with place_id and description
        """
        endpoint = f"{self.base_url}/autocomplete/json"
        params = {
            "input": input_text,
            "key": self.api_key,
        }
        
        if location:
            # Use location bias for better results
            params["location"] = location
            params["radius"] = 50000  # 50km radius
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                print(f"⚠️ Autocomplete API error: {data.get('status')}")
                return []
            
            suggestions = []
            for prediction in data.get("predictions", []):
                suggestions.append({
                    "description": prediction.get("description", ""),
                    "place_id": prediction.get("place_id"),
                    "types": prediction.get("types", [])
                })
            
            return suggestions
            
        except requests.RequestException as e:
            print(f"❌ Error calling Autocomplete API: {e}")
            return []
    
    def search_nearby(self, location: str, radius: int = 5000, 
                     type_filter: Optional[str] = None, keyword: Optional[str] = None) -> List[PlaceDetails]:
        """
        Search for places near a location using Nearby Search API
        
        Args:
            location: Lat,lng coordinates or place name
            radius: Search radius in meters (default 5000m = 5km)
            type_filter: Optional type filter
            keyword: Optional keyword search
        
        Returns:
            List of PlaceDetails objects
        """
        endpoint = f"{self.base_url}/nearbysearch/json"
        params = {
            "location": location,
            "radius": radius,
            "key": self.api_key,
        }
        
        if type_filter:
            params["type"] = type_filter
        
        if keyword:
            params["keyword"] = keyword
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                print(f"⚠️ Nearby Search API error: {data.get('status')}")
                return []
            
            places = []
            for result in data.get("results", []):
                place_id = result.get("place_id")
                if place_id:
                    details = self.get_place_details(place_id)
                    if details:
                        places.append(details)
            
            return places
            
        except requests.RequestException as e:
            print(f"❌ Error calling Nearby Search API: {e}")
            return []


def format_place_for_itinerary(place: PlaceDetails, link_text: Optional[str] = None) -> str:
    """
    Format a PlaceDetails object as HTML for the itinerary
    
    Args:
        place: PlaceDetails object
        link_text: Optional custom link text (defaults to place name)
    
    Returns:
        HTML formatted string
    """
    link_text = link_text or place.name
    url = place.google_maps_url or place.website
    
    if url:
        link = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{link_text}</a>'
    else:
        link = link_text
    
    parts = [link]
    
    if place.formatted_address:
        parts.append(f"<span class='address'>{place.formatted_address}</span>")
    
    if place.rating and place.user_ratings_total:
        parts.append(f"<span class='rating'>⭐ {place.rating}/5 ({place.user_ratings_total} reviews)</span>")
    
    return " - ".join(parts)

