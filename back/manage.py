#!/usr/bin/env python3
"""
This script helps manage the application, particularly for database migrations.
"""
import os
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from app import create_app
from service.database import db

# Create the Flask application
app, socketio = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-Script manager
manager = Manager(app)

# Add migration commands
manager.add_command('db', MigrateCommand)

# Add a runserver command
manager.add_command("runserver", Server(host='0.0.0.0', port=5000))

@manager.command
def init_db():
    """Initialize the database."""
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database initialized successfully.")

@manager.command
def dev():
    """Run the development server with Socket.IO."""
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True)

if __name__ == '__main__':
    manager.run()
