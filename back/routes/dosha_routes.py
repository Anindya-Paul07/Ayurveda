from flask import Blueprint, request, jsonify
from service.dosha_service import determine_dosha

# Create a blueprint for dosha-related routes
dosha_blueprint = Blueprint('dosha', __name__)

@dosha_blueprint.route('/api/dosha', methods=['POST'])
def get_dosha():
    """
    Determine a user's dosha based on their responses to a questionnaire.
    
    Expects a JSON payload with user responses to various questions.
    
    Request Body:
    {
        "responses": {
            "question1": "answer",
            "question2": "answer",
            ...
        }
    }
    
    Returns:
    {
        "dosha": "Vata|Pitta|Kapha",
        "message": "Description of the dosha and its characteristics"
    }
    
    Status Codes:
    - 200: Successful determination
    - 400: Invalid input data
    - 500: Server error
    """
    try:
        # Get the JSON data from the request
        try:
            data = request.get_json()
            if data is None:
                return jsonify({'error': 'Invalid JSON format or Content-Type not set to application/json'}), 400
        except Exception as json_error:
            return jsonify({'error': f'Invalid JSON format: {str(json_error)}'}), 400
        
        # Validate the input data
        if not data or 'responses' not in data:
            return jsonify({
                'error': 'Invalid input. Please provide responses to the questionnaire.'
            }), 400
        
        # Extract the responses
        responses = data['responses']
        
        # Validate that responses is a dictionary and not empty
        if not isinstance(responses, dict) or not responses:
            return jsonify({
                'error': 'Responses must be a non-empty dictionary.'
            }), 400
        
        # Call the service to determine the dosha
        dosha_result = determine_dosha(responses)
        
        # Return the result
        return jsonify({
            'dosha': dosha_result['dosha'],
            'message': dosha_result['message']
        }), 200
        
    except Exception as e:
        # Log the error (in a production environment)
        print(f"Error determining dosha: {str(e)}")
        
        # Return a generic error message
        return jsonify({
            'error': 'An error occurred while determining your dosha.'
        }), 500
