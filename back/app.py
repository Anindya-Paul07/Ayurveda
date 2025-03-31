"""
Ayurveda Chatbot Application

This is the main application file that initializes the Flask app, sets up routes,
and integrates various services including:
- Dosha determination
- Weather data integration
- Ayurvedic recommendations
- RAG-based chatbot with Pinecone vector store

The application uses blueprints to organize routes and provides a comprehensive
API for Ayurvedic health information and personalized recommendations.
"""

# Standard library imports
import os
import re
import sys

# Add parent directory to path to allow imports from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Third-party imports
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Local application imports
from back.service.helper import download_hugging_face_embeddings
from back.service.prompt import system_prompt
from back.service.google_search import execute_google_search

# Import blueprints from routes modules
from back.routes.dosha_routes import dosha_blueprint
from back.routes.weather_routes import weather_bp
from back.routes.recommendations_routes import recommendations_bp

# -------------------------------------------------------------------------
# Disease and Remedy Tracking System
# -------------------------------------------------------------------------

# Enhanced data structure to store tracked diseases and their remedies
tracked_diseases = {}

def track_disease(user_msg, bot_answer):
    """
    Track mentions of diseases in user messages and bot answers.
    
    This function identifies disease keywords in conversations and stores
    relevant information for later retrieval and analysis.
    
    Args:
        user_msg (str): The user's message
        bot_answer (str): The bot's response
    """
    # Define a list of common disease keywords; expand as needed
    disease_keywords = ['diabetes', 'hypertension', 'cancer', 'asthma', 'arthritis']
    for disease in disease_keywords:
        if disease in user_msg.lower() or disease in bot_answer.lower():
            # Initialize the disease entry with a structured format if it doesn't exist
            if disease not in tracked_diseases:
                tracked_diseases[disease] = {
                    'full_responses': [],
                    'remedies': []
                }
            
            # Add the full response
            tracked_diseases[disease]['full_responses'].append(bot_answer)
            
            # Try to extract remedy-specific information
            extract_remedies(disease, bot_answer)

def extract_remedies(disease, bot_answer):
    """
    Extract remedy information from bot answers and store it separately.
    
    This function uses regex patterns to identify text that likely contains
    remedy information for a specific disease.
    
    Args:
        disease (str): The disease name
        bot_answer (str): The bot's response to analyze
    """
    # Common patterns that might indicate remedies in the text
    remedy_indicators = [
        r"(?:recommended|common|effective|useful|beneficial) (?:remedies|treatments|herbs|solutions)",
        r"(?:you can|try|consider) (?:using|taking|consuming)",
        r"(?:home remedies|natural treatments)",
        r"(?:ayurvedic treatments|herbs for)"
    ]
    
    # Check if any remedy indicator is present in the answer
    contains_remedy = any(re.search(pattern, bot_answer.lower()) for pattern in remedy_indicators)
    
    if contains_remedy:
        # If the answer likely contains remedy information, add it to the remedies list
        if bot_answer not in tracked_diseases[disease]['remedies']:
            tracked_diseases[disease]['remedies'].append(bot_answer)

# -------------------------------------------------------------------------
# Flask Application Setup
# -------------------------------------------------------------------------

# Initialize Flask application
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Register blueprints for the API endpoints
# Each blueprint encapsulates a specific domain of functionality
app.register_blueprint(dosha_blueprint)  # /api/dosha - Determines user's dosha based on questionnaire
app.register_blueprint(weather_bp)       # /api/weather - Provides weather data for location-based recommendations
app.register_blueprint(recommendations_bp)  # /api/recommendations - Delivers personalized Ayurvedic recommendations

# Note: Detailed API documentation is available in the docstrings of each route

# -------------------------------------------------------------------------
# Vector Store and LLM Setup for RAG
# -------------------------------------------------------------------------

# Set up API keys from environment variables
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Ensure environment variables are set for libraries that read directly from os.environ
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Download and initialize embeddings model
embeddings = download_hugging_face_embeddings()

# Connect to existing Pinecone vector store index
index_name = "herbbot"
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

# Create a retriever with similarity search
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})

# Initialize the LLM (using Groq's API with Llama model)
llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    model_name="llama-3.3-70b-versatile",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.4,
    max_tokens=1024
)

# Create a prompt template with system and user messages
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# Set up the RAG pipeline
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


# -------------------------------------------------------------------------
# Main Application Routes
# -------------------------------------------------------------------------

@app.route("/")
def index():
    """
    Render the main chat interface with tracked diseases data.
    
    Returns:
        Rendered HTML template with disease tracking data
    """
    return render_template('../templates/ayurveda_chat.html', diseases=tracked_diseases)


