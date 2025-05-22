# Flask Environment Variables
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/ayurveda
USER_DATABASE_URL=postgresql://user:password@localhost/ayurveda_users
ARTICLE_DATABASE_URL=sqlite:///data/ayurveda.db

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Application Configuration
APP_URL=http://localhost:3000
SECRET_KEY=dev-key-change-in-production

# External Services
PINECONE_API_KEY=your-pinecone-api-key
OPENAI_API_KEY=your-openai-api-key
