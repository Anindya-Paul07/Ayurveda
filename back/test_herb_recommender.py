"""
Test script for HerbRecommender
"""
import os
import sys
import json
from service.herb_recommender import HerbRecommender

def test_herb_recommender():
    """Test the HerbRecommender with sample input."""
    # Initialize the recommender
    recommender = HerbRecommender()
    
    # Test input
    test_input = {
        "symptoms": ["indigestion", "bloating"],
        "dosha": "Pitta",
        "current_ailments": ["acid reflux"],
        "contraindications": ["pregnancy"]
    }
    
    # Get recommendations
    result = recommender._run(json.dumps(test_input))
    
    # Print results
    print("Test Results:")
    print("-" * 50)
    print(f"Input: {json.dumps(test_input, indent=2)}")
    print("\nOutput:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    # Add the current directory to the path so we can import from service
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_herb_recommender()