@app.route("/api/general", methods=["GET", "POST"])
def chat():
    """
    Main chat endpoint that processes user messages and returns AI responses.
    
    This endpoint uses RAG (Retrieval Augmented Generation) to provide
    accurate Ayurvedic information, with fallback to Google search when
    the local knowledge base is insufficient.
    
    Request Body:
        {
            "message": "User's question about Ayurveda"
        }
        
    Returns:
        JSON response with the answer
        
    Status Codes:
        200: Successful response
        400: Invalid input
    """
    # Parse and validate the request data
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid input"}), 400
    
    # Extract the user message
    msg = data.get('message')
    print(f"Received message: {msg}")
    
    # Process the message through the RAG pipeline
    response = rag_chain.invoke({"input": msg})
    answer = response.get("answer")
    
    # Fallback to Google search if the local context was insufficient
    if not answer or "don't know" in answer.lower() or "i don't have" in answer.lower():
        google_result = execute_google_search(msg)
        answer = f"Based on additional research, here are some results:\n\n{google_result}"
    
    print(f"Response: {answer}")
    
    # Track diseases and remedies mentioned in the conversation
    track_disease(msg, answer)
    track_remedy(msg, answer)
    
    # Return the response to the client
    return jsonify({"response": answer})

def track_remedy(user_msg, bot_answer):
    """
    Dedicated function to identify and track potential remedies in bot answers.
    
    This function analyzes the bot's response for specific remedy patterns and
    associates them with diseases mentioned in the conversation. It maintains
    a structured database of remedies for later retrieval.
    
    Args:
        user_msg (str): The user's message
        bot_answer (str): The bot's response to analyze
    """
    # Look for specific remedy patterns in the answer
    remedy_patterns = [
        # Pattern for lists of remedies
        r"\d+\.\s+([^.]+)",
        # Pattern for "take X for Y" statements
        r"take\s+([^.]+)\s+for\s+([^.]+)",
        # Pattern for "X is beneficial for Y" statements
        r"([^.]+)\s+is\s+beneficial\s+for\s+([^.]+)",
        # Pattern for "X helps with Y" statements
        r"([^.]+)\s+helps\s+with\s+([^.]+)"
    ]
    
    # Check for disease mentions in the user message or bot answer
    disease_keywords = ['diabetes', 'hypertension', 'cancer', 'asthma', 'arthritis',
                        'cold fever', 'cancer', 'tumor']
    mentioned_diseases = []
    
    for disease in disease_keywords:
        if disease in user_msg.lower() or disease in bot_answer.lower():
            mentioned_diseases.append(disease)
    
    # If no specific disease is mentioned, check for general remedy information
    if not mentioned_diseases:
        if any(re.search(pattern, bot_answer) for pattern in remedy_patterns):
            if "general_remedies" not in tracked_diseases:
                tracked_diseases["general_remedies"] = {
                    'full_responses': [],
                    'remedies': []
                }
            tracked_diseases["general_remedies"]['full_responses'].append(bot_answer)
            tracked_diseases["general_remedies"]['remedies'].append(bot_answer)
    else:
        # For each mentioned disease, check if the answer contains remedy information
        for disease in mentioned_diseases:
            # Ensure the disease entry exists with the proper structure
            if disease not in tracked_diseases:
                tracked_diseases[disease] = {
                    'full_responses': [],
                    'remedies': []
                }
            
            # Check if the answer contains specific remedy patterns
            if any(re.search(pattern, bot_answer) for pattern in remedy_patterns):
                # Add to remedies if not already present
                if bot_answer not in tracked_diseases[disease]['remedies']:
                    tracked_diseases[disease]['remedies'].append(bot_answer)




@app.route('/api/remedies', methods=['GET'])
def get_remedies():
    """
    Retrieve tracked remedies for all diseases.
    
    This endpoint provides access to the remedies that have been identified
    and tracked during conversations with users.
    
    Returns:
        JSON response with a simplified structure mapping diseases to remedies
        
    Example Response:
        {
            "diabetes": ["Take bitter gourd juice...", "Cinnamon helps regulate..."],
            "general_remedies": ["Turmeric is beneficial for..."]
        }
    """
    # Create a simplified version of tracked_diseases for the frontend
    # The frontend expects a structure where each disease maps to a list of remedies
    simplified_remedies = {}
    
    for disease, data in tracked_diseases.items():
        # If we have specific remedies extracted, use those
        if data['remedies']:
            simplified_remedies[disease] = data['remedies']
        # Otherwise fall back to full responses
        elif data['full_responses']:
            simplified_remedies[disease] = data['full_responses']
    
    return jsonify(simplified_remedies)

# -------------------------------------------------------------------------
# Application Entry Point
# -------------------------------------------------------------------------

if __name__ == '__main__':
    """
    Start the Flask application with all registered blueprints.
    
    Available API endpoints:
    - / : Main web interface for the Ayurveda chatbot
    - /api/general: General chat endpoint for Ayurvedic information
    - /api/remedies: Get tracked remedies for various diseases
    - /api/dosha: Determine user's dosha based on questionnaire (POST)
    - /api/weather: Get weather data for a location (GET)
    - /api/recommendations: Get personalized Ayurvedic recommendations (GET)
      based on dosha, season, and other factors
    """
    # Set the template folder to the parent directory's templates folder
    app.template_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
    app.run(host="0.0.0.0", port=8080, debug=True)
