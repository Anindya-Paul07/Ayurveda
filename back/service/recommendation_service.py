import os
from dotenv import load_dotenv

# Import PineconeGRPC class to establish connection with Pinecone services
from pinecone.grpc import PineconeGRPC as Pinecone

# Import PineconeVectorStore to interact with the Pinecone index
from langchain_pinecone import PineconeVectorStore

# Import helper function to download embeddings for text conversion
from back.service.helper import download_hugging_face_embeddings

# Load environment variables from a .env file
load_dotenv()

# Retrieve the Pinecone API key from environment variables
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
# Ensure the API key is available as an environment variable
os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY


def generate_embedding_query(dosha=None, weather_data=None, query=None, health_concern=None, season=None, time_of_day=None):
    """
    Constructs a comprehensive query string incorporating various Ayurvedic parameters.
    
    Args:
        dosha (str, optional): The user's dominant dosha type (Vata, Pitta, Kapha).
        weather_data (dict, optional): Current weather conditions including temperature, humidity, etc.
        query (str, optional): The user's original query or search terms.
        health_concern (str, optional): Specific health issue or concern.
        season (str, optional): Current season (Spring, Summer, Monsoon, Autumn, Winter).
        time_of_day (str, optional): Time period (Morning, Afternoon, Evening, Night).
        
    Returns:
        str: A detailed query string combining all provided parameters.
    """
    query_parts = []
    
    # Add the original query if provided
    if query:
        query_parts.append(query)
    
    # Add dosha information
    if dosha:
        query_parts.append(f"Recommendations for {dosha} dosha")
    
    # Add health concern
    if health_concern:
        query_parts.append(f"Addressing {health_concern}")
    
    # Add seasonal context
    if season:
        query_parts.append(f"During {season} season")
    
    # Add time of day context
    if time_of_day:
        query_parts.append(f"For {time_of_day}")
    
    # Process weather data if available
    if weather_data:
        weather_desc = []
        if 'temperature' in weather_data:
            temp = weather_data['temperature']
            if temp > 30:
                weather_desc.append("hot weather")
            elif temp < 15:
                weather_desc.append("cold weather")
            else:
                weather_desc.append("moderate temperature")
                
        if 'humidity' in weather_data:
            humidity = weather_data['humidity']
            if humidity > 70:
                weather_desc.append("high humidity")
            elif humidity < 30:
                weather_desc.append("dry conditions")
                
        if weather_desc:
            query_parts.append(f"Suitable for {', '.join(weather_desc)}")
    
    # Combine all parts into a comprehensive query
    comprehensive_query = ". ".join(query_parts)
    
    return comprehensive_query


def classify_recommendation(content):
    """
    Analyzes the content of a recommendation and classifies it as 'food', 'lifestyle', or 'general'.
    
    Args:
        content (str): The text content of the recommendation.
        
    Returns:
        str: Classification category ('food', 'lifestyle', or 'general').
    """
    content_lower = content.lower()
    
    # Define keyword sets for each category
    food_keywords = [
        'food', 'diet', 'meal', 'eat', 'eating', 'nutrition', 'consume', 'dish', 'recipe',
        'fruit', 'vegetable', 'spice', 'herb', 'grain', 'dairy', 'ghee', 'oil',
        'breakfast', 'lunch', 'dinner', 'snack', 'drink', 'beverage', 'tea'
    ]
    
    lifestyle_keywords = [
        'exercise', 'yoga', 'meditation', 'sleep', 'routine', 'habit', 'practice',
        'activity', 'rest', 'massage', 'bath', 'oil', 'abhyanga', 'lifestyle',
        'morning', 'evening', 'ritual', 'cleanse', 'detox', 'breathing', 'pranayama'
    ]
    
    # Count keyword occurrences
    food_count = sum(1 for keyword in food_keywords if keyword in content_lower)
    lifestyle_count = sum(1 for keyword in lifestyle_keywords if keyword in content_lower)
    
    # Determine classification based on keyword counts
    if food_count > lifestyle_count:
        return 'food'
    elif lifestyle_count > food_count:
        return 'lifestyle'
    else:
        return 'general'


def get_recommendations(query=None, dosha=None, season=None, time_of_day=None, 
                       health_concern=None, weather_data=None, top_k=5):
    """
    Perform a similarity search on the Pinecone index 'herbbot' using a comprehensive query
    generated from multiple parameters. Returns the top_k matching Ayurvedic recommendations
    with relevance scores and classifications.

    Args:
        query (str, optional): The user's original query or search terms.
        dosha (str, optional): The user's dominant dosha type (Vata, Pitta, Kapha).
        season (str, optional): Current season (Spring, Summer, Monsoon, Autumn, Winter).
        time_of_day (str, optional): Time period (Morning, Afternoon, Evening, Night).
        health_concern (str, optional): Specific health issue or concern.
        weather_data (dict, optional): Current weather conditions including temperature, humidity, etc.
        top_k (int, optional): Number of top recommendations to return. Defaults to 5.

    Returns:
        list: A list of dictionaries containing formatted recommendations with relevance scores and classifications.
    """
    # Generate a comprehensive query from all input parameters
    comprehensive_query = generate_embedding_query(
        dosha=dosha,
        weather_data=weather_data,
        query=query,
        health_concern=health_concern,
        season=season,
        time_of_day=time_of_day
    )
    
    # Download and initialize the embeddings model to convert text into vector embeddings
    embeddings = download_hugging_face_embeddings()

    # Initialize the connection to the existing Pinecone index 'herbbot'
    # This uses the embeddings to transform queries for similarity comparison
    vector_store = PineconeVectorStore.from_existing_index(
        index_name='herbbot',
        embedding=embeddings
    )
    
    # Perform a similarity search with scores using the comprehensive query
    raw_recommendations = vector_store.similarity_search_with_score(comprehensive_query, k=top_k)
    
    # Process and format the recommendations
    formatted_recommendations = []
    for doc, score in raw_recommendations:
        # Classify the recommendation
        classification = classify_recommendation(doc.page_content)
        
        # Format the recommendation
        recommendation = {
            'content': doc.page_content,
            'metadata': doc.metadata,
            'relevance_score': float(score),  # Convert to float for JSON serialization
            'classification': classification
        }
        
        formatted_recommendations.append(recommendation)
    
    # Sort recommendations by relevance score (descending)
    formatted_recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # Return the formatted and sorted recommendations
    return formatted_recommendations
