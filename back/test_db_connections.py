#!/usr/bin/env python3
"""
Test script to verify database connections and basic operations.
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.database import (
    UserConversation, UserMessage, UserContext,
    Article, ArticleMetrics, ArticleKeyword, ArticleTag, ArticleTagMapping,
    get_db_session, init_databases, close_session
)
from service.database_utils import create_object, get_objects

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"{text.upper()}".center(80))
    print("=" * 80)

def test_user_database():
    """Test operations on the user database."""
    print_header("Testing User Database (PostgreSQL)")
    
    try:
        # Create a test conversation
        print("Creating a test conversation...")
        conv_data = {
            'user_id': 'test_user_123',
            'created_at': datetime.utcnow()
        }
        conversation = create_object(UserConversation, conv_data)
        print(f"Created conversation with ID: {conversation.id}")
        
        # Add a message to the conversation
        print("Adding a test message...")
        msg_data = {
            'conversation_id': conversation.id,
            'role': 'user',
            'content': 'Hello, this is a test message',
            'created_at': datetime.utcnow()
        }
        message = create_object(UserMessage, msg_data)
        print(f"Added message with ID: {message.id}")
        
        # Add context to the conversation
        print("Adding conversation context...")
        ctx_data = {
            'conversation_id': conversation.id,
            'user_profile': {'name': 'Test User', 'age': 30},
            'tool_usage': {'tools_used': ['test_tool']},
            'created_at': datetime.utcnow()
        }
        context = create_object(UserContext, ctx_data)
        print(f"Added context with ID: {context.id}")
        
        # Query the conversation with related data
        with get_db_session('user') as db:
            conv = db.query(UserConversation).get(conversation.id)
            print(f"\nConversation details:")
            print(f"- User ID: {conv.user_id}")
            print(f"- Created: {conv.created_at}")
            print(f"- Messages: {len(conv.messages)}")
            print(f"- Context: {conv.context is not None}")
        
        return True
    except Exception as e:
        print(f"Error testing user database: {str(e)}")
        return False

def test_article_database():
    """Test operations on the article database."""
    print_header("Testing Article Database (SQLite)")
    
    try:
        # Create a test article
        print("Creating a test article...")
        article_data = {
            'title': 'Test Article',
            'content': 'This is a test article about Ayurveda.',
            'summary': 'A test article',
            'description': 'This is a test article description',
            'source': 'test',
            'source_url': 'http://example.com/test-article',
            'author': 'Test Author',
            'published_at': datetime.utcnow(),
            'is_published': 1,
            'category': 'Test',
            'slug': 'test-article',
            'tags': 'test, ayurveda'
        }
        article = create_object(Article, article_data, 'article')
        print(f"Created article with ID: {article.id}")
        
        # Add metrics for the article
        print("Adding article metrics...")
        metrics_data = {
            'article_id': article.id,
            'view_count': 0,
            'share_count': 0,
            'like_count': 0,
            'last_viewed': datetime.utcnow()
        }
        metrics = create_object(ArticleMetrics, metrics_data, 'article')
        print(f"Added metrics with ID: {metrics.id}")
        
        # Add keywords for the article
        print("Adding article keywords...")
        keywords = [
            {'article_id': article.id, 'keyword': 'ayurveda', 'score': 10},
            {'article_id': article.id, 'keyword': 'test', 'score': 5},
            {'article_id': article.id, 'keyword': 'health', 'score': 8}
        ]
        for kw in keywords:
            keyword = create_object(ArticleKeyword, kw, 'article')
            print(f"  - Added keyword: {keyword.keyword}")
        
        # Query the article with related data
        with get_db_session('article') as db:
            art = db.query(Article).get(article.id)
            print(f"\nArticle details:")
            print(f"- Title: {art.title}")
            print(f"- Author: {art.author}")
            print(f"- Published: {art.published_at}")
            print(f"- Keywords: {', '.join([k.keyword for k in art.keywords])}")
            print(f"- View count: {art.metrics.view_count if art.metrics else 'N/A'}")
        
        return True
    except Exception as e:
        print(f"Error testing article database: {str(e)}")
        return False

def main():
    """Main function to run the tests."""
    # Load environment variables
    load_dotenv()
    
    print("\n" + "=" * 80)
    print("AYURVEDA AI - DATABASE CONNECTION TEST".center(80))
    print("=" * 80)
    
    # Initialize databases
    print("\nInitializing databases...")
    try:
        init_databases()
        print("✅ Databases initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize databases: {str(e)}")
        return
    
    # Test user database
    user_success = test_user_database()
    
    # Test article database
    article_success = test_article_database()
    
    # Print summary
    print_header("Test Summary")
    print(f"User Database (PostgreSQL): {'✅ PASSED' if user_success else '❌ FAILED'}")
    print(f"Article Database (SQLite): {'✅ PASSED' if article_success else '❌ FAILED'}")
    
    # Cleanup
    close_session()

if __name__ == "__main__":
    main()
