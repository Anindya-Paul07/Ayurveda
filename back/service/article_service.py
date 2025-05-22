"""
Article Service Module

This module provides tools for discovering, processing, and recommending
Ayurveda-related articles. It integrates with the agent system to provide
personalized article recommendations based on user context and preferences.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from bs4 import BeautifulSoup
import feedparser
import logging
from urllib.parse import urlparse, quote_plus

# Database
from .database import get_session
from .models import Article, ArticleInteraction, UserPreference

# Vector store
from pinecone.grpc import PineconeGRPC as Pinecone
from langchain_pinecone import PineconeVectorStore

# Embeddings
from .helper import download_hugging_face_embeddings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_newsapi_key')
GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY', 'your_google_search_key')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID', 'your_search_engine_id')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

class ArticleTool:
    """
    Tool for discovering and recommending Ayurveda articles.
    """
    
    name = "article_recommender"
    description = """
    Use this tool to find and recommend relevant Ayurveda articles.
    Input should be a JSON string with fields:
    - query: Search query (optional)
    - categories: List of categories (e.g., ['herbs', 'yoga', 'diet'])
    - max_results: Maximum number of results (default: 5)
    - user_id: Optional user ID for personalized results
    """
    
    def __init__(self):
        self.embeddings = download_hugging_face_embeddings()
        self.vector_store = self._init_vector_store()
        self.session = get_session()
    
    def _init_vector_store(self):
        """Initialize the vector store for article embeddings."""
        index_name = "ayurveda-articles"
        return PineconeVectorStore(
            index=pc.Index(index_name),
            embedding=self.embeddings,
            text_key="text"
        )
    
    def _run(self, input_str: str) -> str:
        """Execute the tool."""
        try:
            params = json.loads(input_str)
            query = params.get('query', '')
            categories = params.get('categories', [])
            max_results = min(int(params.get('max_results', 5)), 20)
            user_id = params.get('user_id')
            
            # Get personalized recommendations
            recommendations = self.get_article_recommendations(
                query=query,
                categories=categories,
                limit=max_results,
                user_id=user_id
            )
            
            return json.dumps({
                'status': 'success',
                'articles': recommendations,
                'count': len(recommendations)
            })
            
        except json.JSONDecodeError:
            return json.dumps({
                'status': 'error',
                'message': 'Invalid JSON input'
            })
        except Exception as e:
            logger.error(f"Error in ArticleTool: {str(e)}")
            return json.dumps({
                'status': 'error',
                'message': str(e)
            })

class ArticleFetcher:
    """Handles fetching articles from various sources."""
    
    @staticmethod
    def fetch_from_newsapi(query: str = 'Ayurveda', language: str = 'en', 
                          page_size: int = 10, from_date: Optional[str] = None) -> List[Dict]:
        """
        Fetch articles from NewsAPI.
        
        Args:
            query: Search query
            language: Language code (default: 'en')
            page_size: Number of results to return (max 100)
            from_date: Date in YYYY-MM-DD format (default: 1 month ago)
            
        Returns:
            List of article dictionaries
        """
        try:
            if from_date is None:
                # Default to 1 month ago
                from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': query,
                'language': language,
                'sortBy': 'publishedAt',
                'apiKey': NEWS_API_KEY,
                'pageSize': min(page_size, 100),  # API max is 100
                'from': from_date,
                'excludeDomains': 'youtube.com,vimeo.com'  # Exclude video content
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                article_data = {
                    'title': article.get('title', '').strip(),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'Unknown').strip(),
                    'published_at': article.get('publishedAt', ''),
                    'description': article.get('description', '').strip(),
                    'content': article.get('content', '').strip(),
                    'image_url': article.get('urlToImage', ''),
                    'author': article.get('author', '').strip(),
                    'source_type': 'news_api',
                    'language': language,
                    'metadata': {
                        'query_used': query,
                        'retrieved_at': datetime.utcnow().isoformat()
                    }
                }
                articles.append(article_data)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {str(e)}")
            return []
    
    @staticmethod
    def fetch_rss_feed(url: str) -> List[Dict]:
        """Fetch articles from an RSS feed."""
        try:
            feed = feedparser.parse(url)
            return [{
                'title': entry.get('title', ''),
                'url': entry.get('link', ''),
                'source': feed.feed.get('title', 'RSS Feed'),
                'published_at': entry.get('published', ''),
                'description': entry.get('description', ''),
                'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                'image_url': next((link.href for link in entry.links if 'image' in link.type.lower()), '')
            } for entry in feed.entries]
        except Exception as e:
            logger.error(f"Error fetching RSS feed {url}: {str(e)}")
            return []
    
    @staticmethod
    def google_search(query: str, num_results: int = 5) -> List[Dict]:
        """Search Google for articles."""
        try:
            url = 'https://www.googleapis.com/customsearch/v1'
            params = {
                'q': query,
                'key': GOOGLE_SEARCH_API_KEY,
                'cx': SEARCH_ENGINE_ID,
                'num': num_results,
                'lr': 'lang_en',
                'cr': 'countryIN',  # India
                'gl': 'in',
                'dateRestrict': 'm1'  # Last month
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for item in data.get('items', []):
                try:
                    # Fetch the full article content
                    article_content = ArticleFetcher.scrape_article(item['link'])
                    articles.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'source': item.get('displayLink', 'Unknown'),
                        'published_at': item.get('snippet', ''),
                        'description': item.get('snippet', ''),
                        'content': article_content,
                        'image_url': item.get('pagemap', {}).get('cse_image', [{}])[0].get('src', '') if item.get('pagemap', {}).get('cse_image') else ''
                    })
                except Exception as e:
                    logger.error(f"Error processing search result {item.get('link')}: {str(e)}")
            
            return articles
            
        except Exception as e:
            logger.error(f"Error in Google search: {str(e)}")
            return []
    
    @staticmethod
    def scrape_article(url: str) -> str:
        """Scrape the main content from a web page."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
                element.decompose()
            
            # Try to find the main content
            article = soup.find('article')
            if not article:
                article = soup.find('div', class_=lambda x: x and 'content' in x.lower())
            if not article:
                article = soup.find('main')
            if not article:
                article = soup
            
            # Get text with proper spacing
            text = ' '.join(p.get_text(' ', strip=True) for p in article.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']))
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return ''

class ArticleProcessor:
    """Processes and analyzes article content."""
    
    @staticmethod
    def extract_keywords(text: str, num_keywords: int = 5) -> List[str]:
        """Extract keywords from text using a simple algorithm."""
        # In a real implementation, you might want to use NLP libraries like spaCy
        # or integrate with an external service
        words = text.lower().split()
        word_count = {}
        
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_count[word] = word_count.get(word, 0) + 1
        
        # Sort by frequency and get top keywords
        return sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:num_keywords]
    
    @staticmethod
    def summarize_text(text: str, max_sentences: int = 3) -> str:
        """Generate a summary of the text."""
        # In a real implementation, you might want to use NLP libraries
        # or integrate with a summarization service
        sentences = text.split('.')
        return '. '.join(sentences[:max_sentences]) + '.'
    
    @staticmethod
    def is_ayurveda_related(article: Dict) -> bool:
        """Check if an article is related to Ayurveda."""
        ayurveda_keywords = [
            'ayurveda', 'ayurvedic', 'dosha', 'vata', 'pitta', 'kapha',
            'ayur', 'herbal', 'ayurved', 'prakriti', 'vikriti', 'panchakarma',
            'rasayana', 'dhatu', 'agni', 'ama', 'ojas', 'srotas'
        ]
        
        content = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}".lower()
        return any(keyword in content for keyword in ayurveda_keywords)

