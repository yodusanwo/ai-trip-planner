#!/usr/bin/env python3
"""
Test script to verify Google Maps URL generation for specific places.
Run this locally to diagnose URL issues without deploying.

Usage:
    python test_urls.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
backend_dir = Path(__file__).parent
load_dotenv(dotenv_path=backend_dir / '.env')
load_dotenv(dotenv_path=backend_dir.parent / '.env', override=False)

# Add src to path
sys.path.insert(0, str(backend_dir))

from src.trip_planner.google_places import GooglePlacesAPI

# Places to test
TEST_PLACES = [
    "Musée d'Orsay",
    "Louvre Museum",
    "Galeries Lafayette",
    "Jardin du Luxembourg",
    "Eiffel Tower",
    "Arc de Triomphe",
]

def test_place_urls():
    """Test URL generation for specific places"""
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_PLACES_API_KEY not found in environment")
        print("   Please set it in your .env file")
        return False
    
    print("🔍 Testing Google Places URL Generation")
    print("=" * 60)
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    print()
    
    places_api = GooglePlacesAPI(api_key=api_key)
    
    all_passed = True
    
    for place_name in TEST_PLACES:
        print(f"\n📍 Testing: {place_name}")
        print("-" * 60)
        
        try:
            # Search for the place
            places = places_api.text_search(
                query=f"{place_name} Paris",
                location="Paris, France",
                max_results=1
            )
            
            if not places:
                print(f"  ❌ No results found for {place_name}")
                all_passed = False
                continue
            
            place = places[0]
            
            print(f"  ✅ Found: {place.name}")
            print(f"  Place ID: {place.place_id}")
            print(f"  Address: {place.formatted_address}")
            print(f"  Rating: {place.rating}/5 ({place.user_ratings_total} reviews)")
            print(f"  Types: {', '.join(place.types[:5])}")
            
            # Check URL
            if not place.google_maps_url:
                print(f"  ❌ ERROR: No Google Maps URL generated!")
                all_passed = False
                continue
            
            print(f"  🔗 Generated URL: {place.google_maps_url}")
            
            # Validate URL format
            issues = []
            if "query_place_id" not in place.google_maps_url:
                issues.append("Missing query_place_id parameter")
            if "maps.google.com/?cid=" in place.google_maps_url:
                issues.append("Using unreliable CID format")
            if "maps/search" not in place.google_maps_url and "maps/place" not in place.google_maps_url:
                issues.append("Unexpected URL format")
            if place.place_id not in place.google_maps_url:
                issues.append("Place ID not in URL")
            
            if issues:
                print(f"  ⚠️  URL Issues:")
                for issue in issues:
                    print(f"     - {issue}")
                all_passed = False
            else:
                print(f"  ✅ URL format looks correct")
            
            # Test URL length (should be reasonable)
            if len(place.google_maps_url) < 50:
                print(f"  ⚠️  WARNING: URL seems too short ({len(place.google_maps_url)} chars)")
                all_passed = False
            elif len(place.google_maps_url) > 500:
                print(f"  ⚠️  WARNING: URL seems too long ({len(place.google_maps_url)} chars)")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check the issues above.")
    
    return all_passed


def test_specific_place_ids():
    """Test specific place IDs that are known to have issues"""
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_PLACES_API_KEY not found")
        return False
    
    places_api = GooglePlacesAPI(api_key=api_key)
    
    # You can add specific place IDs here if you know them
    # Example: test_place_ids = ["ChIJ...", "ChIJ..."]
    test_place_ids = []
    
    if not test_place_ids:
        print("ℹ️  No specific place IDs to test")
        return True
    
    print("\n🔍 Testing Specific Place IDs")
    print("=" * 60)
    
    for place_id in test_place_ids:
        print(f"\n📍 Place ID: {place_id}")
        try:
            place = places_api.get_place_details(place_id)
            if place:
                print(f"  Name: {place.name}")
                print(f"  URL: {place.google_maps_url}")
            else:
                print(f"  ❌ Failed to get details")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return True


if __name__ == "__main__":
    print("Google Places URL Test Script")
    print("=" * 60)
    print()
    
    # Test URL generation
    success = test_place_urls()
    
    # Test specific place IDs if needed
    test_specific_place_ids()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print()
    print("Next steps:")
    print("1. Check the URLs above - they should all have query_place_id")
    print("2. Try opening the URLs in a browser to verify they work")
    print("3. Compare URLs from logs with URLs generated here")
    print("4. If URLs are correct here but wrong in production, check agent instructions")
    
    sys.exit(0 if success else 1)

