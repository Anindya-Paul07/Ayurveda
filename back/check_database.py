#!/usr/bin/env python3
"""
Database Verification Script

This script verifies that the database was properly initialized and seeded.
"""
import sqlite3
from tabulate import tabulate

def check_database():
    """Check the database and print a summary of its contents."""
    try:
        # Connect to the database
        conn = sqlite3.connect('data/ayurveda.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("🔍 Database Verification Report")
        print("=" * 50)
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        print(f"\n📊 Found {len(tables)} tables: {', '.join(tables)}\n")
        
        # Check articles
        cursor.execute("SELECT COUNT(*) as count FROM articles")
        article_count = cursor.fetchone()['count']
        print(f"📰 Articles: {article_count}")
        
        # Display sample articles
        cursor.execute("""
            SELECT a.id, a.title, a.category, a.featured, 
                   m.view_count, m.like_count, m.share_count
            FROM articles a
            LEFT JOIN article_metrics m ON a.id = m.article_id
            ORDER BY a.id
            LIMIT 5
        """)
        
        print("\n📋 Sample Articles:")
        print(tabulate(cursor.fetchall(), headers="keys", tablefmt="grid"))
        
        # Check categories
        cursor.execute("SELECT COUNT(*) as count FROM article_categories")
        category_count = cursor.fetchone()['count']
        print(f"\n🏷️  Categories: {category_count}")
        
        cursor.execute("SELECT name, slug FROM article_categories")
        print("\n📂 Categories:")
        for row in cursor.fetchall():
            print(f"  - {row['name']} ({row['slug']})")
        
        # Check tags
        cursor.execute("""
            SELECT t.name, t.slug, COUNT(atm.article_id) as article_count
            FROM article_tags t
            LEFT JOIN article_tag_mapping atm ON t.id = atm.tag_id
            GROUP BY t.id
            ORDER BY article_count DESC
        """)
        
        print("\n🏷️  Tags and Usage:")
        print(tabulate(cursor.fetchall(), headers="keys", tablefmt="grid"))
        
        # Check metrics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_articles,
                SUM(view_count) as total_views,
                AVG(view_count) as avg_views,
                SUM(like_count) as total_likes,
                SUM(share_count) as total_shares
            FROM article_metrics
        """)
        
        metrics = cursor.fetchone()
        print("\n📈 Article Metrics:")
        print(f"  - Total Articles: {metrics['total_articles']}")
        print(f"  - Total Views: {metrics['total_views']}")
        print(f"  - Average Views per Article: {metrics['avg_views']:.1f}")
        print(f"  - Total Likes: {metrics['total_likes']}")
        print(f"  - Total Shares: {metrics['total_shares']}")
        
        conn.close()
        print("\n✅ Database verification completed successfully!")
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database()