class ArticleManager:
    """Manages the article database and provides article recommendations."""
    
    def __init__(self, db_connection=None):
        self.db = db_connection or get_session()
        self.embeddings = download_hugging_face_embeddings()
        self.vector_store = self._init_vector_store()
        self.setup_database()
    
    def _init_vector_store(self):
        """Initialize the vector store for article embeddings."""
        index_name = "ayurveda-articles"
        try:
            # Check if index exists
            if index_name not in pc.list_indexes().names():
                # Create index if it doesn't exist
                pc.create_index(
                    name=index_name,
                    dimension=384,  # Dimension of the embeddings
                    metric="cosine"
                )
                
            return PineconeVectorStore(
                index=pc.Index(index_name),
                embedding=self.embeddings,
                text_key="text"
            )
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            return None
    
    def setup_database(self):
        """Initialize the database tables if they don't exist."""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                source TEXT,
                published_at TEXT,
                description TEXT,
                content TEXT,
                image_url TEXT,
                is_published BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                keyword TEXT,
                score REAL,
                FOREIGN KEY (article_id) REFERENCES articles (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                view_count INTEGER DEFAULT 0,
                share_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                FOREIGN KEY (article_id) REFERENCES articles (id)
            )
        ''')
        
        self.db.commit()
    
    def save_article(self, article: Dict) -> int:
        """Save an article to the database."""
        try:
            cursor = self.db.cursor()
            
            # Check if article already exists
            cursor.execute('SELECT id FROM articles WHERE url = ?', (article['url'],))
            existing = cursor.fetchone()
            
            if existing:
                return existing[0]
            
            # Insert new article
            cursor.execute('''
                INSERT INTO articles (
                    title, url, source, published_at, description, content, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.get('title', ''),
                article.get('url', ''),
                article.get('source', 'Unknown'),
                article.get('published_at', datetime.utcnow().isoformat()),
                article.get('description', ''),
                article.get('content', ''),
                article.get('image_url', '')
            ))
            
            article_id = cursor.lastrowid
            
            # Extract and save keywords
            keywords = ArticleProcessor.extract_keywords(
                f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
            )
            
            for keyword, score in keywords:
                cursor.execute('''
                    INSERT INTO article_keywords (article_id, keyword, score)
                    VALUES (?, ?, ?)
                ''', (article_id, keyword, score))
            
            # Initialize metrics
            cursor.execute('''
                INSERT INTO article_metrics (article_id) VALUES (?)
            ''', (article_id,))
            
            self.db.commit()
            return article_id
            
        except Exception as e:
            logger.error(f"Error saving article: {str(e)}")
            self.db.rollback()
            return None
    
    def get_recommended_articles(self, limit: int = 5) -> List[Dict]:
        """Get recommended articles for the dashboard."""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT a.*, am.view_count, am.share_count, am.like_count
                FROM articles a
                LEFT JOIN article_metrics am ON a.id = am.article_id
                WHERE a.is_published = 1
                ORDER BY a.published_at DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting recommended articles: {str(e)}")
            return []
    
    def publish_article(self, article_id: int) -> bool:
        """Mark an article as published."""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                UPDATE articles 
                SET is_published = 1, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (article_id,))
            
            self.db.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error publishing article {article_id}: {str(e)}")
            self.db.rollback()
            return False

