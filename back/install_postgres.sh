#!/bin/bash

# Exit on error
set -e

echo "Installing and setting up PostgreSQL..."

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install PostgreSQL and its contrib package
echo "Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib

# Start the PostgreSQL service
echo "Starting PostgreSQL service..."
sudo systemctl start postgresql

# Enable PostgreSQL to start on boot
echo "Enabling PostgreSQL to start on boot..."
sudo systemctl enable postgresql

# Create the database and user
echo "Setting up database and user..."
sudo -u postgres psql -c "CREATE USER user WITH PASSWORD 'password';" || echo "User 'user' already exists, continuing..."
sudo -u postgres psql -c "CREATE DATABASE ayurveda_users;" || echo "Database 'ayurveda_users' already exists, continuing..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ayurveda_users TO user;"
sudo -u postgres psql -d ayurveda_users -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

# Update PostgreSQL configuration to allow password authentication
echo "Updating PostgreSQL configuration..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/*/main/postgresql.conf

# Update pg_hba.conf to allow connections from the application
sudo bash -c "echo 'host    all             all             127.0.0.1/32            md5' >> /etc/postgresql/*/main/pg_hba.conf"
sudo bash -c "echo 'host    all             all             ::1/128                 md5' >> /etc/postgresql/*/main/pg_hba.conf"

# Restart PostgreSQL to apply changes
echo "Restarting PostgreSQL..."
sudo systemctl restart postgresql

echo -e "\n✅ PostgreSQL installation and setup complete!"
echo "Database connection URL: postgresql://user:password@localhost:5432/ayurveda_users"
echo -e "\nYou can now run the application with the database connection."
