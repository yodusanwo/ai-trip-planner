#!/usr/bin/env python3
"""
Test script to run the full CrewAI flow locally and check URLs in output.
This helps diagnose if the agent is modifying URLs.

Usage:
    python test_local_crew.py
"""

import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
backend_dir = Path(__file__).parent
load_dotenv(dotenv_path=backend_dir / '.env')
load_dotenv(dotenv_path=backend_dir.parent / '.env', override=False)

# Add src to path
sys.path.insert(0, str(backend_dir))

from src.trip_planner.crew import TripPlanner

def extract_urls_from_html(html_content: str):
    """Extract and analyze URLs from HTML"""
    url_pattern = r'href="([^"]+)"'
    all_urls = re.findall(url_pattern, html_content)
    google_maps_urls = [url for url in all_urls if "google.com/maps" in url]
    
    print(f"\n🔗 URL Analysis:")
    print(f"  Total links: {len(all_urls)}")
    print(f"  Google Maps links: {len(google_maps_urls)}")
    
    # Check for problematic places
    problematic_places = {
        "Musée d'Orsay": ["musée", "d'orsay", "orsay"],
        "Louvre Museum": ["louvre"],
        "Galeries Lafayette": ["galeries", "lafayette"],
        "Jardin du Luxembourg": ["jardin", "luxembourg"]
    }
    
    for place_name, keywords in problematic_places.items():
        place_pattern = r'(?i)(' + '|'.join(keywords) + r')[^<]*<a[^>]+href="([^"]+)"'
        matches = re.findall(place_pattern, html_content)
        if matches:
            for match in matches[:2]:
                url = match[1] if isinstance(match, tuple) else match
                print(f"  📍 {place_name}: {url}")
                if "query_place_id" not in url:
                    print(f"    ⚠️ Missing query_place_id")
                if "maps.google.com/?cid=" in url:
                    print(f"    ❌ Using CID format")
    
    # Show sample URLs
    if google_maps_urls:
        print(f"\n  Sample URLs (first 5):")
        for url in google_maps_urls[:5]:
            print(f"    - {url}")
            if "query_place_id" not in url:
                print(f"      ⚠️ Missing query_place_id")
    
    return google_maps_urls


def test_crew_execution():
    """Test the full CrewAI execution locally"""
    print("🧪 Testing CrewAI Execution Locally")
    print("=" * 60)
    
    # Check environment variables
    if not os.getenv("GOOGLE_PLACES_API_KEY"):
        print("⚠️  WARNING: GOOGLE_PLACES_API_KEY not set")
        print("   Google Places integration will be disabled")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not set")
        return False
    
    if not os.getenv("SERPER_API_KEY"):
        print("❌ ERROR: SERPER_API_KEY not set")
        return False
    
    # Create trip planner
    trip_planner = TripPlanner()
    crew = trip_planner.crew()
    
    # Test inputs (short trip for faster testing)
    inputs = {
        "destination": "Paris, France",
        "duration": 3,  # Short trip for testing
        "budget": "moderate",
        "travel_style": "Cultural",
        "special_requirements": ""
    }
    
    print(f"\n📋 Test Inputs:")
    print(f"  Destination: {inputs['destination']}")
    print(f"  Duration: {inputs['duration']} days")
    print(f"  Travel Style: {inputs['travel_style']}")
    print()
    
    print("🚀 Running CrewAI...")
    print("   (This may take a few minutes)")
    print()
    
    try:
        # Run the crew
        result = crew.run(inputs=inputs)
        
        # Extract HTML from result
        html_content = None
        
        if hasattr(result, 'tasks_output') and result.tasks_output:
            for task_output in reversed(result.tasks_output):
                output_str = str(task_output.raw) if hasattr(task_output, 'raw') else str(task_output)
                if output_str and len(output_str) > 100:
                    html_content = output_str
                    break
        elif hasattr(result, 'raw'):
            html_content = str(result.raw)
        elif hasattr(result, 'output'):
            html_content = str(result.output)
        else:
            html_content = str(result)
        
        if not html_content or len(html_content) < 100:
            print("❌ ERROR: No HTML content found in result")
            print(f"   Result type: {type(result)}")
            print(f"   Result: {result}")
            return False
        
        # Clean HTML
        html_content = html_content.strip()
        if html_content.startswith('```html'):
            html_content = html_content[7:]
        if html_content.startswith('```'):
            html_content = html_content[3:]
        if html_content.endswith('```'):
            html_content = html_content[:-3]
        html_content = html_content.strip()
        
        print(f"✅ CrewAI execution completed")
        print(f"   HTML length: {len(html_content)} characters")
        print()
        
        # Extract and analyze URLs
        urls = extract_urls_from_html(html_content)
        
        # Save HTML to file for inspection
        output_file = backend_dir / "test_output.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n💾 HTML saved to: {output_file}")
        print(f"   Open this file in a browser to see the result")
        
        # Validate URLs
        issues_found = False
        for url in urls:
            if "query_place_id" not in url:
                issues_found = True
            if "maps.google.com/?cid=" in url:
                issues_found = True
        
        if issues_found:
            print("\n⚠️  WARNING: Some URLs have issues")
            print("   Check the URL analysis above")
        else:
            print("\n✅ All URLs look correct!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Local CrewAI Test Script")
    print("=" * 60)
    print()
    print("This script will:")
    print("1. Run the full CrewAI flow locally")
    print("2. Extract and analyze URLs from the output")
    print("3. Check for problematic places")
    print("4. Save HTML output for inspection")
    print()
    
    success = test_crew_execution()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed!")
    else:
        print("❌ Test failed. Check errors above.")
    
    sys.exit(0 if success else 1)

