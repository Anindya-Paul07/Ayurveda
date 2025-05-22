"""
Agent Service Module

This module implements an agentic RAG chain that uses LangChain's Agent framework
with multiple tools for different capabilities. It maintains compatibility with
the existing RAG chain interface while providing enhanced reasoning capabilities.
"""

import time
import traceback
from typing import Dict, Any, List, Optional, Union, Tuple
import json
import time
from datetime import datetime
import logging

from langchain.agents import AgentExecutor, Tool
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI


from .conversation_memory import ConversationMemory
from .context_manager import ContextManager
from .herb_recommender import HerbRecommender
from .symptom_analyzer import SymptomAnalyzer
from .dosha_calculator import DoshaCalculator
# VectorStoreTool is defined in this file, so no need to import it
from .tool_usage_tracker import ToolUsageTracker
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
from .article_service import ArticleTool, ArticleAgent
import json
import os
import logging

# Load environment variables first
load_dotenv()

# Import database functions after environment is loaded
from .database import init_db, get_db_session

# Initialize database
DB_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/ayurveda')
init_db(DB_URL)

# Get Pinecone API key
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Import helper functions after environment is set up
from .helper import download_hugging_face_embeddings

# Initialize Pinecone vector store
index_name = "herbbot"
embeddings = download_hugging_face_embeddings()
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

# Create retriever with similarity search
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

from .helper import download_hugging_face_embeddings

from .google_search import execute_google_search
from .weather_service import get_weather_data as get_current_weather
from .dosha_tool import DoshaTool as NewDoshaTool
from .dosha_service import determine_dosha
from .herb_recommender import HerbRecommender
from .symptom_analyzer import SymptomAnalyzer
from .tool_usage_tracker import ToolUsageTracker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SymptomAnalyzerTool(BaseTool):
    """Tool for analyzing symptoms and suggesting potential dosha imbalances."""
    name: str = "symptom_analyzer"
    description: str = """Useful for when you need to analyze symptoms and suggest potential dosha imbalances.
    Input should be a JSON string with the following fields:
    - symptoms: List of symptoms the user is experiencing
    - existing_conditions: List of any existing health conditions (optional)
    - current_treatments: List of current treatments or medications (optional)
    - lifestyle_factors: List of relevant lifestyle factors (optional)
    """
    
    def _run(self, query: str) -> str:
        """Run the tool."""
        try:
            import json
            from .symptom_analyzer import SymptomAnalyzer
            
            # Parse the input query as JSON
            params = json.loads(query)
            
            # Extract parameters with defaults
            symptoms = params.get('symptoms', []),
            existing_conditions = params.get('existing_conditions', [])
            current_treatments = params.get('current_treatments', [])
            lifestyle_factors = params.get('lifestyle_factors', [])
            
            if not symptoms:
                return "Error: No symptoms provided for analysis."
            
            # Initialize and run the symptom analyzer
            analyzer = SymptomAnalyzer()
            result = analyzer.analyze_symptoms(symptoms)
            
            # Format the response
            response = ["## Symptom Analysis Results\n"]
            
            if result["primary_dosha"]:
                dosha = result['primary_dosha'].lower()
                response.append(f"### Primary Dosha Imbalance: {result['primary_dosha'].title()} "
                              f"(Confidence: {result['confidence']*100:.1f}%)")
                
                # Add general information about the dosha
                try:
                    search_query = f"Ayurveda {dosha} dosha characteristics and balancing"
                    search_results = execute_google_search(search_query, num_results=3)
                    
                    if search_results:
                        response.append("\n**About This Dosha:**")
                        for i, res in enumerate(search_results[:2], 1):  
                            response.append(f"{i}. {res['title']} - {res['link']}")
                        response.append("\n*Note: Please consult an Ayurvedic practitioner for personalized advice.*")
                except Exception as e:
                    logger.warning(f"Error fetching dosha information: {str(e)}")
                
                if result['matched_symptoms'].get(dosha):
                    response.append("\n**Matching Symptoms:**")
                    for symptom in result['matched_symptoms'][result['primary_dosha'].lower()]:
                        response.append(f"- {symptom}")
                
                if result['recommendations']:
                    response.append("\n**Recommendations:**")
                    for i, rec in enumerate(result['recommendations'], 1):
                        response.append(f"{i}. {rec}")
                
                
                if result['secondary_dosha'] and result['secondary_dosha'] != result['primary_dosha']:
                    response.append(f"\n### Secondary Dosha Imbalance: {result['secondary_dosha']}")
                    if result['matched_symptoms'].get(result['secondary_dosha'].lower()):
                        response.append("\n**Matching Symptoms:**")
                        for symptom in result['matched_symptoms'][result['secondary_dosha'].lower()]:
                            response.append(f"- {symptom}")
            else:
                response.append("No clear dosha imbalance detected from the provided symptoms.")
            
            response.append("\n*Note: This is a preliminary analysis. For a complete assessment, "
                          "please consult with an Ayurvedic practitioner.*")
            
            return "\n".join(response)
            
        except json.JSONDecodeError:
            return "Error: Invalid JSON input. Please provide a valid JSON string with the required fields."
        except Exception as e:
            return f"Error analyzing symptoms: {str(e)}"

