"""
Enhanced Recommendation Service

This module provides personalized Ayurvedic recommendations by combining:
- Vector similarity search
- User preferences and history
- Contextual information (weather, time, etc.)
- Collaborative filtering
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging
from dotenv import load_dotenv

# Database
from .database import get_session
from .models import User, UserPreference, Interaction

# Vector store
from pinecone.grpc import PineconeGRPC as Pinecone
from langchain_pinecone import PineconeVectorStore

# Embeddings
from .helper import download_hugging_face_embeddings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


class RecommendationService:
    """
    Service for generating personalized Ayurvedic recommendations.
    """
    
    def __init__(self, user_id: Optional[str] = None):
        """Initialize the recommendation service.
        
        Args:
            user_id: Optional user ID for personalized recommendations
        """
        self.user_id = user_id
        self.embeddings = download_hugging_face_embeddings()
        self.vector_store = self._init_vector_store()
        self.session = get_session()
    
    def _init_vector_store(self):
        """Initialize the Pinecone vector store."""
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index_name = "herbbot"
        return PineconeVectorStore(
            index=pc.Index(index_name),
            embedding=self.embeddings,
            text_key="text"
        )
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from the database."""
        if not self.user_id:
            return {}
            
        try:
            user = self.session.query(User).filter_by(id=self.user_id).first()
            if not user:
                return {}
                
            preferences = {pref.key: pref.value 
                         for pref in user.preferences}
            
            # Get recent interactions
            interactions = self.session.query(Interaction)\
                .filter_by(user_id=self.user_id)\
                .order_by(Interaction.timestamp.desc())\
                .limit(10)\
                .all()
                
            return {
                'preferences': preferences,
                'recent_interactions': [
                    {
                        'content': i.content[:200],
                        'interaction_type': i.interaction_type,
                        'timestamp': i.timestamp.isoformat()
                    } for i in interactions
                ]
            }
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    def get_personalized_recommendations(
        self,
        query: Optional[str] = None,
        dosha: Optional[str] = None,
        season: Optional[str] = None,
        time_of_day: Optional[str] = None,
        health_concern: Optional[str] = None,
        weather_data: Optional[Dict] = None,
        top_k: int = 5,
        personalization_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations based on multiple factors.
        
        Args:
            query: User's search query
            dosha: User's dosha type
            season: Current season
            time_of_day: Current time of day
            health_concern: Specific health concern
            weather_data: Current weather data
            top_k: Number of recommendations to return
            personalization_weight: Weight for personalization (0-1)
            
        Returns:
            List of recommendation dictionaries with metadata
        """
        try:
            # Get user preferences and history
            user_context = self.get_user_preferences()
            
            # Generate the base query
            base_query = generate_embedding_query(
                dosha=dosha,
                weather_data=weather_data,
                query=query,
                health_concern=health_concern,
                season=season,
                time_of_day=time_of_day
            )
            
            # Add personalization context
            personalized_query = self._add_personalization_context(
                base_query, 
                user_context
            )
            
            # Get embeddings for both queries
            base_embedding = self.embeddings.embed_query(base_query)
            personalized_embedding = self.embeddings.embed_query(personalized_query)
            
            # Get more results than needed for diversity
            base_results = self.vector_store.similarity_search_by_vector(
                embedding=base_embedding,
                k=top_k * 3  # Get more for diversity
            )
            
            personal_results = self.vector_store.similarity_search_by_vector(
                embedding=personalized_embedding,
                k=top_k * 2
            )
            
            # Combine and rank results
            recommendations = self._rank_recommendations(
                base_results, 
                personal_results,
                personalization_weight
            )
            
            # Add personalization metadata
            for rec in recommendations:
                rec['personalized'] = rec.get('source', '') in [
                    r.metadata.get('source') for r in personal_results[:top_k]]
            
            return recommendations[:top_k]
            
        except Exception as e:
            logger.error(f"Error in get_personalized_recommendations: {e}")
            # Fallback to non-personalized recommendations
            return self._get_fallback_recommendations(
                base_query, 
                top_k
            )
    
    def _add_personalization_context(
        self, 
        base_query: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Enhance the query with personalization context."""
        if not user_context or not user_context.get('preferences'):
            return base_query
            
        # Add preferences to query
        prefs = user_context['preferences']
        personal_context = []
        
        if prefs.get('dietary_restrictions'):
            personal_context.append(f"Dietary restrictions: {prefs['dietary_restrictions']}")
            
        if prefs.get('health_goals'):
            personal_context.append(f"Health goals: {prefs['health_goals']}")
            
        # Add recent interactions
        if user_context.get('recent_interactions'):
            recent_topics = set()
            for interaction in user_context['recent_interactions']:
                # Simple topic extraction (in a real app, use NLP)
                words = interaction['content'].lower().split()[:10]
                recent_topics.update(words)
            
            if recent_topics:
                personal_context.append(
                    f"Recently interested in: {', '.join(recent_topics)}"
                )
        
        if not personal_context:
            return base_query
            
        return f"{base_query}. Personal context: {'; '.join(personal_context)}"
    
    def _rank_recommendations(
        self, 
        base_results: List[Any], 
        personal_results: List[Any],
        personalization_weight: float
    ) -> List[Dict[str, Any]]:
        """Rank recommendations by combining base and personalized results."""
        # Create a scoring dictionary
        scores = {}
        
        # Score base results (higher score = better)
        for i, doc in enumerate(base_results):
            doc_id = doc.metadata.get('id') or id(doc)
            scores[doc_id] = {
                'doc': doc,
                'score': 1.0 - (i * 0.1),  # Linear decay
                'source': 'base'
            }
        
        # Boost personal results
        for i, doc in enumerate(personal_results):
            doc_id = doc.metadata.get('id') or id(doc)
            if doc_id in scores:
                scores[doc_id]['score'] += personalization_weight * (1.0 - (i * 0.1))
                scores[doc_id]['source'] = 'both'
            else:
                scores[doc_id] = {
                    'doc': doc,
                    'score': personalization_weight * (1.0 - (i * 0.1)),
                    'source': 'personal'
                }
        
        # Sort by score
        ranked = sorted(
            scores.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )
        
        # Format results
        recommendations = []
        for i, item in enumerate(ranked):
            doc = item['doc']
            content = getattr(doc, 'page_content', str(doc))
            metadata = getattr(doc, 'metadata', {})
            
            recommendations.append({
                'content': content,
                'source': metadata.get('source', 'Unknown'),
                'relevance_score': item['score'],
                'classification': classify_recommendation(content),
                'metadata': {
                    'dosha': metadata.get('dosha', ''),
                    'category': metadata.get('category', ''),
                    'source_url': metadata.get('source_url', ''),
                    'recommendation_source': item['source']
                }
            })
        
        return recommendations
    
    def _get_fallback_recommendations(
        self, 
        query: str, 
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Fallback to simple similarity search if personalization fails."""
        try:
            query_embedding = self.embeddings.embed_query(query)
            results = self.vector_store.similarity_search_by_vector(
                embedding=query_embedding,
                k=top_k
            )
            
            return [{
                'content': doc.page_content,
                'source': doc.metadata.get('source', 'Unknown'),
                'relevance_score': 1.0 - (i * 0.1),
                'classification': classify_recommendation(doc.page_content),
                'metadata': doc.metadata,
                'fallback': True
            } for i, doc in enumerate(results)]
            
        except Exception as e:
            logger.error(f"Fallback recommendation failed: {e}")
            return []
    
    def log_interaction(
        self, 
        content: str, 
        interaction_type: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Log a user interaction for future personalization."""
        if not self.user_id:
            return
            
        try:
            interaction = Interaction(
                user_id=self.user_id,
                content=content[:1000],  # Limit size
                interaction_type=interaction_type,
                metadata=metadata or {},
                timestamp=datetime.utcnow()
            )
            self.session.add(interaction)
            self.session.commit()
        except Exception as e:
            logger.error(f"Error logging interaction: {e}")
            self.session.rollback()


# For backward compatibility
def get_recommendations(
    query=None, 
    dosha=None, 
    season=None, 
    time_of_day=None, 
    health_concern=None, 
    weather_data=None, 
    top_k=5
):
    """
    Wrapper for backward compatibility.
    """
    service = RecommendationService()
    return service.get_personalized_recommendations(
        query=query,
        dosha=dosha,
        season=season,
        time_of_day=time_of_day,
        health_concern=health_concern,
        weather_data=weather_data,
        top_k=top_k
    )
