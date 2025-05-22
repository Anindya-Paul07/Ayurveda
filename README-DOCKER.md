# Ayurveda AI Assistant - Docker Setup

This guide will help you set up and run the Ayurveda AI Assistant using Docker Compose.

## Prerequisites

- Docker (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- Make sure ports 80, 443, 3000, and 5000 are available on your system

## Quick Start

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd ayurveda
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and fill in your API keys and configuration.

3. **Build and start the services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend (development): http://localhost:3000
   - Backend API: http://localhost:5000
   - Production build: http://localhost

## Available Services

### Production Services
- **Nginx**: Serves the frontend and proxies API requests
  - Ports: 80 (HTTP), 443 (HTTPS)
  - Access: http://localhost

- **Backend**: Python/Flask API
  - Port: 5000
  - API Base URL: http://localhost:5000/api
  - Health Check: http://localhost:5000/api/health

- **Redis**: In-memory data store
  - Port: 6379 (internal only)

### Development Services
- **Frontend (Development)**: React development server
  - Port: 3000
  - Access: http://localhost:3000
  - Hot-reload enabled

- **Backend (Development)**: Python/Flask development server
  - Port: 5000
  - Auto-reload enabled

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Application
NODE_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# Redis
REDIS_URL=redis://redis:6379

# API Keys
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
PINECONE_API_KEY=your-pinecone-api-key
GOOGLE_API_KEY=your-google-api-key
```

## Useful Commands

- **Start services in detached mode**:
  ```bash
  docker-compose up -d
  ```

- **View logs**:
  ```bash
  docker-compose logs -f
  ```

- **Stop services**:
  ```bash
  docker-compose down
  ```

- **Rebuild containers**:
  ```bash
  docker-compose up --build
  ```

- **Access container shell**:
  ```bash
  docker-compose exec backend-dev bash
  ```

## Troubleshooting

1. **Port conflicts**:
   - Make sure ports 80, 443, 3000, and 5000 are not in use by other applications.
   - You can change the ports in the `docker-compose.yml` file if needed.

2. **Missing environment variables**:
   - Ensure all required environment variables are set in the `.env` file.
   - The application won't start without the required API keys.

3. **Docker permissions**:
   - If you encounter permission errors, you might need to run Docker commands with `sudo` or add your user to the `docker` group.

4. **Container logs**:
   - Check the logs for any errors: `docker-compose logs -f`

## Production Deployment

For production deployment, you should:

1. Set `NODE_ENV=production` in the `.env` file
2. Build the frontend for production:
   ```bash
   cd frontend
   npm run build
   ```
3. Use a proper SSL certificate (e.g., Let's Encrypt) for HTTPS
4. Consider using a process manager like PM2 for the backend in production
5. Set up proper monitoring and logging

## License

[Your License Here]
