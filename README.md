# ayurveda
An AI Assistant which tells you the goodness of nature and how you can prevent and cure diseases, with personalized recommendations based on weather conditions.

## Features

- **Ayurvedic Knowledge Base**: Access comprehensive information about herbs, remedies, and traditional Ayurvedic practices
- **Disease Tracking**: The system tracks diseases mentioned in conversations and provides relevant remedies
- **Dosha Determination**: Identify your Ayurvedic body type (Vata, Pitta, Kapha) through a questionnaire
- **Weather-Based Recommendations**: Get personalized Ayurvedic recommendations based on real-time weather conditions in your location
- **Google Search Fallback**: When the knowledge base doesn't have sufficient information, the system automatically searches the web

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