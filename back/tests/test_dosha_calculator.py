"""
Tests for the DoshaCalculator class.
"""
import unittest
from back.service.dosha_calculator import DoshaCalculator, DoshaType

class TestDoshaCalculator(unittest.TestCase):
    """Test cases for the DoshaCalculator class."""
    
    def setUp(self):
        """Set up the test case with a fresh calculator instance."""
        self.calculator = DoshaCalculator()
    
    def test_vata_dominant(self):
        """Test with responses that indicate Vata dominance."""
        responses = {
            "body_frame": "thin",
            "skin_type": "dry",
            "energy_level": "variable"
        }
        result = self.calculator.calculate_dosha(responses)
        self.assertEqual(result["primary_dosha"], "Vata")
        self.assertGreater(result["scores"]["vata"], result["scores"]["pitta"])
        self.assertGreater(result["scores"]["vata"], result["scores"]["kapha"])
        self.assertIn("Vata", result["analysis"]["overall"])
        self.assertGreater(len(result["recommendations"]), 0)
    
    def test_pitta_dominant(self):
        """Test with responses that indicate Pitta dominance."""
        responses = {
            "body_frame": "medium",
            "skin_type": "sensitive",
            "energy_level": "intense"
        }
        result = self.calculator.calculate_dosha(responses)
        self.assertEqual(result["primary_dosha"], "Pitta")
        self.assertGreater(result["scores"]["pitta"], result["scores"]["vata"])
        self.assertGreater(result["scores"]["pitta"], result["scores"]["kapha"])
        self.assertIn("Pitta", result["analysis"]["overall"])
    
    def test_kapha_dominant(self):
        """Test with responses that indicate Kapha dominance."""
        responses = {
            "body_frame": "large",
            "skin_type": "oily",
            "energy_level": "steady"
        }
        result = self.calculator.calculate_dosha(responses)
        self.assertEqual(result["primary_dosha"], "Kapha")
        self.assertGreater(result["scores"]["kapha"], result["scores"]["vata"])
        self.assertGreater(result["scores"]["kapha"], result["scores"]["pitta"])
        self.assertIn("Kapha", result["analysis"]["overall"])
    
    def test_balanced_doshas(self):
        """Test with responses that result in balanced doshas."""
        responses = {
            "body_frame": "medium",
            "skin_type": "sensitive",
            "energy_level": "steady"
        }
        result = self.calculator.calculate_dosha(responses)
        self.assertIn(result["primary_dosha"], ["Vata", "Pitta", "Kapha"])
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)
    
    def test_empty_responses(self):
        """Test with no responses provided."""
        result = self.calculator.calculate_dosha({})
        self.assertEqual(result["primary_dosha"], "Unknown")
        self.assertEqual(result["confidence"], 0.0)
    
    def test_get_questionnaire(self):
        """Test that the questionnaire is returned in the correct format."""
        questionnaire = self.calculator.get_questionnaire()
        self.assertIsInstance(questionnaire, list)
        self.assertGreater(len(questionnaire), 0)
        for question in questionnaire:
            self.assertIn("id", question)
            self.assertIn("text", question)
            self.assertIn("options", question)
            self.assertIn("category", question)
            self.assertIsInstance(question["options"], list)
            if question["options"]:
                self.assertIn("value", question["options"][0])
                self.assertIn("text", question["options"][0])


if __name__ == "__main__":
    unittest.main()
