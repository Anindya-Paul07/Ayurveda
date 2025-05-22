# Ayurveda AI Assistant

An AI-powered Ayurvedic assistant that provides personalized health recommendations based on traditional Ayurvedic practices, weather conditions, and your unique dosha profile.

## ✨ Features

- **🌿 Ayurvedic Knowledge Base**: Comprehensive information about herbs, remedies, and traditional practices
- **📊 Dosha Analysis**: Determine your Ayurvedic body type (Vata, Pitta, Kapha) through an interactive questionnaire
- **🌦️ Weather-Adaptive**: Personalized recommendations based on real-time weather conditions
- **🤖 AI-Powered Chat**: Interactive chat interface with both RAG and Agentic modes
- **📈 Health Tracking**: Monitor your health metrics and track progress over time
- **🔍 Smart Search**: Intelligent search across Ayurvedic knowledge base with web fallback
- **📰 Article Service**: Discover and read Ayurveda-related articles with recommendations

## 🚀 Quick Start with Docker

The easiest way to get started is using Docker Compose.

### Prerequisites

- Docker 20.10.0+
- Docker Compose 2.0.0+
- Node.js 18+ (for development)
- Python 3.11+ (for development)

### Running with Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/Anindya2369/ayurveda.git
   cd ayurveda
   ```

2. Create a `.env` file in the root directory with your API keys:
   ```bash
   cp .env.example .env
   # Edit the .env file with your API keys
   ```

3. Start the application:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost
   - API Docs: http://localhost/api/docs

### Development Setup

For development, you can use the development containers:

```bash
# Start development services
docker-compose up -d redis

# Run backend in development mode
docker-compose up backend-dev

# In another terminal, run frontend in development mode
docker-compose up frontend-dev
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```ini
# Required
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
SERP_API_KEY=your_serp_api_key
REDIS_URL=redis://redis:6379

# Article Service
NEWS_API_KEY=your_newsapi_key
GOOGLE_SEARCH_API_KEY=your_google_search_key
SEARCH_ENGINE_ID=your_search_engine_id

# Optional
NODE_ENV=development
DEBUG=true
```

## 🏗️ Project Structure

```
ayurveda/
├── back/                  # Backend (FlaskAPI)
│   ├── app/               # Application code
│   ├── data/              # Database files
│   ├── routes/            # API route definitions
│   ├── service/           # Business logic
│   ├── tests/             # Backend tests
│   ├── init_db.py         # Database initialization
│   ├── seed_database.py   # Sample data population
│   └── requirements.txt   # Python dependencies
├── frontend/              # Frontend (React)
│   ├── public/            # Static files
│   ├── src/               # React source code
│   └── package.json       # Frontend dependencies
├── docker/                # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
└── Dockerfile             # Production Dockerfile
```

## 📚 Documentation

