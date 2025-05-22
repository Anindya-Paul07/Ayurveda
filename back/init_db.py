"""
Database Initialization Script

This script initializes the SQLite database with the required tables for the article service.
It should be run once during application setup.
"""
import os
import sqlite3
from datetime import datetime

def drop_tables(cursor):
    """Drop all tables if they exist."""
    tables = [
        'article_tag_mapping',
        'article_keywords',
        'article_metrics',
        'article_tags',
        'article_categories',
        'articles'
    ]
    
    for table in tables:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
        except Exception as e:
            print(f"Error dropping table {table}: {e}")

def init_database():
    """Initialize the SQLite database with required tables."""
    try:
        # Create data directory if it doesn't exist
        db_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(db_dir, exist_ok=True)
        
        # Connect to SQLite database (creates it if it doesn't exist)
        db_path = os.path.join(db_dir, 'ayurveda.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON;')
        
        # Drop existing tables if they exist
        drop_tables(cursor)
        
        # Create articles table
        cursor.execute('''
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            summary TEXT,
            description TEXT,
            source TEXT NOT NULL,
            source_url TEXT,
            image_url TEXT,
            author TEXT,
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_published BOOLEAN DEFAULT 1,
            category TEXT,
            tags TEXT,
            featured BOOLEAN DEFAULT 0,
            slug TEXT UNIQUE
        )
        ''')
        
        # Create article_keywords table
        cursor.execute('''
        CREATE TABLE article_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            keyword TEXT NOT NULL,
            score REAL NOT NULL,
            FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE
        )
        ''')
        
        # Create article_metrics table
        cursor.execute('''
        CREATE TABLE article_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL UNIQUE,
            view_count INTEGER DEFAULT 0,
            share_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            last_viewed TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE
        )
        ''')
        
        # Create article_categories table
        cursor.execute('''
        CREATE TABLE article_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            slug TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create article_tags table
        cursor.execute('''
        CREATE TABLE article_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create article_tag_mapping table
        cursor.execute('''
        CREATE TABLE article_tag_mapping (
            article_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (article_id, tag_id),
            FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES article_tags (id) ON DELETE CASCADE
        )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX idx_articles_published ON articles(is_published, published_at)')
        cursor.execute('CREATE INDEX idx_articles_category ON articles(category)')
        cursor.execute('CREATE INDEX idx_articles_featured ON articles(featured)')
        cursor.execute('CREATE INDEX idx_article_keywords_article_id ON article_keywords(article_id)')
        cursor.execute('CREATE INDEX idx_article_keywords_keyword ON article_keywords(keyword)')
        cursor.execute('CREATE INDEX idx_article_metrics_article_id ON article_metrics(article_id)')
        cursor.execute('CREATE INDEX idx_article_tag_mapping_article_id ON article_tag_mapping(article_id)')
        cursor.execute('CREATE INDEX idx_article_tag_mapping_tag_id ON article_tag_mapping(tag_id)')
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized successfully at {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    init_database()
