"""
Herb Recommender Tool

This module provides the HerbRecommender tool for suggesting Ayurvedic herbs
based on symptoms, dosha type, and other health parameters.
"""

import json
from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from .recommendation_service import get_recommendations


class HerbRecommender(BaseTool):
    """Tool for recommending Ayurvedic herbs and formulations.
    
    This tool provides personalized herb recommendations based on dosha, symptoms,
    health concerns, and other Ayurvedic parameters.
    """
    name: str = "herb_recommender"
    description: str = """
    Use this tool to get personalized Ayurvedic herb recommendations.
    
    Input should be a JSON string with any of these optional parameters:
    - symptoms: List of symptoms or health concerns
    - dosha: User's dosha type (Vata, Pitta, Kapha, or combination)
    - current_ailments: Any current health issues
    - season: Current season (e.g., 'summer', 'winter')
    - contraindications: Any known allergies or conditions to avoid
    
    Example input:
    {
        "symptoms": ["indigestion", "bloating"],
        "dosha": "Pitta",
        "current_ailments": ["acid reflux"],
        "contraindications": ["pregnancy"]
    }
    """
    
    def _run(self, query: str) -> Dict[str, Any]:
        """Run the tool synchronously.
        
        Args:
            query: JSON string containing the input parameters
            
        Returns:
            Dict containing herb recommendations or error message
        """
        try:
            # Parse the input query
            try:
                params = json.loads(query)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON input. Please provide a valid JSON object."}
            
            # Extract parameters with defaults
            symptoms = params.get('symptoms', [])
            dosha = params.get('dosha')
            health_concern = ', '.join(params.get('current_ailments', []))
            season = params.get('season')
            
            # Generate recommendations
            recommendations = get_recommendations(
                query=' '.join(symptoms) if symptoms else None,
                dosha=dosha,
                health_concern=health_concern if health_concern else None,
                season=season,
                top_k=5
            )
            
            # Filter based on contraindications if any
            contraindications = params.get('contraindications', [])
            if contraindications:
                recommendations = [
                    rec for rec in recommendations 
                    if not any(contra.lower() in rec.get('content', '').lower() 
                             for contra in contraindications)
                ]
            
            return {
                "recommendations": recommendations,
                "parameters": {
                    "symptoms": symptoms,
                    "dosha": dosha,
                    "season": season
                }
            }
            
        except Exception as e:
            return {"error": f"Error generating herb recommendations: {str(e)}"}
    
    async def _arun(self, query: str) -> Dict[str, Any]:
        """Run the tool asynchronously.
        
        Args:
            query: JSON string containing the input parameters
            
        Returns:
            Dict containing herb recommendations or error message
        """
        # For now, just call the synchronous version
        return self._run(query)
