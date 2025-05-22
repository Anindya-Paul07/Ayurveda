#!/bin/bash

# Database setup script for Ayurveda Backend

# Create data directory if it doesn't exist
mkdir -p data

echo "Initializing database..."
python3 init_db.py

echo "Seeding database with sample data..."
python3 seed_database.py

echo "Database setup complete!"
