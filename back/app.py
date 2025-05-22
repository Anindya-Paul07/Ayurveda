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

This centralized backend integrates with the React frontend by serving
static assets from the frontend directory and providing API endpoints that
the React components interact with. Environment variables for services like
Pinecone, OpenWeatherMap, and OpenAI are loaded using dotenv, ensuring they are
free and open-source options.
"""

# Standard library imports
import os
import sys
import eventlet
eventlet.monkey_patch()  # Required for WebSocket support

# Add parent directory to path to allow imports from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Third-party imports
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Local application imports
from config import config

# Local application imports
from service.helper import download_hugging_face_embeddings
from service.prompt import system_prompt, prompt
from service.google_search import execute_google_search
from service.agent_service import agent_service
from service.metrics_service import metrics_service

# Import blueprints from routes modules
from routes.dosha_routes import dosha_blueprint
from routes.health_routes import health_bp
from routes.weather_routes import weather_bp
from routes.recommendations_routes import recommendations_bp
from routes.metrics_routes import init_metrics_routes
from routes.article_routes import article_bp

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

def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name (str): The configuration to use ('development', 'testing', 'production')
        
    Returns:
        tuple: (app, socketio) - Flask application and SocketIO instance
    """
    # Initialize the Flask application
    app = Flask(__name__, static_folder='../frontend/build', static_url_path='/static')
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from extensions import init_extensions, db, socketio, login_manager
    init_extensions(app)
    
    # Register teardown handler
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
    
    # Initialize metrics service
    from service.metrics_service import metrics_service
    metrics_service.initialize(app)  # Pass app for any route registration

    # Register blueprints for the API endpoints
    # Each blueprint encapsulates a specific domain of functionality
    app.register_blueprint(dosha_blueprint, url_prefix='/api/dosha')
    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(article_bp, url_prefix='')
    
    # Initialize metrics routes with socketio
    metrics_bp = init_metrics_routes(socketio)
    app.register_blueprint(metrics_bp, url_prefix='/api/metrics')

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
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain

    # Create the document chain
    combine_docs_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=prompt,
        document_variable_name="context"
    )

    # Create the RAG chain
    rag_chain = create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=combine_docs_chain
    )

    return app, socketio, rag_chain

# -------------------------------------------------------------------------
# Main Application Routes
# -------------------------------------------------------------------------

# Create the application instance
app, socketio, rag_chain = create_app()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

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
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Invalid request body'}), 400
            
        msg = data['message']
        start_time = time.time()
        
        # Get response from RAG chain
        response = rag_chain.invoke({"input": msg})
        response_time = time.time() - start_time
        
        # Track metrics if metrics_service is available
        if hasattr(metrics_service, 'track_rag_request'):
            metrics_service.track_rag_request(
                response_time,
                response.get("metrics", {}).get("tool_usage", {})
            )
        
        answer = response.get("answer", "")
        
        # Fallback to Google search if the local context was insufficient
        if not answer or any(phrase in answer.lower() for phrase in ["don't know", "i don't have"]):
            google_result = execute_google_search(msg)
            answer = f"Based on my search: {google_result}"
        
        print(f"Response: {answer}")
        
        # Track diseases and remedies mentioned in the conversation
        if 'tracked_diseases' in globals():
            track_disease(msg, answer)
            track_remedy(msg, answer)
        
        # Return the response to the client
        return jsonify({"response": answer})
        
    except Exception as e:
        print(f'Error in chat endpoint: {str(e)}')
        return jsonify({"error": "Internal server error while processing your message. Please try again later."}), 500