- [API Documentation](http://localhost/api/docs) (available when running locally)
- [Article Service API](back/API_README.md) - Detailed documentation of the article endpoints
- [Ayurveda Knowledge Base](docs/knowledge-base.md)

## 🗄️ Database Setup

The application uses SQLite for data persistence. To initialize and seed the database with sample data:

```bash
# Navigate to the backend directory
cd back

# Make the setup script executable
chmod +x setup_database.sh

# Run the setup script
./setup_database.sh
```

This will:
1. Create the necessary database tables
2. Seed the database with sample articles
3. Set up initial categories and tags

## 🆕 Article Service

The Article Service provides functionality to discover, manage, and recommend Ayurveda-related articles. Key features include:

- **Article Discovery**: Fetch articles from various sources (NewsAPI, Google Search, RSS feeds)
- **Content Processing**: Extract and analyze article content
- **Recommendations**: Get personalized article recommendations
- **Engagement Tracking**: Track views, likes, and shares

### API Endpoints

See the [Article Service API Documentation](back/API_README.md) for a complete list of available endpoints and usage examples.

### Adding New Articles

New articles can be added through the API or by extending the `seed_database.py` script. The system supports:
- Rich text content
- Categories and tags
- Featured articles
- Article metrics (views, likes, shares)

### Customization

To customize the article sources or processing logic, modify the `ArticleFetcher` and `ArticleProcessor` classes in `back/service/article_service.py`.
- [Development Guide](docs/development.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## How to run?
### steps:

Clone the repository

```bash
git clone https://github.com/Anindya2369/ayurveda.git
```

After cloning the repository, navigate to the frontend directory and run 'npm install' to install all frontend dependencies.

### step 01- Create a conda environment after opening the repository

```bash
conda create -n herbbot python=3.8 -y
```
```bash 
conda activate herbbot
```

### step 02- Install the requirements

```bash
pip install -r requirements.txt
```

### step 03- Create a '.env' file in the root directory and add your Pinecone, OpenAI, and SERP API credentials as follows:

```ini
PINECONE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OPENAI_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SERP_API_KEY = "YOUR_SERP_API_KEY"
```

The SERP API key is required for the Google search fallback functionality, which allows the assistant to retrieve up-to-date information when it doesn't have sufficient context in its knowledge base.

### step 04- Create a Data directory and add your PDF files

```bash
mkdir -p Data
# Copy your PDF files into the Data/ directory
# These PDFs will be used to build the knowledge base
```

### step 05- Create the knowledge base for the bot:

```bash
# Run the following command to create embeddings and store them to Pinecone.
# This will create a Pinecone index named "herbbot"
python store_index.py
```

### step 05.1 - Build the React frontend

Navigate to the frontend directory, install dependencies, and build the production-ready React assets. Note that a new dependency, 'dompurify', has been added to support text sanitization and no paid modules are used.

```bash
cd frontend
npm install
npm run build
```

This builds a fully React-based frontend whose assets are served by the Flask backend.

### step 06- Initialize the unified backend server:

Start the Flask application which consolidates all routes via blueprints and serves the static React assets.

```bash
python app.py
```

### step 07- Check the deployed application on localhost:

```bash
# Open your browser and navigate to http://localhost:8080
```

The application runs on port 8080 by default.

## How to run tests?
### Running Backend Tests
Execute the following command to run backend tests using pytest:
```bash
pytest ./tests/backend
```

### Running Frontend Tests
Navigate to the frontend directory and run the following command to execute frontend tests using npm:
```bash
npm test
```
Note: The integration:test script uses cross-env to set NODE_PATH=./node_modules so that when the integration test (located in ../tests/integration) is executed, it uses the dependencies from the frontend/node_modules directory.

### Using the run_tests.sh Script
You can also run all tests using the provided script. From the root directory, execute:
```bash
sh run_tests.sh
```

## Unified Architecture

This application has been refactored to use a centralized Flask backend that integrates multiple blueprints for different functionalities:
- Dosha determination
- Weather data retrieval
- Personalized recommendations

The frontend is now fully built using React and is served as static assets by the Flask backend, ensuring a seamless unified experience.

## Weather Feature

The application now includes a weather-based recommendation system that provides Ayurvedic advice tailored to current weather conditions:

### How to use the Weather Feature:

1. Access the `/api/weather` endpoint with your city name (and optionally country code)
2. The system will fetch real-time weather data including temperature, humidity, and weather conditions
3. Based on this data, the `/api/recommendations` endpoint can provide weather-appropriate Ayurvedic recommendations

Example API call:
```
GET /api/weather?city=Mumbai&country=IN
```

This feature integrates weather data with Ayurvedic principles to offer personalized health recommendations based on environmental factors.

## Project Structure

The project follows a modular structure:

- **routes/**: Contains API endpoint definitions
  - `dosha_routes.py`: Endpoints for dosha determination
  - `weather_routes.py`: Weather data retrieval endpoints
  - `recommendations_routes.py`: Personalized recommendation endpoints
- **service/**: Backend services and helper functions
- **templates/**: HTML templates for the web interface
- **NEW_DOCS/**: Comprehensive documentation
  - `API_Documentation.md`: Detailed API reference
  - `Directory_Structure.md`: Project organization overview
  - `Security_Guidelines.md`: Security best practices

For a complete overview of the project structure, refer to `NEW_DOCS/Directory_Structure.md`.

## Docker Deployment

You can also run the application using Docker:

### Build the Docker image:

```bash
docker build -t ayurveda-app .
```

### Run the Docker container:

```bash
docker run -p 8080:8080 --env-file .env -v $(pwd)/Data:/app/Data ayurveda-app
```

Note: Before running the Docker container, make sure you have:
1. Created the `.env` file with your API credentials
2. Added your PDF files to the Data directory
3. Run `store_index.py` to create the Pinecone index
4. Built the React frontend using `npm install` and `npm run build` in the frontend directory

## Security Considerations

The application implements several security best practices:
- Environment variables for sensitive API keys
- Input validation on all API endpoints
- Error handling to prevent information leakage

For more details on security practices, refer to `NEW_DOCS/Security_Guidelines.md`.

## Techstack Used:

- Python
- LangChain
- Flask
- groq_client
- Pinecone
- Weather API integration
- Docker