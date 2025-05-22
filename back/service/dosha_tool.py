"""
Dosha Tool Module

This module provides a tool for the agent to analyze a user's dosha type
based on their responses to a detailed questionnaire.
"""
import json
from typing import Dict, Any, List, Optional

from langchain.tools import BaseTool
from .dosha_calculator import DoshaCalculator

class DoshaTool(BaseTool):
    """Tool for determining a user's Ayurvedic dosha type."""
    
    name: str = "dosha_calculator"
    description: str = """
    Use this tool when you need to determine a user's Ayurvedic dosha type.
    Input should be a JSON string with the following fields:
    - responses: A dictionary mapping question IDs to the user's responses
    - user_context: (Optional) Additional context about the user
    
    Example input:
    {
        "responses": {
            "body_frame": "thin",
            "skin_type": "dry",
            "energy_level": "variable"
        },
        "user_context": "The user is interested in understanding their Ayurvedic constitution."
    }
    """
    
    def __init__(self, **kwargs):
        """Initialize the dosha tool with a calculator instance.
        
        Args:
            **kwargs: Additional arguments to pass to the parent class
        """
        super().__init__(**kwargs)
        self._calculator = DoshaCalculator()
    
    def _run(self, query: str) -> str:
        """
        Run the dosha calculation tool.
        
        Args:
            query: JSON string containing the user's responses and optional context
            
        Returns:
            str: Formatted analysis of the user's dosha type
        """
        try:
            # Parse the input query as JSON
            params = json.loads(query)
            responses = params.get("responses", {})
            
            if not responses:
                return "Error: No responses provided. Please provide responses to the dosha questionnaire."
            
            # Calculate the dosha
            result = self._calculator.calculate_dosha(responses)
            
            # Format the response
            response = [
                "## Dosha Analysis Results\n",
                f"### Primary Dosha: {result['primary_dosha']} (Confidence: {result['confidence']*100:.1f}%)\n",
                result["analysis"]["overall"],
                "\n### Detailed Analysis"
            ]
            
            # Add category-specific analysis
            for category, analysis in result["analysis"].items():
                if category != "overall":
                    response.append(f"\n**{category.capitalize()}:** {analysis}")
            
            # Add recommendations
            if result["recommendations"]:
                response.append("\n\n### Recommendations for Balance\n")
                response.extend([f"- {rec}" if not rec.startswith("**") else rec for rec in result["recommendations"]])
            
            # Add a note about consulting a professional
            response.append(
                "\n\n*Note: This is a preliminary analysis. For a complete assessment "
                "and personalized recommendations, please consult with an Ayurvedic practitioner.*"
            )
            
            return "\n".join(response)
            
        except json.JSONDecodeError:
            return "Error: Invalid JSON input. Please provide a valid JSON string with the required fields."
        except Exception as e:
            return f"Error calculating dosha: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version of the run method."""
        # For simplicity, we'll just call the sync version
        # In a real implementation, you might want to make this truly async
        return self._run(query)

    def get_questionnaire(self) -> List[Dict[str, Any]]:
        """
        Get the list of questions for the dosha assessment.
        
        Returns:
            List of question dictionaries with id, text, options, and category
        """
        return self._calculator.get_questionnaire()

    @property
    def calculator(self) -> DoshaCalculator:
        """Get the underlying DoshaCalculator instance."""
        return self._calculator

# Create a default instance for easy importing
dosha_tool = DoshaTool()
