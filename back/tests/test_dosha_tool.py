"""
Tests for the DoshaTool class.
"""
import unittest
import json
from back.service.dosha_tool import DoshaTool

class TestDoshaTool(unittest.TestCase):
    """Test cases for the DoshaTool class."""
    
    def setUp(self):
        """Set up the test case with a fresh tool instance."""
        self.tool = DoshaTool()
    
    def test_valid_responses(self):
        """Test with valid responses."""
        test_input = {
            "responses": {
                "body_frame": "thin",
                "skin_type": "dry",
                "energy_level": "variable"
            },
            "user_context": "Testing the tool"
        }
        result = self.tool._run(json.dumps(test_input))
        self.assertIn("Dosha Analysis Results", result)
        self.assertIn("Primary Dosha", result)
        self.assertIn("Recommendations", result)
    
    def test_empty_responses(self):
        """Test with empty responses."""
        test_input = {
            "responses": {},
            "user_context": "Testing with no responses"
        }
        result = self.tool._run(json.dumps(test_input))
        self.assertIn("Error", result)
    
    def test_invalid_json(self):
        """Test with invalid JSON input."""
        result = self.tool._run("not a json string")
        self.assertIn("Error", result)
        self.assertIn("Invalid JSON", result)
    
    def test_get_questionnaire(self):
        """Test that the questionnaire is returned in the correct format."""
        questionnaire = self.tool.get_questionnaire()
        self.assertIsInstance(questionnaire, list)
        self.assertGreater(len(questionnaire), 0)
        for question in questionnaire:
            self.assertIn("id", question)
            self.assertIn("text", question)
            self.assertIn("options", question)
            self.assertIn("category", question)


if __name__ == "__main__":
    unittest.main()
