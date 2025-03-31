"""
Dosha Service Module

This module provides functionality to determine a user's Ayurvedic dosha type
based on their responses to a questionnaire or assessment.
"""

def determine_dosha(user_responses):
    """
    Determines a user's dominant dosha based on their responses to a questionnaire.
    
    Uses a scoring system to evaluate responses to various questions about physical
    and mental traits, and calculates the predominant dosha along with a confidence level.
    
    Args:
        user_responses (dict): A dictionary where keys are question IDs and values 
                              are the user's answers from the Dosha questionnaire.
    
    Returns:
        dict: A dictionary containing:
            - 'dosha': The determined dosha type ('Vata', 'Pitta', 'Kapha', or 'Unknown')
            - 'confidence': A percentage indicating the confidence in the determination
            - 'message': A description of the dosha and its characteristics
    """
    # Initialize scores for each dosha type
    vata_score = 0
    pitta_score = 0
    kapha_score = 0
    
    # Define the scoring system for each question and possible answer
    scoring_system = {
        "body_frame": {
            "thin": {"vata": 3, "pitta": 1, "kapha": 0},
            "medium": {"vata": 0, "pitta": 3, "kapha": 1},
            "large": {"vata": 0, "pitta": 0, "kapha": 3}
        },
        "skin_type": {
            "dry": {"vata": 3, "pitta": 0, "kapha": 0},
            "sensitive": {"vata": 1, "pitta": 3, "kapha": 0},
            "oily": {"vata": 0, "pitta": 1, "kapha": 3}
        },
        "hair_type": {
            "dry": {"vata": 3, "pitta": 0, "kapha": 0},
            "fine": {"vata": 2, "pitta": 2, "kapha": 0},
            "thick": {"vata": 0, "pitta": 1, "kapha": 3}
        },
        "appetite": {
            "variable": {"vata": 3, "pitta": 0, "kapha": 0},
            "strong": {"vata": 0, "pitta": 3, "kapha": 0},
            "steady": {"vata": 0, "pitta": 1, "kapha": 3}
        },
        "digestion": {
            "irregular": {"vata": 3, "pitta": 0, "kapha": 0},
            "quick": {"vata": 0, "pitta": 3, "kapha": 0},
            "slow": {"vata": 0, "pitta": 0, "kapha": 3}
        },
        "weight_tendency": {
            "difficult_to_gain": {"vata": 3, "pitta": 1, "kapha": 0},
            "easy_to_maintain": {"vata": 0, "pitta": 3, "kapha": 0},
            "difficult_to_lose": {"vata": 0, "pitta": 0, "kapha": 3}
        },
        "temperature_preference": {
            "warm": {"vata": 3, "pitta": 0, "kapha": 1},
            "cool": {"vata": 0, "pitta": 3, "kapha": 0},
            "adaptable": {"vata": 1, "pitta": 1, "kapha": 3}
        },
        "sleep_pattern": {
            "light": {"vata": 3, "pitta": 1, "kapha": 0},
            "moderate": {"vata": 0, "pitta": 3, "kapha": 0},
            "heavy": {"vata": 0, "pitta": 0, "kapha": 3}
        },
        "energy_level": {
            "variable": {"vata": 3, "pitta": 0, "kapha": 0},
            "intense": {"vata": 0, "pitta": 3, "kapha": 0},
            "steady": {"vata": 0, "pitta": 0, "kapha": 3}
        },
        "mental_activity": {
            "restless": {"vata": 3, "pitta": 0, "kapha": 0},
            "focused": {"vata": 0, "pitta": 3, "kapha": 0},
            "calm": {"vata": 0, "pitta": 0, "kapha": 3}
        },
        "emotional_tendency": {
            "anxious": {"vata": 3, "pitta": 0, "kapha": 0},
            "irritable": {"vata": 0, "pitta": 3, "kapha": 0},
            "attached": {"vata": 0, "pitta": 0, "kapha": 3}
        },
        "speech_pattern": {
            "fast": {"vata": 3, "pitta": 1, "kapha": 0},
            "sharp": {"vata": 0, "pitta": 3, "kapha": 0},
            "slow": {"vata": 0, "pitta": 0, "kapha": 3}
        }
    }
    
    # Process each user response
    for question, answer in user_responses.items():
        # Check if the question is in our scoring system
        if question in scoring_system:
            # Check if the answer is in our scoring system for this question
            if answer in scoring_system[question]:
                # Add the scores for each dosha
                vata_score += scoring_system[question][answer]["vata"]
                pitta_score += scoring_system[question][answer]["pitta"]
                kapha_score += scoring_system[question][answer]["kapha"]
    
    # Calculate total score
    total_score = vata_score + pitta_score + kapha_score
    
    # If no scores were accumulated, return unknown
    if total_score == 0:
        return {
            'dosha': 'Unknown',
            'confidence': 0.0,
            'message': 'Unable to determine your dosha based on the provided responses. Please ensure you answer all questions in the questionnaire.'
        }
    
    # Determine the predominant dosha
    dosha_scores = {
        'Vata': vata_score,
        'Pitta': pitta_score,
        'Kapha': kapha_score
    }
    
    predominant_dosha = max(dosha_scores, key=dosha_scores.get)
    
    # Calculate confidence percentage
    confidence = (dosha_scores[predominant_dosha] / total_score) * 100
    confidence = round(confidence, 2)  # Round to 2 decimal places
    
    # Define descriptions for each dosha
    dosha_descriptions = {
        'Vata': (
            "You have a predominantly Vata constitution. Vata types are typically creative, energetic, and quick-thinking. "
            "They often have a thin build, dry skin, and variable appetite. To balance your Vata, maintain regular routines, "
            "stay warm, get adequate rest, and favor warm, nourishing foods. Avoid excessive stimulation, cold, and irregular habits."
        ),
        'Pitta': (
            "You have a predominantly Pitta constitution. Pitta types are typically intelligent, focused, and ambitious. "
            "They often have a medium build, warm skin, and strong appetite. To balance your Pitta, stay cool, avoid excessive "
            "heat and sun exposure, eat cooling foods, and manage stress through relaxation techniques. "
            "Avoid excessive spicy foods, alcohol, and intense competition."
        ),
        'Kapha': (
            "You have a predominantly Kapha constitution. Kapha types are typically calm, steady, and compassionate. "
            "They often have a larger build, oily skin, and steady appetite. To balance your Kapha, maintain regular exercise, "
            "seek variety and stimulation, and favor light, warm, and spicy foods. Avoid excessive sleep, heavy foods, "
            "and sedentary lifestyle."
        ),
        'Unknown': (
            "Your dosha type could not be determined with confidence. This may be due to a balanced constitution "
            "or insufficient information. Consider consulting with an Ayurvedic practitioner for a more personalized assessment."
        )
    }
    
    # Return the result
    return {
        'dosha': predominant_dosha,
        'confidence': confidence,
        'message': dosha_descriptions[predominant_dosha]
    }

# Potential enhancements:
# 1. Implement a more sophisticated scoring system with weighted keywords
# 2. Consider the context of keywords (e.g., negations like "not dry")
# 3. Use machine learning models trained on labeled data
# 4. Include seasonal and temporal variations in dosha determination
# 5. Consider secondary and tertiary doshas for a more nuanced analysis