class VectorStoreTool(BaseTool):
    """Tool for searching and retrieving relevant documents from the vector store.
    
    This tool provides advanced search capabilities over the Ayurvedic knowledge base,
    including semantic search, relevance scoring, and document analysis.
    """
    name: str = "vector_store_search"
    description: str = """
    Use this tool to search the vector store for relevant documents.
    
    Input should be a clear search query related to Ayurveda, herbs, symptoms, or treatments.
    The tool will return the most relevant documents along with metadata and relevance scores.
    """
    
    def _get_vector_store_context(self, query: str, k: int = 3) -> dict:
        """
        Retrieve relevant context from the vector store based on the query.
        
        Args:
            query: The search query string
            k: Number of documents to retrieve (default: 3)
            
        Returns:
            dict: Dictionary containing documents, metadata, and analysis
        """
        start_time = time.time()
        try:
            if not query or not isinstance(query, str):
                raise ValueError("Query must be a non-empty string")
                
            if not hasattr(retriever, 'get_relevant_documents'):
                raise AttributeError("Retriever is not properly initialized")
            
            docs = retriever.get_relevant_documents(query, k=k)
            
            if not docs:
                logger.info(f"No documents found for query: {query}")
                return {'documents': [], 'metadata': {}, 'relevance_scores': []}
            
            context = {
                'documents': [],
                'metadata': {},
                'relevance_scores': [],
                'query': query,
                'retrieval_time': time.time() - start_time,
                'document_count': len(docs)
            }
            
            for idx, doc in enumerate(docs, 1):
                doc_id = doc.metadata.get('id', f'doc_{idx}')
                context['documents'].append({
                    'id': doc_id,
                    'content': doc.page_content,
                    'score': float(doc.score) if hasattr(doc, 'score') else 0.0
                })
                
                context['metadata'][doc_id] = {
                    'source': doc.metadata.get('source', 'unknown'),
                    'created_at': doc.metadata.get('created_at', 'unknown'),
                    'document_type': doc.metadata.get('type', 'general'),
                    'page_number': doc.metadata.get('page', 0)
                }
                
                if hasattr(doc, 'score'):
                    context['relevance_scores'].append(float(doc.score))
            
            context['analysis'] = self._analyze_semantic_similarity(docs)
            context['success'] = True
            
            return context
            
        except Exception as e:
            error_msg = f"Error retrieving vector store context: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                'error': error_msg,
                'success': False,
                'query': query,
                'retrieval_time': time.time() - start_time
            }

    def _get_topic_distribution(self, docs) -> dict:
        """
        Analyze and extract topic distribution from retrieved documents.
        
        This method identifies key Ayurvedic topics, their relationships, and provides
        relevant treatment information based on the document content.
        
        Args:
            docs: List of Document objects to analyze
            
        Returns:
            dict: Structured topic distribution with relationships and treatments
        """
        if not docs:
            return {}
        
        try:
            # Define basic Ayurvedic topics
            ayurvedic_topics = {
                'dosha': {
                    'keywords': ['dosha', 'vata', 'pitta', 'kapha', 'tridosha'],
                    'related': ['prakriti', 'guna', 'rasa'],
                    'treatments': {
                        'diet': 'Balanced according to dosha type',
                        'lifestyle': 'Dosha-specific daily routine',
                        'herbs': 'Dosha-balancing herbs'
                    }
                },
                'prakriti': {
                    'keywords': ['prakriti', 'constitution', 'body type'],
                    'related': ['dosha', 'vata', 'pitta', 'kapha'],
                    'treatments': {
                        'assessment': 'Pulse and physical examination',
                        'lifestyle': 'Constitution-based recommendations'
                    }
                }
            }
            
            # Extract text from documents
            doc_text = " ".join([doc.page_content for doc in docs if hasattr(doc, 'page_content')]).lower()
            
            # Calculate topic scores
            topic_scores = {}
            for topic, data in ayurvedic_topics.items():
                score = 0
                # Score based on keywords
                for kw in data.get('keywords', []) + [topic]:
                    score += doc_text.count(kw.lower())
                # Add related terms with lower weight
                for related in data.get('related', []):
                    score += doc_text.count(related.lower()) * 0.5
                topic_scores[topic] = score
            
            # Normalize scores
            max_score = max(topic_scores.values()) if topic_scores else 1
            if max_score == 0:
                max_score = 1  # Avoid division by zero
                
            # Prepare result
            result = {
                'topics': {
                    topic: {
                        'score': score / max_score,
                        'normalized_score': round(score / max_score, 2)
                    }
                    for topic, score in topic_scores.items()
                },
                'primary_topic': max(topic_scores.items(), key=lambda x: x[1])[0] if topic_scores else None
            }
            
            # Add treatment recommendations for primary topic
            if result['primary_topic']:
                primary_topic = result['primary_topic']
                if primary_topic in ayurvedic_topics and 'treatments' in ayurvedic_topics[primary_topic]:
                    result['recommendations'] = ayurvedic_topics[primary_topic]['treatments']
            
            return result
            
        except Exception as e:
            logger.error(f"Error in topic distribution analysis: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'message': 'Failed to analyze topic distribution'
            }

    def _analyze_semantic_similarity(self, docs) -> dict:
        """
        Analyze semantic similarity between retrieved documents.
        
        Args:
            docs: List of Document objects from the vector store
            
        Returns:
            dict: Analysis including average similarity, most relevant doc, and topic distribution
        """
        if not docs:
            return {
                'error': 'No documents provided',
                'average_similarity': 0.0,
                'topic_distribution': {},
                'document_count': 0
            }
            
        try:
            # Calculate score statistics
            scores = [float(doc.score) for doc in docs if hasattr(doc, 'score')]
            avg_similarity = sum(scores) / len(scores) if scores else 0.0
            
            # Get most relevant document
            most_relevant = max(
                [doc for doc in docs if hasattr(doc, 'score')],
                key=lambda x: float(x.score),
                default=None
            )
            
            # Analyze topic distribution
            topic_distribution = self._analyze_topics(docs)
            
            # Prepare result
            result = {
                'average_similarity': avg_similarity,
                'score_distribution': {
                    'min': min(scores) if scores else 0.0,
                    'max': max(scores) if scores else 0.0,
                    'average': avg_similarity
                },
                'document_count': len(docs),
                'most_relevant': {
                    'content': getattr(most_relevant, 'page_content', '') if most_relevant else '',
                    'score': float(most_relevant.score) if most_relevant and hasattr(most_relevant, 'score') else 0.0,
                    'metadata': getattr(most_relevant, 'metadata', {}) if most_relevant else {}
                },
                'topic_analysis': topic_distribution
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in semantic similarity analysis: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'message': 'Failed to analyze documents',
                'average_similarity': 0.0,
                'document_count': len(docs)
            }
    
    def _analyze_topics(self, docs):
        """
        Analyze topics in the documents.
        
        Args:
            docs: List of Document objects
            
        Returns:
            dict: Topic analysis results
        """
        if not docs:
            return {}
            
        try:
            # Combine all document content
            doc_text = " ".join([doc.page_content for doc in docs if hasattr(doc, 'page_content')])
            doc_text = doc_text.lower()
            
            # Initialize topic analysis
            topic_analysis = {
                'topics': {},
                'primary_topic': None,
                'primary_subtopic': None,
                'topic_scores': {}
            }
            
            # Calculate topic relevance scores
            max_score = 0
            topic_scores = {}
            
            for topic, data in ayurvedic_topics.items():
                score = 0
                # Check for topic keywords
                keywords = data.get('keywords', []) + [topic]
                for kw in keywords:
                    score += doc_text.count(kw.lower())
                
                # Check for related terms
                for related in data.get('related', []):
                    score += doc_text.count(related.lower()) * 0.5
                
                # Process subtopics if they exist
                if 'subtopics' in data:
                    topic_scores[topic] = {}
                    topic_scores[topic]['_score'] = score
                    
                    for subtopic, subdata in data['subtopics'].items():
                        subtopic_score = 0
                        sub_keywords = subdata.get('keywords', []) + [subtopic]
                        for kw in sub_keywords:
                            subtopic_score += doc_text.count(kw.lower())
                        
                        score += subtopic_score * 1.5
                        topic_scores[topic][subtopic] = subtopic_score
                        
                        # Update max score
                        max_score = max(max_score, subtopic_score)
                
                # Update max score for standalone topics
                if topic not in topic_scores:
                    topic_scores[topic] = score
                    max_score = max(max_score, score)
            
            # Normalize scores and build result
            max_score = max(max_score, 1)  # Avoid division by zero
            
            for topic, scores in topic_scores.items():
                if isinstance(scores, dict):
                    # Topic with subtopics
                    topic_score = scores.pop('_score', 0) / max_score
                    topic_analysis['topics'][topic] = {
                        'score': topic_score,
                        'subtopics': {k: v/max_score for k, v in scores.items()}
                    }
                    
                    # Track primary topic/subtopic
                    if not topic_analysis['primary_topic'] or \
                       topic_score > topic_analysis['topics'].get(topic_analysis['primary_topic'], {}).get('score', 0):
                        topic_analysis['primary_topic'] = topic
                        
                        # Find primary subtopic
                        if scores:
                            primary_sub = max(scores.items(), key=lambda x: x[1])
                            topic_analysis['primary_subtopic'] = primary_sub[0]
                else:
                    # Standalone topic
                    topic_score = scores / max_score
                    topic_analysis['topics'][topic] = {'score': topic_score}
                    
                    # Track primary topic
                    if not topic_analysis['primary_topic'] or \
                       topic_score > topic_analysis['topics'].get(topic_analysis['primary_topic'], {}).get('score', 0):
                        topic_analysis['primary_topic'] = topic
            
            # Add treatment recommendations if primary topic is found
            if topic_analysis['primary_topic'] and topic_analysis['primary_topic'] in ayurvedic_topics:
                self._add_treatment_recommendations(topic_analysis, ayurvedic_topics[topic_analysis['primary_topic']])
            
            return topic_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing topics: {str(e)}", exc_info=True)
            return {
                'error': str(e),
                'message': 'Failed to analyze topics'
            }
    
    def _add_treatment_recommendations(self, topic_analysis, topic_data):
        """
        Add treatment recommendations to the topic analysis.
        
        Args:
            topic_analysis: The topic analysis dictionary to update
            topic_data: The topic data containing treatment information
        """
        if 'treatments' in topic_data:
            topic_analysis['recommendations'] = topic_data['treatments']
        
        # Add subtopic treatments if available
        if topic_analysis.get('primary_subtopic') and 'subtopics' in topic_data:
            subtopic_data = topic_data['subtopics'].get(topic_analysis['primary_subtopic'], {})
            if 'treatments' in subtopic_data:
                topic_analysis['recommendations'] = subtopic_data['treatments']
        
        return topic_analysis

    def _run(self, query: str) -> str:
        """Run the tool."""
        # Get vector store context
        context = self._get_vector_store_context(query)
        
        # Return context as string
        return json.dumps(context)

    async def _arun(self, query: str) -> str:
        """Async run."""
        raise NotImplementedError()

