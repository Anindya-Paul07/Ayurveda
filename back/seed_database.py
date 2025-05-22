"""
Database Seeding Script

This script populates the database with sample articles for testing and development.
"""
import os
import sqlite3
from datetime import datetime, timedelta
import random
import sys

def get_db_connection():
    """Create and return a database connection."""
    try:
        db_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, 'ayurveda.db')
        
        # Check if database exists
        if not os.path.exists(db_path):
            print("❌ Database not found. Please run 'python init_db.py' first.")
            sys.exit(1)
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)

def seed_database():
    """Seed the database with sample data."""
    print("🌱 Starting database seeding...")
    
    # Sample article data
    sample_articles = [
        {
            'title': 'The Benefits of Turmeric in Ayurveda',
            'content': '''Turmeric, known as Haridra in Sanskrit, is a golden spice widely used in Ayurveda for its powerful anti-inflammatory and antioxidant properties. It helps in balancing all three doshas and is particularly beneficial for Pitta and Kapha types. Regular consumption can improve digestion, reduce inflammation, and boost immunity.''',
            'source': 'Ayurveda Today',
            'source_url': 'https://ayurveda-today.com/turmeric-benefits',
            'image_url': 'https://example.com/turmeric.jpg',
            'category': 'Herbs',
            'tags': 'turmeric,herbs,anti-inflammatory,digestion',
            'featured': 1,
            'author': 'Dr. Vaidya'
        },
        {
            'title': 'Understanding the Three Doshas',
            'content': '''Ayurveda is based on the concept of three doshas: Vata, Pitta, and Kapha. These biological energies govern all physical and mental processes. Understanding your dominant dosha can help you make better lifestyle and dietary choices for optimal health and well-being.''',
            'source': 'Ayurveda Wisdom',
            'source_url': 'https://ayurveda-wisdom.org/three-doshas',
            'image_url': 'https://example.com/doshas.jpg',
            'category': 'Ayurveda Basics',
            'tags': 'doshas,vata,pitta,kapha,ayurveda basics',
            'featured': 1,
            'author': 'Dr. Sharma'
        },
        {
            'title': 'Daily Routine for Better Health',
            'content': '''Dinacharya, or daily routine, is a fundamental concept in Ayurveda. Waking up before sunrise, oil pulling, tongue scraping, and self-massage are some of the practices that can help maintain balance and prevent disease. A consistent routine aligned with natural rhythms promotes overall well-being.''',
            'source': 'Holistic Living',
            'source_url': 'https://holistic-living.com/daily-routine',
            'image_url': 'https://example.com/dinacharya.jpg',
            'category': 'Lifestyle',
            'tags': 'daily routine,dinacharya,ayurvedic lifestyle,self-care',
            'featured': 0,
            'author': 'Dr. Patel'
        },
        {
            'title': 'Ayurvedic Herbs for Stress Relief',
            'content': '''Ashwagandha, Brahmi, and Jatamansi are some of the powerful Ayurvedic herbs that help combat stress and anxiety. These adaptogenic herbs help the body adapt to stress and promote mental clarity and emotional balance when taken regularly under proper guidance.''',
            'source': 'Herbal Remedies',
            'source_url': 'https://herbal-remedies.org/stress-relief-herbs',
            'image_url': 'https://example.com/herbs-stress.jpg',
            'category': 'Herbs',
            'tags': 'herbs,stress relief,ashwagandha,brahmi,jatamansi,adaptogens',
            'featured': 1,
            'author': 'Dr. Gupta'
        },
        {
            'title': 'The Importance of Digestion in Ayurveda',
            'content': '''Agni, or digestive fire, is central to Ayurvedic health. A strong agni ensures proper digestion, absorption, and assimilation of nutrients while eliminating toxins. Simple practices like eating in a calm environment and avoiding cold drinks with meals can significantly improve digestive health.''',
            'source': 'Digestive Wellness',
            'source_url': 'https://digestive-wellness.com/ayurvedic-digestion',
            'image_url': 'https://example.com/digestion.jpg',
            'category': 'Digestive Health',
            'tags': 'digestion,agni,ayurvedic diet,gut health',
            'featured': 0,
            'author': 'Dr. Iyer'
        }
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        print("🧹 Clearing existing data...")
        tables = [
            'article_tag_mapping',
            'article_keywords',
            'article_metrics',
            'article_tags',
            'articles',
            'article_categories'
        ]
        
        for table in tables:
            try:
                cursor.execute(f'DELETE FROM {table}')
                print(f"  - Cleared {table}")
            except sqlite3.OperationalError as e:
                print(f"  - Skipping {table}: {e}")
        
        # Insert categories
        print("📚 Inserting categories...")
        categories = [
            ('Herbs', 'Ayurvedic herbs and their benefits', 'herbs'),
            ('Ayurveda Basics', 'Fundamental concepts of Ayurveda', 'ayurveda-basics'),
            ('Lifestyle', 'Daily routines and lifestyle practices', 'lifestyle'),
            ('Digestive Health', 'Maintaining digestive wellness', 'digestive-health')
        ]
        
        category_map = {}
        for name, description, slug in categories:
            try:
                cursor.execute('''
                    INSERT INTO article_categories (name, description, slug)
                    VALUES (?, ?, ?)
                ''', (name, description, slug))
                category_map[name] = cursor.lastrowid
                print(f"  - Added category: {name}")
            except sqlite3.IntegrityError:
                cursor.execute('SELECT id FROM article_categories WHERE name = ?', (name,))
                category_map[name] = cursor.fetchone()[0]
                print(f"  - Using existing category: {name}")
        
        # Insert articles
        print("📝 Inserting articles...")
        for i, article_data in enumerate(sample_articles, 1):
            try:
                published_at = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                slug = article_data['title'].lower().replace(' ', '-').replace(',', '').replace("'", '')
                
                cursor.execute('''
                    INSERT INTO articles (
                        title, content, source, source_url, published_at, 
                        description, image_url, is_published, category, 
                        tags, featured, slug, author
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
                ''', (
                    article_data['title'],
                    article_data['content'],
                    article_data['source'],
                    article_data['source_url'],
                    published_at,
                    article_data['content'][:150] + '...',  # Simple description
                    article_data['image_url'],
                    article_data['category'],
                    article_data['tags'],
                    article_data['featured'],
                    slug,
                    article_data['author']
                ))
                
                article_id = cursor.lastrowid
                
                # Insert metrics
                cursor.execute('''
                    INSERT INTO article_metrics (article_id, view_count, share_count, like_count, last_viewed)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    article_id,
                    random.randint(10, 1000),  # Random view count
                    random.randint(0, 100),     # Random share count
                    random.randint(0, 50),      # Random like count
                    datetime.now().isoformat()
                ))
                
                # Extract and insert keywords (simple word frequency for demo)
                words = article_data['content'].lower().split()
                word_count = {}
                for word in words:
                    if len(word) > 3:  # Only consider words longer than 3 characters
                        word_count[word] = word_count.get(word, 0) + 1
                
                # Take top 5 keywords
                keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
                for keyword, count in keywords:
                    cursor.execute('''
                        INSERT INTO article_keywords (article_id, keyword, score)
                        VALUES (?, ?, ?)
                    ''', (article_id, keyword, count))
                
                # Process tags
                for tag_name in article_data['tags'].split(','):
                    tag_name = tag_name.strip()
                    if not tag_name:
                        continue
                        
                    # Insert tag if not exists
                    try:
                        cursor.execute('''
                            INSERT INTO article_tags (name, slug)
                            VALUES (?, ?)
                        ''', (tag_name, tag_name.lower().replace(' ', '-').replace(',', '')))
                        tag_id = cursor.lastrowid
                    except sqlite3.IntegrityError:
                        # Tag already exists
                        cursor.execute('SELECT id FROM article_tags WHERE name = ?', (tag_name,))
                        tag_id = cursor.fetchone()[0]
                    
                    # Create mapping
                    try:
                        cursor.execute('''
                            INSERT INTO article_tag_mapping (article_id, tag_id)
                            VALUES (?, ?)
                        ''', (article_id, tag_id))
                    except sqlite3.IntegrityError:
                        # Mapping already exists
                        pass
                
                print(f"  - Added article: {article_data['title']}")
                
            except Exception as e:
                print(f"  ❌ Error inserting article {article_data['title']}: {e}")
                conn.rollback()
                continue
        
        conn.commit()
        print("✅ Database seeded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
