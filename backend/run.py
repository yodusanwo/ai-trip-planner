"""
Test script to run the TripPlanner crew and validate the output.
This script can be used for local testing and validation.
"""
import os
import sys
from pathlib import Path

# Add src to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=backend_dir / '.env')
load_dotenv(dotenv_path=backend_dir.parent / '.env', override=False)

# Import TripPlanner class and validator
from src.trip_planner.crew import TripPlanner, validate_itinerary_output

def main():
    """Run the trip planner with test variables and validate output."""
    
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        sys.exit(1)
    
    if not os.getenv('SERPER_API_KEY'):
        print("❌ ERROR: SERPER_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        sys.exit(1)
    
    print("🚀 Creating TripPlanner crew...")
    
    # Create the crew
    trip_planner = TripPlanner()
    crew = trip_planner.crew()
    
    # Fill in task variables
    variables = {
        "destination": "Tokyo",
        "duration": 5,
        "budget": "$2500",
        "travel_style": "Family-friendly",
        "special_requirements": "Accessible transport and vegetarian food options"
    }
    
    print(f"\n📍 Planning trip to {variables['destination']} for {variables['duration']} days")
    print(f"💰 Budget: {variables['budget']}")
    print(f"🎯 Style: {variables['travel_style']}")
    print(f"📝 Requirements: {variables['special_requirements']}\n")
    
    print("⏳ Running crew... This may take a few minutes...\n")
    
    try:
        # Run the crew
        result = crew.kickoff(inputs=variables)
        
        # Get output text (handle different CrewAI result formats)
        if hasattr(result, "raw"):
            itinerary_text = result.raw
        elif hasattr(result, "output"):
            itinerary_text = result.output
        elif isinstance(result, dict) and "result" in result:
            itinerary_text = str(result["result"])
        else:
            itinerary_text = str(result)
        
        print("\n" + "="*80)
        print("--- FINAL ITINERARY ---")
        print("="*80 + "\n")
        print(itinerary_text)
        
        print("\n" + "="*80)
        print("--- VALIDATION REPORT ---")
        print("="*80 + "\n")
        
        # Run validation
        validation_result = validate_itinerary_output(itinerary_text)
        print(validation_result)
        
        print("\n" + "="*80)
        print("✅ Trip planning complete!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