class GoogleSearchTool(BaseTool):
    """Tool for Google search."""
    name: str = "google_search"
    description: str = "Use this tool to search the web for additional information."
    
    def _run(self, query: str) -> str:
        """Run the tool."""
        return execute_google_search(query)

    async def _arun(self, query: str) -> str:
        """Async run."""
        raise NotImplementedError()

class WeatherTool(BaseTool):
    """Tool for weather information."""
    name: str = "weather"
    description: str = "Use this tool to get current weather information for a location."
    
    def _run(self, query: str) -> str:
        """Run the tool."""
        city = query.split()[0]
        return get_current_weather(city)

    async def _arun(self, query: str) -> str:
        """Async run."""
        raise NotImplementedError()

class DoshaTool(BaseTool):
    """Tool for dosha determination."""
    name: str = "dosha"
    description: str = "Use this tool to determine a person's dosha type based on responses."
    
    def _run(self, query: str) -> str:
        """Run the tool."""
        try:
            import json
            from typing import Dict, Any
            
            # Parse JSON string to dict
            try:
                responses: Dict[str, str] = json.loads(query)
            except json.JSONDecodeError as e:
                return json.dumps({
                    "error": "Invalid JSON format",
                    "details": str(e)
                })
        
        # Validate responses
            if not isinstance(responses, dict):
                return json.dumps({
                    "error": "Responses must be a JSON object"
                })
            
        # Ensure all values are strings
            if not all(isinstance(v, str) for v in responses.values()):
                return json.dumps({
                    "error": "All response values must be strings"
                })
        
        # Call the dosha calculator
            result = determine_dosha(responses)
            return json.dumps(result)
        
        except Exception as e:
            return json.dumps({
                "error": "Error processing dosha calculation",
                "details": str(e)
            })

