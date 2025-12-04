"""
CrewAI Tools for Google Places API Integration
"""

from crewai_tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from .google_places import GooglePlacesAPI, PlaceDetails, format_place_for_itinerary
import json


class GooglePlacesSearchInput(BaseModel):
    """Input schema for Google Places search tool"""
    query: str = Field(..., description="Search query for places (e.g., 'restaurants in Traverse City')")
    location: Optional[str] = Field(None, description="Location context (e.g., 'Traverse City, Michigan')")
    place_type: Optional[str] = Field(None, description="Type filter: restaurant, tourist_attraction, lodging, etc.")
    max_results: int = Field(5, description="Maximum number of results to return")


class GooglePlacesSearchTool(BaseTool):
    """Tool for searching verified places using Google Places API"""
    
    name: str = "Search Verified Places"
    description: str = """
    Search for verified restaurants, attractions, and hotels using Google Places API.
    Returns verified place information including:
    - Name and formatted address
    - Phone number and website
    - Google Maps URL
    - Rating and review count
    - Business status (open/closed)
    - Opening hours
    
    Use this instead of web search for finding real businesses and attractions.
    """
    args_schema: Type[BaseModel] = GooglePlacesSearchInput
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.places_api = GooglePlacesAPI(api_key=api_key)
    
    def _run(self, query: str, location: Optional[str] = None, 
            place_type: Optional[str] = None, max_results: int = 5) -> str:
        """
        Execute the search and return formatted results
        """
        try:
            places = self.places_api.text_search(
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
                    "phone": place.phone_number
                }
                results.append(result)
            
            return json.dumps(results, indent=2)
            
        except Exception as e:
            return f"Error searching places: {str(e)}"


class GooglePlacesAutocompleteInput(BaseModel):
    """Input schema for Google Places autocomplete tool"""
    input_text: str = Field(..., description="User input text to autocomplete (e.g., 'Traverse City' or 'TC Michigan')")
    location: Optional[str] = Field(None, description="Optional location bias for better results")


class GooglePlacesAutocompleteTool(BaseTool):
    """Tool for autocompleting destination names using Google Places API"""
    
    name: str = "Autocomplete Destination"
    description: str = """
    Use Google Places Autocomplete API to interpret vague entries or match user-input destinations exactly.
    Helps resolve ambiguous location names to verified places.
    """
    args_schema: Type[BaseModel] = GooglePlacesAutocompleteInput
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.places_api = GooglePlacesAPI(api_key=api_key)
    
    def _run(self, input_text: str, location: Optional[str] = None) -> str:
        """
        Execute autocomplete and return suggestions
        """
        try:
            suggestions = self.places_api.autocomplete(
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


class GooglePlaceDetailsInput(BaseModel):
    """Input schema for getting place details"""
    place_id: str = Field(..., description="Google Place ID to get details for")


class GooglePlaceDetailsTool(BaseTool):
    """Tool for getting detailed information about a specific place"""
    
    name: str = "Get Place Details"
    description: str = """
    Get comprehensive details about a specific place using its Google Place ID.
    Returns full information including address, phone, website, rating, reviews, and opening hours.
    """
    args_schema: Type[BaseModel] = GooglePlaceDetailsInput
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.places_api = GooglePlacesAPI(api_key=api_key)
    
    def _run(self, place_id: str) -> str:
        """
        Get place details and return formatted result
        """
        try:
            place = self.places_api.get_place_details(place_id)
            
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
                "types": place.types
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error getting place details: {str(e)}"

