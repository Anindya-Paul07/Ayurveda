"""
Extensions Module

This module initializes and configures all Flask extensions used in the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_caching import Cache
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_apscheduler import APScheduler
from redis import Redis
import rq

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()
mail = Mail()
cache = Cache()
cors = CORS()
socketio = SocketIO(cors_allowed_origins="*")
scheduler = APScheduler()

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Import models to ensure they are registered with SQLAlchemy
# This must be after db initialization to avoid circular imports
from models import User  # noqa: F401

def init_extensions(app):
    """Initialize all Flask extensions with the application."""
    # Initialize database
    db.init_app(app)
    
    # Initialize migrations
    migrate.init_app(app, db)
    
    # Configure SQLAlchemy binds
    with app.app_context():
        # This ensures that all models are loaded before creating tables
        from models import User  # noqa: F401
        
        # Create tables if they don't exist
        db.create_all()
    
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Configure JWT
    jwt.init_app(app)
    
    # Configure Flask-Mail
    mail.init_app(app)
    
    # Configure CORS
    cors.init_app(app)
    
    # Configure Socket.IO
    socketio.init_app(app)
    
    # Configure rate limiting
    limiter.init_app(app)
    
    # Setup user_loader
    from .models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Initialize JWT
    jwt.init_app(app)
    
    # Initialize mail
    mail.init_app(app)
    
    # Initialize cache
    cache.init_app(app)
    
    # Initialize CORS
    cors.init_app(app)
    
    # Initialize Socket.IO
    socketio.init_app(
        app,
        message_queue=app.config.get('SOCKETIO_MESSAGE_QUEUE'),
        async_mode=app.config.get('SOCKETIO_ASYNC_MODE', 'eventlet'),
        cors_allowed_origins=app.config.get('CORS_ORIGINS', '*')
    )
    
    # Initialize rate limiter
    limiter.init_app(app)
    
    # Initialize scheduler
    if not app.config['TESTING']:  # Don't run scheduler during tests
        scheduler.init_app(app)
        scheduler.start()
    
    # Initialize Redis
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('ayurveda-tasks', connection=app.redis)
    
    return app
