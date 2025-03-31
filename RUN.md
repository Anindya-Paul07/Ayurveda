
This document provides step-by-step instructions to set up and run the Ayurvedic Recommender project locally with the new weather-based feature enabled.

## Overview

- **Project Structure**: The project consists of a React frontend and a Flask backend, organized in separate 'frontend' and 'back' directories within the ayurveda directory.
- **New Feature**: Weather-based Ayurvedic recommendations are integrated into the frontend (see `components/WeatherDisplay.jsx`) and supported by backend endpoints (see `routes/weather_routes.py` and `routes/recommendations_routes.py`).

## Prerequisites

- **Node.js and npm**: Ensure you have Node.js (v14 or higher) and npm installed.
- **Python**: Python 3.8+ is required.
- **Package Manager**: Use `pip` (or conda if preferred) to manage Python dependencies.

## Backend Setup

1. **Navigate to the Backend Directory**

   ```bash
   cd back
   ```
   All backend commands should be run from within the back directory.

2. **Create a Virtual Environment (Optional but Recommended)**
   - Using conda:

     ```bash
     conda create -n herbbot python=3.8 -y
     conda activate herbbot
     ```
   - Or using venv:

     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows use: venv\Scripts\activate
     ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   - Create a `.env` file in the back directory with the following content:

     ```ini
     PINECONE_API_KEY = "your_pinecone_api_key"
     OPENAI_API_KEY = "your_openai_api_key"
     SERP_API_KEY = "your_serp_api_key"
     WEATHER_API_KEY = "your_weather_api_key"  # Required for weather-based recommendations
     ```

5. **(Optional) Build the Knowledge Base**
   - If required for the new feature, run:

     ```bash
     python store_index.py
     ```

6. **Start the Backend Server**

   ```bash
   python app.py
   ```
   - The Flask backend should now be running on http://localhost:8080.

## Frontend Setup

1. **Navigate to the Frontend Directory**

   ```bash
   cd frontend
   ```
   All frontend commands should be run from within the frontend directory.

2. **Install Node Dependencies**

   ```bash
   npm install
   ```

3. **Start the React Development Server**

   ```bash
   npm start
   ```
   - The React app will typically open at http://localhost:3000.

## Verifying the New Feature

- **Access the React Application**:
  - Open your browser and navigate to http://localhost:3000.
- **Test the Weather Feature**:
  - Click on the 'Weather' tab in the navigation bar. Verify that the app displays current weather data along with Ayurvedic recommendations based on the fetched weather information.
  
- **API Testing**:
  - You can directly test the weather API endpoint: http://localhost:8080/api/weather?city=Mumbai&country=IN
  - Test weather-based recommendations: http://localhost:8080/api/recommendations?dosha=pitta&city=Mumbai&country=IN

## Troubleshooting

- If issues with dependencies or API errors occur, confirm all prerequisites are installed and API keys in the `.env` file are correct.
- Check the console logs for error messages and address them accordingly.
- For weather-related features, ensure your WEATHER_API_KEY is valid and that you're providing valid city names in your requests.
- If the weather feature isn't working, verify network connectivity as the application needs to make external API calls.

## Additional Notes

- The weather feature integrates with the recommendations system to provide personalized Ayurvedic advice based on current weather conditions in your location.
- Weather data includes temperature, humidity, and general conditions which are mapped to Ayurvedic principles.
- The system can automatically determine the season based on weather data if not explicitly provided.

*This document is designed to guide the local development setup. For deployment instructions (e.g., Docker, EC2), please refer to the README.md file.*
