"""
Dosha Calculator Module

This module provides an advanced dosha calculator that offers detailed analysis
and personalized recommendations based on Ayurvedic principles.
"""
from typing import Dict, List, Optional, TypedDict
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone

class DoshaType(str, Enum):
    """Enum representing the three dosha types in Ayurveda."""
    VATA = "Vata"
    PITTA = "Pitta"
    KAPHA = "Kapha"
    UNKNOWN = "Unknown"

class DoshaScores(TypedDict):
    """Type definition for dosha scores dictionary."""
    vata: float
    pitta: float
    kapha: float

class DoshaResult(TypedDict):
    """Type definition for the dosha analysis result."""
    primary_dosha: str
    secondary_dosha: Optional[str]
    scores: Dict[str, float]
    confidence: float
    analysis: Dict[str, str]
    recommendations: List[str]
    timestamp: str

@dataclass
class DoshaQuestion:
    """Class representing a question in the dosha assessment."""
    id: str
    text: str
    options: Dict[str, str]  # value: display_text
    weights: Dict[str, Dict[str, int]]  # option_value: {dosha: weight}
    category: str  # physical, mental, emotional, lifestyle

class DoshaCalculator:
    """
    A comprehensive dosha calculator that provides detailed analysis and recommendations
    based on Ayurvedic principles.
    """
    
    def __init__(self):
        """Initialize the dosha calculator with the question set."""
        self.questions = self._initialize_questions()
    
    def _initialize_questions(self) -> List[DoshaQuestion]:
        """Initialize the set of questions for the dosha assessment."""
        questions = [
            # Physical characteristics
            DoshaQuestion(
                id="body_frame",
                text="Which best describes your body frame?",
                options={
                    "thin": "Thin, light build, difficulty gaining weight",
                    "medium": "Medium, well-proportioned build",
                    "large": "Large, solid, heavy build"
                },
                weights={
                    "thin": {"vata": 3, "pitta": 1, "kapha": 0},
                    "medium": {"vata": 0, "pitta": 3, "kapha": 1},
                    "large": {"vata": 0, "pitta": 0, "kapha": 3}
                },
                category="physical"
            ),
            DoshaQuestion(
                id="skin_type",
                text="How would you describe your skin type?",
                options={
                    "dry": "Dry, rough, or flaky skin",
                    "sensitive": "Sensitive, prone to rashes or inflammation",
                    "oily": "Oily, smooth, or moist skin"
                },
                weights={
                    "dry": {"vata": 3, "pitta": 0, "kapha": 0},
                    "sensitive": {"vata": 1, "pitta": 3, "kapha": 0},
                    "oily": {"vata": 0, "pitta": 1, "kapha": 3}
                },
                category="physical"
            ),
            DoshaQuestion(
                id="hair_type",
                text="What best describes your hair?",
                options={
                    "dry": "Dry, frizzy, or brittle",
                    "fine": "Fine, straight, or thinning",
                    "thick": "Thick, oily, or wavy"
                },
                weights={
                    "dry": {"vata": 3, "pitta": 0, "kapha": 0},
                    "fine": {"vata": 2, "pitta": 2, "kapha": 0},
                    "thick": {"vata": 0, "pitta": 1, "kapha": 3}
                },
                category="physical"
            ),
            
            # Digestion and appetite
            DoshaQuestion(
                id="appetite",
                text="How would you describe your appetite?",
                options={
                    "variable": "Variable, sometimes strong, sometimes weak",
                    "strong": "Strong, can't skip meals",
                    "steady": "Steady, can easily skip meals"
                },
                weights={
                    "variable": {"vata": 3, "pitta": 0, "kapha": 0},
                    "strong": {"vata": 0, "pitta": 3, "kapha": 0},
                    "steady": {"vata": 0, "pitta": 1, "kapha": 3}
                },
                category="physical"
            ),
            DoshaQuestion(
                id="digestion",
                text="How would you describe your digestion?",
                options={
                    "irregular": "Irregular, sometimes constipated",
                    "quick": "Quick, strong digestion, can eat almost anything",
                    "slow": "Slow, heavy after meals"
                },
                weights={
                    "irregular": {"vata": 3, "pitta": 0, "kapha": 0},
                    "quick": {"vata": 0, "pitta": 3, "kapha": 0},
                    "slow": {"vata": 0, "pitta": 0, "kapha": 3}
                },
                category="physical"
            ),
            
            # Energy and activity
            DoshaQuestion(
                id="weight_tendency",
                text="What is your weight tendency?",
                options={
                    "difficult_to_gain": "Difficult to gain weight",
                    "easy_to_maintain": "Easy to maintain weight",
                    "difficult_to_lose": "Difficult to lose weight"
                },
                weights={
                    "difficult_to_gain": {"vata": 3, "pitta": 1, "kapha": 0},
                    "easy_to_maintain": {"vata": 0, "pitta": 3, "kapha": 0},
                    "difficult_to_lose": {"vata": 0, "pitta": 0, "kapha": 3}
                },
                category="lifestyle"
            ),
            DoshaQuestion(
                id="temperature_preference",
                text="What temperature do you prefer?",
                options={
                    "warm": "Warm, dislike cold",
                    "cool": "Cool, dislike heat",
                    "adaptable": "Adaptable, but dislike dampness"
                },
                weights={
                    "warm": {"vata": 3, "pitta": 0, "kapha": 1},
                    "cool": {"vata": 0, "pitta": 3, "kapha": 0},
                    "adaptable": {"vata": 1, "pitta": 1, "kapha": 3}
                },
                category="physical"
            ),
            
            # Sleep patterns
            DoshaQuestion(
                id="sleep_pattern",
                text="How would you describe your sleep?",
                options={
                    "light": "Light, easily disturbed",
                    "moderate": "Moderate, wake up easily if needed",
                    "heavy": "Heavy, difficult to wake up"
                },
                weights={
                    "light": {"vata": 3, "pitta": 1, "kapha": 0},
                    "moderate": {"vata": 0, "pitta": 3, "kapha": 0},
                    "heavy": {"vata": 0, "pitta": 0, "kapha": 3}
                },
                category="lifestyle"
            ),
            
            # Mental and emotional
            DoshaQuestion(
                id="energy_level",
                text="How would you describe your energy levels?",
                options={
                    "variable": "Variable, bursts of energy",
                    "intense": "Intense, high energy",
                    "steady": "Steady, even energy"
                },
                weights={
                    "variable": {"vata": 3, "pitta": 0, "kapha": 0},
                    "intense": {"vata": 0, "pitta": 3, "kapha": 0},
                    "steady": {"vata": 0, "pitta": 0, "kapha": 3}
                },
                category="mental"
            ),
            DoshaQuestion(
                id="mental_activity",
                text="How would you describe your mental activity?",
                options={
                    "restless": "Restless, active mind",
                    "focused": "Focused, sharp",
                    "calm": "Calm, steady"
                },
                weights={
                    "restless": {"vata": 3, "pitta": 0, "kapha": 0},
                    "focused": {"vata": 0, "pitta": 3, "kapha": 0},
                    "calm": {"vata": 0, "pitta": 0, "kapha": 3}
                },
                category="mental"
            ),
            DoshaQuestion(
                id="emotional_tendency",
                text="What is your emotional tendency?",
                options={
                    "anxious": "Anxious, worrisome",
                    "irritable": "Easily irritated or angry",
                    "attached": "Attached, sentimental"
                },
                weights={
                    "anxious": {"vata": 3, "pitta": 0, "kapha": 0},
                    "irritable": {"vata": 0, "pitta": 3, "kapha": 0},
                    "attached": {"vata": 0, "pitta": 0, "kapha": 3}
                },
                category="emotional"
            ),
            
            # Speech and communication
            DoshaQuestion(
                id="speech_pattern",
                text="How would you describe your speech pattern?",
                options={
                    "fast": "Fast, talkative",
                    "sharp": "Sharp, precise",
                    "slow": "Slow, deliberate"
                },
                weights={
                    "fast": {"vata": 3, "pitta": 1, "kapha": 0},
                    "sharp": {"vata": 0, "pitta": 3, "kapha": 0},
                    "slow": {"vata": 0, "pitta": 0, "kapha": 3}
                },
                category="mental"
            )
        ]
        return questions
    
    def calculate_dosha(self, responses: Dict[str, str]) -> DoshaResult:
        """
        Calculate dosha based on user responses.
        
        Args:
            responses: Dictionary of question IDs to selected option values
            
        Returns:
            DoshaResult with detailed analysis
        """
        scores = {"vata": 0, "pitta": 0, "kapha": 0}
        category_scores = {
            "physical": {"vata": 0, "pitta": 0, "kapha": 0},
            "mental": {"vata": 0, "pitta": 0, "kapha": 0},
            "emotional": {"vata": 0, "pitta": 0, "kapha": 0},
            "lifestyle": {"vata": 0, "pitta": 0, "kapha": 0}
        }
        
        # Calculate scores
        for question in self.questions:
            if question.id in responses and responses[question.id] in question.weights:
                selected_option = responses[question.id]
                weights = question.weights[selected_option]
                
                # Update main scores
                for dosha, weight in weights.items():
                    scores[dosha] += weight
                    category_scores[question.category][dosha] += weight
        
        # Normalize scores
        total = sum(scores.values()) or 1  # Avoid division by zero
        normalized_scores = {k: round((v / total) * 100, 1) for k, v in scores.items()}
        
        # Determine primary and secondary doshas
        sorted_doshas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_dosha = sorted_doshas[0][0].capitalize() if sorted_doshas[0][1] > 0 else DoshaType.UNKNOWN
        secondary_dosha = sorted_doshas[1][0].capitalize() if len(sorted_doshas) > 1 and sorted_doshas[1][1] > 0 else None
        
        # Calculate confidence (difference between primary and secondary)
        confidence = 0.0
        if len(sorted_doshas) > 1:
            confidence = (sorted_doshas[0][1] - sorted_doshas[1][1]) / total
        
        # Generate analysis and recommendations
        analysis = self._generate_analysis(primary_dosha, category_scores)
        recommendations = self._generate_recommendations(primary_dosha, secondary_dosha)
        
        return {
            "primary_dosha": primary_dosha,
            "secondary_dosha": secondary_dosha,
            "scores": normalized_scores,
            "confidence": confidence,
            "analysis": analysis,
            "recommendations": recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_analysis(self, primary_dosha: str, category_scores: Dict[str, Dict[str, int]]) -> Dict[str, str]:
        """Generate detailed analysis based on dosha scores by category."""
        analysis = {}
        
        # Overall analysis
        analysis["overall"] = (
            f"Your primary dosha is {primary_dosha}. This means you have a predominance of {primary_dosha} energy "
            f"in your constitution. {self._get_dosha_description(primary_dosha)}"
        )
        
        # Category-wise analysis
        for category, scores in category_scores.items():
            category_total = sum(scores.values()) or 1
            if category_total > 0:  # Only include categories with responses
                category_dominant = max(scores.items(), key=lambda x: x[1])[0].capitalize()
                category_percent = (scores[category_dominant.lower()] / category_total) * 100
                
                analysis[category] = (
                    f"In {category} aspects, you show strong {category_dominant} tendencies ({category_percent:.1f}%). "
                    f"{self._get_category_analysis(category, category_dominant)}"
                )
        
        return analysis
    
    def _get_dosha_description(self, dosha: str) -> str:
        """Get a description of the given dosha."""
        descriptions = {
            "Vata": (
                "Vata represents the energy of movement and is associated with qualities like dry, light, cold, "
                "rough, subtle, and mobile. When in balance, Vata promotes creativity and flexibility. When out "
                "of balance, it can cause fear, anxiety, and physical ailments."
            ),
            "Pitta": (
                "Pitta represents the energy of transformation and is associated with qualities like hot, sharp, "
                "light, liquid, and oily. When in balance, Pitta promotes intelligence and understanding. When out "
                "of balance, it can cause anger, jealousy, and inflammation."
            ),
            "Kapha": (
                "Kapha represents the energy of structure and lubrication and is associated with qualities like "
                "heavy, slow, cool, oily, and smooth. When in balance, Kapha promotes love, calmness, and forgiveness. "
                "When out of balance, it can lead to attachment, greed, and resistance to change."
            )
        }
        return descriptions.get(dosha, "")
    
    def _get_category_analysis(self, category: str, dosha: str) -> str:
        """Get analysis for a specific category and dosha."""
        analysis = {
            ("physical", "Vata"): "Your physical constitution shows characteristics like a light frame, dry skin, and variable digestion.",
            ("physical", "Pitta"): "Your physical constitution shows characteristics like a medium build, warm skin, and strong digestion.",
            ("physical", "Kapha"): "Your physical constitution shows characteristics like a solid build, oily skin, and steady energy.",
            ("mental", "Vata"): "Your mental patterns show creativity, quick thinking, and adaptability.",
            ("mental", "Pitta"): "Your mental patterns show sharpness, focus, and determination.",
            ("mental", "Kapha"): "Your mental patterns show steadiness, patience, and methodical thinking.",
            ("lifestyle", "Vata"): "Your lifestyle tendencies include variable energy levels and enthusiasm for new experiences.",
            ("lifestyle", "Pitta"): "Your lifestyle tendencies include goal-oriented behavior and intensity in activities.",
            ("lifestyle", "Kapha"): "Your lifestyle tendencies include steady energy and enjoyment of routine.",
            ("emotional", "Vata"): "Your emotional nature is characterized by quick changes and enthusiasm.",
            ("emotional", "Pitta"): "Your emotional nature is characterized by passion and intensity.",
            ("emotional", "Kapha"): "Your emotional nature is characterized by stability and loyalty."
        }
        return analysis.get((category, dosha), "")
    
    def _generate_recommendations(self, primary_dosha: str, secondary_dosha: Optional[str] = None) -> List[str]:
        """Generate personalized recommendations based on dosha analysis."""
        recommendations = []
        
        # Diet recommendations
        diet = {
            "Vata": [
                "Favor warm, cooked, and slightly oily foods",
                "Include sweet, sour, and salty tastes",
                "Eat in a calm environment and maintain regular meal times"
            ],
            "Pitta": [
                "Favor cool or warm (but not hot) foods",
                "Include sweet, bitter, and astringent tastes",
                "Avoid excessive spicy, sour, or salty foods"
            ],
            "Kapha": [
                "Favor light, dry, and warm foods",
                "Include pungent, bitter, and astringent tastes",
                "Avoid heavy, oily, or excessively sweet foods"
            ]
        }
        
        # Lifestyle recommendations
        lifestyle = {
            "Vata": [
                "Maintain a regular daily routine",
                "Engage in gentle, grounding exercises like yoga or walking",
                "Ensure adequate rest and relaxation"
            ],
            "Pitta": [
                "Avoid excessive heat and sun exposure",
                "Engage in moderate exercise and relaxation techniques",
                "Maintain a good work-life balance"
            ],
            "Kapha": [
                "Engage in regular, vigorous exercise",
                "Seek variety and new experiences",
                "Avoid excessive sleep and daytime napping"
            ]
        }
        
        # Add primary dosha recommendations
        if primary_dosha in diet:
            recommendations.append(f"**Diet for {primary_dosha} balance:**")
            recommendations.extend([f"- {item}" for item in diet[primary_dosha]])
            
            recommendations.append(f"\n**Lifestyle for {primary_dosha} balance:**")
            recommendations.extend([f"- {item}" for item in lifestyle[primary_dosha]])
        
        # Add secondary dosha recommendations if significant
        if secondary_dosha and secondary_dosha in diet and secondary_dosha != primary_dosha:
            recommendations.append(f"\n**Additional considerations for {secondary_dosha} influence:**")
            recommendations.extend([f"- {item}" for item in diet[secondary_dosha][:2]])
            recommendations.extend([f"- {item}" for item in lifestyle[secondary_dosha][:2]])
        
        return recommendations
    
    def get_questionnaire(self) -> List[dict]:
        """Get the list of questions for the dosha assessment."""
        return [
            {
                "id": q.id,
                "text": q.text,
                "options": [{"value": k, "text": v} for k, v in q.options.items()],
                "category": q.category
            }
            for q in self.questions
        ]

# Create a default instance for easy importing
dosha_calculator = DoshaCalculator()

def determine_dosha(user_responses: Dict[str, str]) -> Dict[str, any]:
    """
    Determine the dominant dosha based on user responses.
    
    This is a convenience wrapper around the DoshaCalculator for backward compatibility.
    """
    result = dosha_calculator.calculate_dosha(user_responses)
    return {
        'dosha': result['primary_dosha'],
        'confidence': result['confidence'],
        'message': result['analysis'].get('overall', '')
    }
