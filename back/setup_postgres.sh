#!/bin/bash

# Exit on error
set -e

echo "Setting up PostgreSQL database..."

# Load environment variables from .env file
if [ -f ../.env ]; then
    export $(grep -v '^#' ../.env | xargs -d '\n' | grep -v '^$')
fi

# Default values if not set in .env
USER_DATABASE_URL=${USER_DATABASE_URL:-"postgresql://user:password@localhost:5432/ayurveda_users"}

# Extract database connection details
DB_USER=$(echo $USER_DATABASE_URL | grep -oP '(?<=//)[^:]+')
DB_PASS=$(echo $USER_DATABASE_URL | grep -oP '(?<=:)[^@]+' | cut -d'@' -f1)
DB_HOST=$(echo $USER_DATABASE_URL | grep -oP '(?<=@)[^/]+' | cut -d':' -f1)
DB_PORT=$(echo $USER_DATABASE_URL | grep -oP '(?<=:)[0-9]+' | tail -1)
DB_NAME=$(echo $USER_DATABASE_URL | grep -oP '(?<=/)[^/]+$')

echo "Database connection details:"
echo "- User: $DB_USER"
echo "- Host: $DB_HOST"
echo "- Port: ${DB_PORT:-5432}"
echo "- Database: $DB_NAME"

# Create the database and user if they don't exist
echo -e "\nCreating database '$DB_NAME' and user '$DB_USER'..."

# Create user if it doesn't exist
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "Creating user $DB_USER..."
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
else
    echo "User $DB_USER already exists, updating password..."
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASS';"
fi

# Create database if it doesn't exist
if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Creating database $DB_NAME..."
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
else
    echo "Database $DB_NAME already exists."
fi

# Grant privileges
echo "Granting privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Create necessary extensions
echo "Creating necessary extensions..."
sudo -u postgres psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

echo -e "\n✅ Database setup complete!"
echo "Database URL: $USER_DATABASE_URL"
echo -e "\nYou can now run the application with the database connection."
