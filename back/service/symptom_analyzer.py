"""
Symptom Analyzer Module

This module provides functionality to analyze symptoms and suggest potential
dosha imbalances based on Ayurvedic principles.
"""
from typing import Dict, List, Optional
from enum import Enum

class DoshaType(str, Enum):
    VATA = "Vata"
    PITTA = "Pitta"
    KAPHA = "Kapha"

class SymptomAnalyzer:
    """
    A tool for analyzing symptoms and suggesting potential dosha imbalances.
    """
    
    def __init__(self):
        """Initialize the symptom analyzer with symptom-dosha mappings."""
        self.symptom_mapping = {
            # Physical symptoms
            "dry skin": DoshaType.VATA,
            "dry hair": DoshaType.VATA,
            "constipation": DoshaType.VATA,
            "gas": DoshaType.VATA,
            "bloating": DoshaType.VATA,
            "joint pain": DoshaType.VATA,
            "insomnia": DoshaType.VATA,
            "irregular appetite": DoshaType.VATA,
            "weight loss": DoshaType.VATA,
            "cold hands and feet": DoshaType.VATA,
            "fatigue": DoshaType.VATA,
            "skin rashes": DoshaType.PITTA,
            "acne": DoshaType.PITTA,
            "heartburn": DoshaType.PITTA,
            "acid reflux": DoshaType.PITTA,
            "excessive body heat": DoshaType.PITTA,
            "inflammation": DoshaType.PITTA,
            "excessive sweating": DoshaType.PITTA,
            "loose stools": DoshaType.PITTA,
            "bad breath": DoshaType.PITTA,
            "excessive thirst": DoshaType.PITTA,
            "congestion": DoshaType.KAPHA,
            "mucus": DoshaType.KAPHA,
            "weight gain": DoshaType.KAPHA,
            "water retention": DoshaType.KAPHA,
            "lethargy": DoshaType.KAPHA,
            "slow digestion": DoshaType.KAPHA,
            "allergies": DoshaType.KAPHA,
            "sinus congestion": DoshaType.KAPHA,
            "excessive sleep": DoshaType.KAPHA,
            "slow metabolism": DoshaType.KAPHA,
            
            # Mental/Emotional symptoms
            "anxiety": DoshaType.VATA,
            "worry": DoshaType.VATA,
            "fear": DoshaType.VATA,
            "restlessness": DoshaType.VATA,
            "irritability": DoshaType.PITTA,
            "anger": DoshaType.PITTA,
            "impatience": DoshaType.PITTA,
            "jealousy": DoshaType.PITTA,
            "attachment": DoshaType.KAPHA,
            "greed": DoshaType.KAPHA,
            "possessiveness": DoshaType.KAPHA,
            "depression": DoshaType.KAPHA,
        }
        
        self.dosha_descriptions = {
            DoshaType.VATA: {
                "description": "Vata is associated with movement, communication, and creativity. When imbalanced, it can cause anxiety, dry skin, constipation, and joint pain.",
                "balancing_tips": [
                    "Maintain a regular routine for eating, sleeping, and activities",
                    "Stay warm and avoid cold, dry, windy environments",
                    "Eat warm, moist, and nourishing foods",
                    "Practice gentle, grounding exercises like yoga and walking",
                    "Get adequate rest and maintain a consistent sleep schedule"
                ]
            },
            DoshaType.PITTA: {
                "description": "Pitta governs digestion, metabolism, and transformation. Imbalance can lead to inflammation, heartburn, skin rashes, and irritability.",
                "balancing_tips": [
                    "Avoid excessive heat and sun exposure",
                    "Eat cooling, non-spicy foods",
                    "Practice moderation in work and exercise",
                    "Engage in calming activities like meditation",
                    "Avoid alcohol and processed foods"
                ]
            },
            DoshaType.KAPHA: {
                "description": "Kapha provides structure and lubrication. When out of balance, it can cause weight gain, congestion, lethargy, and attachment.",
                "balancing_tips": [
                    "Engage in regular physical activity",
                    "Eat light, warm, and spicy foods",
                    "Vary your routine and seek new experiences",
                    "Avoid heavy, oily, and sweet foods",
                    "Stay warm and dry"
                ]
            }
        }
    
    def analyze_symptoms(self, symptoms: List[str]) -> Dict:
        """
        Analyze a list of symptoms and suggest potential dosha imbalances.
        
        Args:
            symptoms: List of symptoms to analyze
            
        Returns:
            Dictionary containing analysis results including:
            - primary_dosha: The most imbalanced dosha
            - secondary_dosha: The second most imbalanced dosha (if any)
            - confidence: Confidence score (0-1)
            - recommendations: List of balancing recommendations
            - details: Detailed analysis of each dosha
        """
        # Initialize dosha scores
        dosha_scores = {
            DoshaType.VATA: 0,
            DoshaType.PITTA: 0,
            DoshaType.KAPHA: 0
        }
        
        # Score each symptom
        matched_symptoms = {dosha: [] for dosha in DoshaType}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            if symptom_lower in self.symptom_mapping:
                dosha = self.symptom_mapping[symptom_lower]
                dosha_scores[dosha] += 1
                matched_symptoms[dosha].append(symptom)
        
        # Calculate total score and confidence
        total_score = sum(dosha_scores.values())
        
        if total_score == 0:
            return {
                "primary_dosha": None,
                "secondary_dosha": None,
                "confidence": 0,
                "recommendations": ["No specific dosha imbalance detected based on the provided symptoms."],
                "details": {},
                "matched_symptoms": {}
            }
        
        # Normalize scores
        normalized_scores = {
            dosha: (score / total_score) for dosha, score in dosha_scores.items()
        }
        
        # Sort doshas by score (descending)
        sorted_doshas = sorted(
            dosha_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        primary_dosha, primary_score = sorted_doshas[0]
        secondary_dosha, secondary_score = sorted_doshas[1] if len(sorted_doshas) > 1 else (None, 0)
        
        # Only consider secondary dosha if it has a significant score
        if secondary_score == 0 or (primary_score - secondary_score) > 2:
            secondary_dosha = None
        
        # Prepare response
        response = {
            "primary_dosha": primary_dosha.value if primary_dosha else None,
            "secondary_dosha": secondary_dosha.value if secondary_dosha else None,
            "confidence": normalized_scores[primary_dosha],
            "recommendations": [],
            "details": {},
            "matched_symptoms": matched_symptoms
        }
        
        # Add recommendations and details for primary dosha
        if primary_dosha:
            response["recommendations"].extend(
                self.dosha_descriptions[primary_dosha]["balancing_tips"]
            )
            response["details"][primary_dosha.value] = {
                "description": self.dosha_descriptions[primary_dosha]["description"],
                "score": dosha_scores[primary_dosha],
                "normalized_score": normalized_scores[primary_dosha],
                "matched_symptoms": matched_symptoms[primary_dosha]
            }
        
        # Add recommendations and details for secondary dosha if significant
        if secondary_dosha and secondary_dosha != primary_dosha and secondary_score > 0:
            response["recommendations"].extend(
                self.dosha_descriptions[secondary_dosha]["balancing_tips"]
            )
            response["details"][secondary_dosha.value] = {
                "description": self.dosha_descriptions[secondary_dosha]["description"],
                "score": dosha_scores[secondary_dosha],
                "normalized_score": normalized_scores[secondary_dosha],
                "matched_symptoms": matched_symptoms[secondary_dosha]
            }
        
        return response
