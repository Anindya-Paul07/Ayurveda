# Ayurveda AI Backend

This is the backend service for the Ayurveda AI application, built with Flask and various modern Python technologies.

## Features

- User authentication and authorization
- RESTful API endpoints
- Real-time communication with WebSockets
- Database migrations with Flask-Migrate
- Rate limiting and security features
- Integration with external services (OpenAI, Pinecone, etc.)

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for caching and rate limiting)
- Node.js and npm (for frontend development)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ayurveda-ai.git
   cd ayurveda-ai/back
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## Running the Application

### Development Mode

```bash
# Start the development server
flask run

# Or with auto-reload
FLASK_DEBUG=1 flask run
```

### Production Mode

```bash
# Using Gunicorn
gunicorn -w 4 -k eventlet -b 0.0.0.0:5000 "app:create_app()"
```

## Database Migrations

When you make changes to your models, generate a new migration:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

To rollback a migration:

```bash
flask db downgrade
```

## API Documentation

API documentation is available at `/api/docs` when running in development mode.

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=.
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Flask application entry point | `app.py` |
| `FLASK_ENV` | Environment (development, production) | `development` |
| `SECRET_KEY` | Secret key for session management | `dev-key-change-in-production` |
| `DATABASE_URL` | Main database URL | `postgresql://user:password@localhost/ayurveda` |
| `USER_DATABASE_URL` | User database URL | `postgresql://user:password@localhost/ayurveda_users` |
| `ARTICLE_DATABASE_URL` | Articles database URL | `sqlite:///data/ayurveda.db` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | `jwt-secret-key-change-in-production` |
| `MAIL_SERVER` | SMTP server for emails | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USE_TLS` | Use TLS for email | `True` |
| `MAIL_USERNAME` | Email username | - |
| `MAIL_PASSWORD` | Email password | - |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask
- SQLAlchemy
- Flask-Migrate
- And all other open-source projects used in this project.
