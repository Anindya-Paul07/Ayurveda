"""
Tests for the SymptomAnalyzer class.
"""
import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from back.service.symptom_analyzer import SymptomAnalyzer, DoshaType

class TestSymptomAnalyzer(unittest.TestCase):
    """Test cases for SymptomAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = SymptomAnalyzer()
    
    def test_vata_imbalance(self):
        """Test detection of Vata imbalance."""
        symptoms = ["dry skin", "constipation", "anxiety", "insomnia"]
        result = self.analyzer.analyze_symptoms(symptoms)
        self.assertEqual(result["primary_dosha"], "Vata")
        self.assertGreater(result["confidence"], 0.5)
        self.assertIn("Vata", result["details"])
        self.assertGreaterEqual(len(result["recommendations"]), 3)
    
    def test_pitta_imbalance(self):
        """Test detection of Pitta imbalance."""
        symptoms = ["heartburn", "skin rashes", "irritability"]
        result = self.analyzer.analyze_symptoms(symptoms)
        self.assertEqual(result["primary_dosha"], "Pitta")
        self.assertGreater(result["confidence"], 0.5)
        self.assertIn("Pitta", result["details"])
    
    def test_kapha_imbalance(self):
        """Test detection of Kapha imbalance."""
        symptoms = ["congestion", "weight gain", "lethargy"]
        result = self.analyzer.analyze_symptoms(symptoms)
        self.assertEqual(result["primary_dosha"], "Kapha")
        self.assertGreater(result["confidence"], 0.5)
        self.assertIn("Kapha", result["details"])
    
    def test_combined_imbalance(self):
        """Test detection of combined dosha imbalance."""
        symptoms = ["dry skin", "heartburn", "congestion"]
        result = self.analyzer.analyze_symptoms(symptoms)
        self.assertIn(result["primary_dosha"], ["Vata", "Pitta", "Kapha"])
        self.assertIsNotNone(result["primary_dosha"])
        self.assertGreater(result["confidence"], 0.3)
    
    def test_no_matching_symptoms(self):
        """Test with no matching symptoms."""
        symptoms = ["nonexistent_symptom1", "nonexistent_symptom2"]
        result = self.analyzer.analyze_symptoms(symptoms)
        self.assertIsNone(result["primary_dosha"])
        self.assertEqual(result["confidence"], 0)
        self.assertEqual(len(result["recommendations"]), 1)

if __name__ == "__main__":
    unittest.main()