class RecommendationTool(BaseTool):
    """Tool for getting recommendations."""
    name: str = "recommendations"
    description: str = "Use this tool to get personalized recommendations based on parameters."
    
    def _run(self, query: str) -> str:
        """Run the tool."""
        params = eval(query)  # TODO: Proper parsing
        return get_recommendations(params)

    async def _arun(self, query: str) -> str:
        """Async run."""
        raise NotImplementedError()

class AgentService:
    """
    Enhanced Agent Service with integrated article recommendations and tool tracking.
    
    This service provides an agentic interface with support for Ayurvedic knowledge,
    article recommendations, and comprehensive tool usage tracking.
    """
    
    def __init__(self, user_id: str = "default_user"):
        
        """
        Initialize the AgentService with tools, memory, and article integration.
        
        Args:
            user_id: Unique identifier for the user session
        """
        self.user_id = user_id
        self.llm = ChatOpenAI(
            openai_api_base="https://api.groq.com/openai/v1",
            model_name="llama-3.2-70b-instruct",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.4,
            max_tokens=1024
        )
        
        # Initialize article agent and tool
        self.article_agent = ArticleAgent()
        self.article_tool = ArticleTool()
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Initialize memory and context with enhanced configuration
        self.memory = ConversationMemory(
            user_id=user_id,
            persist_dir="./data/conversations",
            max_messages=30,  # Increased from 20
            max_tokens=6000    # Increased from 4000
        )
        
        # Initialize context manager with expanded capacity
        self.context_manager = ContextManager(
            max_tokens=4500,  # Increased from 3500
            max_messages=20,  # Increased from 15
            min_recent_messages=5  # Increased from 3
        )
        
        # Initialize tool usage tracker with persistent storage
        self.usage_tracker = ToolUsageTracker(
            storage_path=f"./data/usage/tool_usage_{user_id}.json"
        )
        
        # Initialize metrics
        self.metrics = self._initialize_metrics()
        
        # Track tool usage patterns
        self.tool_usage_patterns = {}
        self.last_tool_used = None
        
        # Create the agent executor
        self.executor = self._create_agent_executor()
        
        # Add system message to context
        self._add_system_context()
        
        # Log service initialization
        logger.info(f"Initialized AgentService for user: {user_id}")
    
    def _add_system_context(self) -> None:
        """Add system context to the conversation."""
        system_context = """
        You are an Ayurvedic health assistant. Your goal is to provide helpful, accurate, 
        and personalized Ayurvedic advice while maintaining a warm and professional tone.
        
        Guidelines:
        - Always prioritize user safety and well-being
        - Provide evidence-based Ayurvedic recommendations
        - Acknowledge the limitations of your knowledge
        - Encourage users to consult qualified healthcare professionals for serious conditions
        - Be culturally sensitive and respectful
        - Maintain context across multiple messages
        - Ask clarifying questions when needed
        - Keep responses concise and focused
        """
        self.context_manager.add_message(
            role='system',
            content=system_context.strip()
        )
    
    def _initialize_tools(self) -> List[BaseTool]:
        """
        Initialize and configure all available tools for the agent.
        
        Returns:
            List of initialized tool instances
        """
        tools = [
            VectorStoreTool(),
            SymptomAnalyzerTool(),
            GoogleSearchTool(),
            WeatherTool(),
            DoshaTool(),
            RecommendationTool(),
            Tool(
                name="article_recommender",
                func=self._handle_article_recommendation,
                description="""
                Use this tool to find and recommend relevant Ayurveda articles.
                Input should be a JSON string with fields:
                - query: Search query (optional)
                - categories: List of categories (e.g., ['herbs', 'yoga', 'diet'])
                - max_results: Maximum number of results (default: 5)
                - user_id: Optional user ID for personalization
                """
            )
        ]
        
        # Log tool initialization
        tool_names = ", ".join([tool.name for tool in tools])
        logger.info(f"Initialized tools: {tool_names}")
        
        return tools
    
    def _initialize_metrics(self) -> Dict[str, Any]:
        """
        Initialize and configure performance and usage metrics.
        
        Returns:
            Dictionary containing initialized metrics
        """
        return {
            "total_requests": 0,
            "total_tool_calls": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "avg_response_time": 0.0,  # in milliseconds
            "unique_tools_used": set(),
            "article_recommendations": 0,
            "article_views": 0,
            "article_interactions": 0,
            "tool_usage_patterns": {},
            "session_start_time": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    def get_article_metrics(self, article_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for article interactions.
        
        Args:
            article_id: Optional article ID to get metrics for
            
        Returns:
            Dictionary containing article metrics
        """
        return self.usage_tracker.get_article_metrics(article_id)
    
    def get_user_engagement(self, days: int = 30) -> Dict[str, Any]:
        """
        Get user engagement metrics.
        
        Args:
            days: Number of days of data to include
            
        Returns:
            Dictionary containing user engagement data
        """
        return self.usage_tracker.get_user_engagement(
            user_id=self.user_id,
            days=days
        )
    
    def get_article_recommendations(
        self,
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        limit: int = 5,
        exclude_viewed: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get personalized article recommendations.
        
        Args:
            query: Search query (optional)
            categories: List of categories to filter by
            limit: Maximum number of recommendations to return
            exclude_viewed: Whether to exclude previously viewed articles
            
        Returns:
            List of recommended articles with metadata
        """
        return self.usage_tracker.get_article_recommendations(
            user_id=self.user_id,
            limit=limit,
            exclude_viewed=exclude_viewed
        )
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create and configure the agent executor with enhanced context handling."""
        from langchain.agents import initialize_agent, AgentType
        from .prompt import prompt

        
        system_message = SystemMessage(
            content="""You are a knowledgeable Ayurvedic health assistant with access to various tools. 
            Your goal is to provide accurate, helpful, and personalized Ayurvedic advice.
            
            Guidelines:
            1. Always consider the full conversation context when responding
            2. If the user refers to previous messages, acknowledge and address them appropriately
            3. Use the available tools when specific information is needed
            4. Be concise but thorough in your explanations
            5. If you're unsure about something, say so and offer to help find the information
            6. Maintain a warm, professional, and culturally sensitive tone
            7. Always prioritize user safety and well-being
            """
        )
        
        # Initialize the LLM with appropriate settings
        llm = ChatOpenAI(
            openai_api_base="https://api.groq.com/openai/v1",
            model_name="llama-3.2-70b-instruct",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.4,
            max_tokens=1024,
            request_timeout=30
        )
        
        # Create the agent with enhanced configuration
        agent = initialize_agent(
            tools=self.tools,
            llm=llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            memory=self.memory,
            agent_kwargs={
                'system_message': system_message,
                'extra_prompt_messages': [prompt],
                'handle_parsing_errors': True
            },
            return_intermediate_steps=True
        )
        
        return agent
    
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input through the agentic RAG chain with enhanced memory and context.
        
        Args:
            input_data: Dictionary containing:
                - message: The user's message (required)
                - session_id: Optional session ID to switch to
                - metadata: Additional metadata to store with the message
                
        Returns:
            Dictionary containing:
                - response: The AI's response
                - session_id: Current session ID
                - metadata: Additional response metadata
                - metrics: Performance and usage metrics
        """
        start_time = time.time()
        
        try:
            # Update metrics
            self.metrics["total_requests"] += 1
            
            # Switch session if requested
            if 'session_id' in input_data and input_data['session_id'] != self.memory.session_id:
                self.switch_session(input_data['session_id'])
            
            # Enhance user message with context
            enhanced_input = self._enhance_with_context(input_data["message"])
            
            # Generate response using enhanced input
            response = self._generate_response(enhanced_input)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Process tool usage and update context
            tool_data = self._process_tool_usage(response, duration_ms)
            
            # Add assistant response to context
            self.context_manager.add_message(
                role='assistant',
                content=response.get('output', ''),
                tool_calls=tool_data['tool_calls'],
                tool_results=tool_data['tool_results']
            )
            
            # Update conversation summary if needed
            if len(self.context_manager.conversation_history) >= 8:  # Update summary every 8 messages
                summary = self._generate_conversation_summary()
                self.context_manager.update_summary(summary)
            
            # Prepare response
            response_data = {
                'response': response.get('output', ''),
                'session_id': self.memory.session_id,
                'metadata': {
                    'tool_calls': tool_data['tool_calls'],
                    'tool_results': tool_data['tool_results'],
                    'context_used': enhanced_input.get('context', []),
                    'is_follow_up': enhanced_input.get('is_follow_up', False),
                    'referenced_message': enhanced_input.get('referenced_message'),
                    'message_id': str(hash(datetime.now())),
                    'timestamp': datetime.now().isoformat(),
                    'fallback_used': response.get('fallback_used', False)
                },
                'metrics': {
                    'response_time_ms': duration_ms,
                    'tool_usage': tool_data['tool_usage'],
                    'tool_stats': {
                        tool.name: {
                            'total_invocations': self.usage_tracker.get_stats(tool_name=tool.name)['total_invocations'],
                            'success_rate': self.usage_tracker.get_stats(tool_name=tool.name)['success_rate'],
                            'avg_duration_ms': self.usage_tracker.get_stats(tool_name=tool.name)['avg_duration_ms']
                        } for tool in self.tools
                    },
                    'avg_response_time_ms': (
                        (self.metrics["total_time"] + duration_ms) / self.metrics["total_requests"]
                        if self.metrics["total_requests"] > 0 else 0
                    )
                }
            }
            
            # Update metrics
            self.metrics["total_time"] += duration_ms
            
            # Save to conversation memory
            try:
                self.memory.save_context(
                    {"input": input_data["message"]},
                    {
                        "output": response_data["response"],
                        "metadata": {
                            "timestamp": datetime.now().isoformat(),
                            "user_id": self.user_id,
                            "session_id": self.memory.session_id,
                            "fallback_used": response.get("fallback_used", False)
                        }
                    }
                )
            except Exception as save_error:
                logger.error(f"Failed to save conversation context: {str(save_error)}")
            
            return response_data
            
        except Exception as e:
            # Record failed invocation
            self.usage_tracker.record_invocation(
                tool_name="agent",
                duration_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e),
                input_tokens=len(input_data["message"].split()) if "message" in input_data else 0,
                metadata={
                    "user_id": self.user_id,
                    "input": input_data.get("message", "")[:500],
                    "error": str(e)
                }
            )
            
            logger.error(f"Error in agent service: {str(e)}", exc_info=True)
            
            # Record the error in conversation context
            error_context = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "user_id": self.user_id,
                "session_id": getattr(self.memory, 'session_id', 'unknown'),
                "stack_trace": traceback.format_exc()
            }
            
            # Save error to conversation history if possible
            if hasattr(self, 'memory') and hasattr(self.memory, 'save_context'):
                try:
                    self.memory.save_context(
                        {"input": input_data.get("message", "") if 'input_data' in locals() else ""},
                        {
                            "output": "I'm sorry, I encountered an error processing your request.",
                            "metadata": error_context
                        }
                    )
                except Exception as save_error:
                    logger.error(f"Failed to save error context: {str(save_error)}")
            
            # Generate a user-friendly error message
            try:
                error_message = self._generate_error_response(e, input_data.get("message", ""))
            except Exception as gen_error:
                logger.error(f"Failed to generate error response: {str(gen_error)}")
                error_message = "I'm sorry, I encountered an error processing your request. Please try again later."
            
            return {
                "response": error_message,
                "error": str(e),
                "metadata": error_context,
                "metrics": {
                    **self.metrics,
                    "error": True,
                    "error_type": type(e).__name__,
                    "response_time_ms": (time.time() - start_time) * 1000
                },
                "session_id": getattr(self.memory, 'session_id', None)
            }

    def _process_tool_usage(self, response: Dict[str, Any], duration_ms: float) -> Dict[str, Any]:
        """
        Process tool usage from the agent's response and update metrics.
        
        This method tracks tool usage patterns, records metrics, and updates
        the context based on tool interactions.
        
        Args:
            response: The response from the agent's execution
            duration_ms: The duration of the agent's execution in milliseconds
            
        Returns:
            Dictionary containing tool usage information and results
        """
        tool_calls = response.get("intermediate_steps", [])
        tool_usage = {}
        
        # Process each tool call
        for tool_call in tool_calls:
            tool_name = tool_call[0].tool
            tool_input = tool_call[0].tool_input
            tool_output = tool_call[1]
            
            # Track article interactions specifically
            if tool_name == 'article_recommender' and isinstance(tool_output, dict):
                if tool_output.get('status') == 'success':
                    for article in tool_output.get('articles', []):
                        self.usage_tracker.log_article_interaction(
                            user_id=self.user_id,
                            article_id=article.get('id'),
                            interaction_type='view',
                            execution_time=duration_ms / 1000.0,  # Convert to seconds
                            metadata={
                                'input': tool_input,
                                'output': str(observation)
                            }
                        )
        
        # Update metrics
        self.metrics["tool_usage"] = tool_usage
        
        return {
            'tool_calls': tool_calls,
            'tool_results': tool_results,
            'tool_usage': tool_usage
        }
        
    def _generate_error_response(self, error: Exception, user_input: str = "") -> str:
        """Generate a user-friendly error response based on the error type.
        
        Args:
            error: The exception that occurred
            user_input: The user's input that caused the error
            
        Returns:
            str: A user-friendly error message
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Common error patterns
        if "connection" in error_msg or "timeout" in error_msg:
            return (
                "I'm having trouble connecting to one of our services. "
                "Please check your internet connection and try again in a moment."
            )
        elif "rate limit" in error_msg or "quota" in error_msg:
            return (
                "I've reached my limit for processing requests right now. "
                "Please wait a few minutes and try again. Thank you for your patience!"
            )
        elif "validation" in error_type.lower() or "invalid" in error_msg:
            return (
                "I couldn't understand your request. Could you please rephrase it? "
                f"Here's what went wrong: {error_msg}"
            )
        
        # Default error message with option to reference the error ID for support
        error_id = str(hash(f"{datetime.now().isoformat()}{str(error)}"))[-8:]
        return (
            "I'm sorry, I encountered an unexpected error while processing your request. "
            f"(Error ID: {error_id}) Please try again in a moment. If the problem persists, "
            "you can reference this error ID when contacting support."
        )
    
    def switch_session(self, session_id: str) -> None:
        """Switch to a different conversation session.
        
        Args:
            session_id: ID of the session to switch to
        """
        # Save current session if needed
        if hasattr(self.memory, '_persist'):
            try:
                self.memory._persist()
            except Exception as e:
                logger.warning(f"Failed to persist current session: {str(e)}")
        
        # Create new memory instance with the new session
        self.memory = ConversationMemory(
            user_id=self.user_id,
            session_id=session_id,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Update the executor with the new memory
        self.executor.memory = self.memory
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the conversation history for the current session.
        
        Args:
            limit: Maximum number of messages to return (default: all)
            
        Returns:
            List of message dictionaries with content and metadata
        """
        if hasattr(self.memory, 'get_conversation_history'):
            return self.memory.get_conversation_history(limit=limit)
        return []
    
    def clear_conversation(self) -> None:
        """Clear the current conversation history."""
        if hasattr(self.memory, 'clear'):
            self.memory.clear()
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available conversation sessions for the current user.
        
        Returns:
            List of session metadata dictionaries
        """
        if not hasattr(self.memory, 'list_sessions'):
            return []
        return self.memory.list_sessions()


# Initialize service
agent_service = AgentService()