def track_remedy(user_msg, bot_answer):
    """
    Track remedies mentioned in the conversation.
    
    This function extracts and stores remedies from the bot's responses
    for later reference and analysis.
    
    Args:
        user_msg (str): The user's message
        bot_answer (str): The bot's response
    """
    # Simple extraction of remedies (can be enhanced with NLP)
    remedies = []
    
    # Look for common remedy patterns
    if "take" in bot_answer.lower() or "try" in bot_answer.lower():
        # Simple pattern matching - in a real app, use NLP for better extraction
        remedies = re.findall(r'(?:take|try|use|apply)\s+([^.,;]+?)(?=[.,;]|$)', bot_answer, re.IGNORECASE)
    
    if remedies:
        # Clean up the extracted remedies
        remedies = [r.strip() for r in remedies if len(r.strip()) > 10]  # Filter out very short matches
        
        # Store in tracked_diseases under a general category
        if 'general_remedies' not in tracked_diseases:
            tracked_diseases['general_remedies'] = {
                'count': 0,
                'remedies': [],
                'full_responses': []
            }
        
        tracked_diseases['general_remedies']['count'] += 1
        tracked_diseases['general_remedies']['remedies'].extend(remedies)
        tracked_diseases['general_remedies']['full_responses'].append(bot_answer)
        
        # Also associate with specific diseases if mentioned in the user's message
        for disease in tracked_diseases:
            if disease.lower() in user_msg.lower() and disease != 'general_remedies':
                if disease not in tracked_diseases:
                    tracked_diseases[disease] = {
                        'full_responses': [],
                        'remedies': []
                    }
                tracked_diseases[disease]['remedies'].extend(remedies)
                if any(re.search(pattern, bot_answer) for pattern in remedy_patterns):
                    # Add to remedies if not already present
                    if bot_answer not in tracked_diseases[disease]['remedies']:
                        tracked_diseases[disease]['remedies'].append(bot_answer)

@app.route("/api/agent", methods=["GET", "POST"])
def agent_chat():
    """
    Agent chat endpoint that processes user messages using the agentic framework.
    
    Returns:
        JSON response with the agent's output and metrics
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
            
        msg = data.get("message")
        start_time = time.time()
        
        # Create a tool calling agent with the available tools
        agent = create_tool_calling_agent(
            llm=ChatOpenAI(
                openai_api_base="https://api.groq.com/openai/v1",
                model_name="llama-3.3-70b-versatile",
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.4,
                max_tokens=1024),
            tools=agent_service.tools,
            prompt=prompt
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=agent_service.tools,
            verbose=True
        )
        
        # Get response
        response = agent_executor.invoke({"input": msg})
        
        response_time = time.time() - start_time
        
        # Track metrics if metrics_service is available
        if hasattr(metrics_service, 'track_agent_request'):
            metrics_service.track_agent_request(
                response_time,
                response.get("metrics", {}).get("tool_usage", {})
            )
        
        return jsonify({
            "response": response.get("output", ""),
            "metrics": response.get("metrics", {})
        })
        
    except Exception as e:
        print(f'Error in agent chat endpoint: {str(e)}')
        return jsonify({"error": "Internal server error while processing your message with the agent."}), 500

@app.route('/api/metrics/comparison', methods=['GET'])
def get_comparison_metrics():
    """
    Get comparison metrics between RAG and Agent implementations.
    
    Returns:
        JSON response with performance comparison metrics
    """
    try:
        if hasattr(metrics_service, 'get_comparison_metrics'):
            return jsonify(metrics_service.get_comparison_metrics())
        return jsonify({"error": "Metrics service not available"}), 503
    except Exception as e:
        print(f'Error getting comparison metrics: {str(e)}')
        return jsonify({"error": "Failed to retrieve metrics"}), 500

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
    try:
        # Check if tracked_diseases exists
        if 'tracked_diseases' not in globals():
            return jsonify({"error": "No remedies data available"}), 404
            
        # Create a simplified version of tracked_diseases for the frontend
        simplified_remedies = {}
        
        for disease, data in tracked_diseases.items():
            # If we have specific remedies extracted, use those
            if data.get('remedies'):
                simplified_remedies[disease] = data['remedies']
            # Otherwise fall back to full responses
            elif data.get('full_responses'):
                simplified_remedies[disease] = data['full_responses']
        
        return jsonify(simplified_remedies)
        
    except Exception as e:
        print(f'Error retrieving remedies: {str(e)}')
        return jsonify({"error": "Failed to retrieve remedies"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring and orchestration."""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Create application instance
    app, socketio = create_app()
    
    # Get configuration from app
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    
    # Log startup information
    print(f"Starting Ayurveda AI Backend on port {port} (debug={debug})")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    # Run the application with Socket.IO
    socketio.run(app, 
                host='0.0.0.0', 
                port=port, 
                debug=debug,
                use_reloader=debug)