class ArticleAgent:
    """AI agent that discovers, processes, and recommends articles."""
    
    def __init__(self, article_manager: Optional[ArticleManager] = None):
        self.article_manager = article_manager or ArticleManager()
        self.fetcher = ArticleFetcher()
        self.processor = ArticleProcessor()
        self.tool = ArticleTool()
    
    def get_article_recommendations(
        self,
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        limit: int = 5,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get personalized article recommendations.
        
        Args:
            query: Search query
            categories: List of categories to filter by
            limit: Maximum number of recommendations
            user_id: Optional user ID for personalization
            
        Returns:
            List of recommended articles with metadata
        """
        try:
            # Prepare input for the tool
            input_data = {
                'query': query or '',
                'categories': categories or [],
                'max_results': limit,
                'user_id': user_id
            }
            
            # Use the tool to get recommendations
            result = self.tool._run(json.dumps(input_data))
            result_data = json.loads(result)
            
            if result_data.get('status') == 'success':
                return result_data.get('articles', [])
            else:
                logger.error(f"Error getting recommendations: {result_data.get('message')}")
                return []
                
        except Exception as e:
            logger.error(f"Error in get_article_recommendations: {e}")
            return []
    
    def log_article_interaction(
        self,
        user_id: str,
        article_id: str,
        interaction_type: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Log a user's interaction with an article.
        
        Args:
            user_id: ID of the user
            article_id: ID of the article
            interaction_type: Type of interaction (view, like, save, share)
            metadata: Additional metadata about the interaction
            
        Returns:
            bool: True if the interaction was logged successfully
        """
        try:
            interaction = ArticleInteraction(
                user_id=user_id,
                article_id=article_id,
                interaction_type=interaction_type,
                metadata=metadata or {},
                timestamp=datetime.utcnow()
            )
            
            self.article_manager.db.add(interaction)
            self.article_manager.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error logging article interaction: {e}")
            self.article_manager.db.rollback()
            return False
    
    def discover_articles(self, query: str = 'Ayurveda') -> List[Dict]:
        """Discover new articles from various sources."""
        try:
            # Fetch from multiple sources
            articles = []
            
            # 1. NewsAPI
            articles.extend(self.fetcher.fetch_from_newsapi(query))
            
            # 2. Google Search
            articles.extend(self.fetcher.google_search(f"{query} site:.in OR site:.com"))
            
            # Filter and process articles
            processed_articles = []
            for article in articles:
                if self.processor.is_ayurveda_related(article):
                    # Save to database
                    article_id = self.article_manager.save_article(article)
                    if article_id:
                        article['id'] = article_id
                        processed_articles.append(article)
            
            return processed_articles
            
        except Exception as e:
            logger.error(f"Error in article discovery: {str(e)}")
            return []
    
    def generate_article_summary(self, article_id: int) -> str:
        """Generate a summary for an article."""
        try:
            cursor = self.article_manager.db.cursor()
            cursor.execute('SELECT content FROM articles WHERE id = ?', (article_id,))
            article = cursor.fetchone()
            
            if not article:
                return ""
                
            content = article[0]
            return self.processor.summarize_text(content)
            
        except Exception as e:
            logger.error(f"Error generating summary for article {article_id}: {str(e)}")
            return ""
    
    def get_article_recommendations(self, article_id: int, limit: int = 3) -> List[Dict]:
        """Get recommended articles based on keywords."""
        try:
            cursor = self.article_manager.db.cursor()
            
            # Get keywords for the current article
            cursor.execute('''
                SELECT keyword, score 
                FROM article_keywords 
                WHERE article_id = ?
                ORDER BY score DESC
                LIMIT 5
            ''', (article_id,))
            
            keywords = [row[0] for row in cursor.fetchall()]
            if not keywords:
                return []
            
            # Find similar articles
            query = '''
                SELECT DISTINCT a.*, am.view_count
                FROM articles a
                JOIN article_keywords ak ON a.id = ak.article_id
                LEFT JOIN article_metrics am ON a.id = am.article_id
                WHERE a.id != ? 
                AND a.is_published = 1
                AND ak.keyword IN ({})
                ORDER BY am.view_count DESC
                LIMIT ?
            '''.format(','.join(['?'] * len(keywords)))
            
            cursor.execute(
                query, 
                [article_id] + keywords + [limit]
            )
            
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting article recommendations: {str(e)}")
            return []

# Example usage
if __name__ == "__main__":
    import sqlite3
    
    # Initialize database and services
    db = sqlite3.connect(':memory:')  # Use a file in production
    article_manager = ArticleManager(db)
    agent = ArticleAgent(article_manager)
    
    # Discover and save articles
    print("Discovering articles...")
    articles = agent.discover_articles()
    print(f"Found {len(articles)} articles")
    
    # Publish some articles
    for article in articles[:3]:
        agent.article_manager.publish_article(article['id'])
    
    # Get recommended articles
    print("\nRecommended articles:")
    for article in article_manager.get_recommended_articles():
        print(f"- {article['title']} (Views: {article['view_count']})")
