import React, { useState } from 'react';
import { fetchWeather, fetchUnifiedRecommendations } from '../services/api';

function WeatherDisplay() {
  const [weather, setWeather] = useState(null);
  const [city, setCity] = useState('');
  const [country, setCountry] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loadingRec, setLoadingRec] = useState(false);
  const [errorRec, setErrorRec] = useState(null);

  const handleFetchWeather = async () => {
    if (!city) {
      setError('Please enter a city name');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await fetchWeather(city, country);
      setWeather(data);
      // Reset recommendations when new weather is fetched
      setRecommendations(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch weather data');
    } finally {
      setLoading(false);
    }
  };

  const handleFetchRecommendations = async () => {
    // Retrieve stored dosha result, if any
    let dosha = '';
    try {
      const doshaData = localStorage.getItem('doshaResult');
      if (doshaData) {
        const parsedData = JSON.parse(doshaData);
        dosha = parsedData && parsedData.dosha ? parsedData.dosha : '';
      }
    } catch (err) {
      console.error('Error parsing dosha data from localStorage:', err);
    }
    
    // Construct payload; you can add time_of_day, health_concern, or query as needed
    const payload = {
      dosha: dosha,
      city,
      country,
      season: weather && weather.season ? weather.season : '',
      limit: 5
    };
    setLoadingRec(true);
    setErrorRec(null);
    try {
      const data = await fetchUnifiedRecommendations(payload);
      setRecommendations(data.recommendations);
    } catch (err) {
      setErrorRec(err.message || 'Failed to fetch recommendations');
    } finally {
      setLoadingRec(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    handleFetchWeather();
    // Clear any existing recommendations when searching for new weather
    setRecommendations(null);
    setErrorRec(null);
  };

  return (
    <div className="max-w-lg mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-primary">Weather Information</h2>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Enter city name"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              data-cy="city-input"
              required
            />
          </div>
          <div className="flex-1">
            <input
              type="text"
              placeholder="Country (optional)"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              data-cy="country-input"
            />
          </div>
          <button 
            type="submit" 
            className="px-6 py-2 bg-primary text-white rounded hover:bg-primary-dark transition-colors duration-300 disabled:opacity-50"
            disabled={!city || loading}
            data-cy="get-weather-button"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
      
      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
        </div>
      )}
      
      {error && (
        <div className="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg" role="alert">
          <span className="font-medium">Error:</span> {error}
        </div>
      )}
      
      {weather && !loading && !error && (
        <div className="p-6 border border-gray-200 rounded-lg shadow-sm bg-gray-50" data-cy="weather-data">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
            <h3 className="text-xl font-semibold">{weather.city}{weather.country ? `, ${weather.country}` : ''}</h3>
            {weather.weather_icon && (
              <img 
                src={weather.weather_icon} 
                alt={weather.weather_description || 'Weather icon'} 
                className="w-16 h-16"
              />
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center">
              <span className="text-3xl font-bold">{weather.temperature}°C</span>
            </div>
            
            <div>
              <p className="text-lg capitalize">{weather.weather_description}</p>
            </div>
            
            <div className="flex items-center">
              <span className="mr-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M5.5 17a4.5 4.5 0 01-1.44-8.765 4.5 4.5 0 018.302-3.046 3.5 3.5 0 014.504 4.272A4 4 0 0115 17H5.5z" clipRule="evenodd" />
                </svg>
              </span>
              <span><strong>Humidity:</strong> {weather.humidity}%</span>
            </div>
            
            {weather.wind_speed && (
              <div className="flex items-center">
                <span className="mr-2">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                </span>
                <span><strong>Wind:</strong> {weather.wind_speed} m/s</span>
              </div>
            )}
            
            {weather.pressure && (
              <div className="flex items-center">
                <span className="mr-2">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                  </svg>
                </span>
                <span><strong>Pressure:</strong> {weather.pressure} hPa</span>
              </div>
            )}
          </div>
          
          {weather.ayurvedic_recommendation && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg" data-cy="weather-recommendations">
              <h4 className="font-semibold text-green-800 mb-2">Ayurvedic Weather Insight:</h4>
              <p className="text-green-700">{weather.ayurvedic_recommendation}</p>
            </div>
          )}
          
          <button 
            onClick={handleFetchRecommendations} 
            disabled={loadingRec} 
            className="mt-4 px-4 py-2 bg-secondary text-white rounded hover:bg-opacity-90 transition-colors duration-300"
          >
            {loadingRec ? 'Fetching Recommendations...' : 'Get Ayurvedic Recommendations'}
          </button>
          
          {errorRec && (
            <div className="p-4 mt-4 text-sm text-red-700 bg-red-100 rounded-lg" role="alert">
              <span className="font-medium">Error:</span> {errorRec}
            </div>
          )}
          
          {recommendations && (
            <div className="mt-6 p-4 border rounded bg-gray-50" data-cy="weather-recommendations">
              <h4 className="font-semibold mb-3">Personalized Recommendations:</h4>
              <ul className="space-y-3">
                {recommendations.map((item, index) => (
                  <li key={index} className="p-3 bg-white rounded shadow-sm">
                    <p className="mb-1">{item.content}</p>
                    <small className="text-gray-600">Classification: {item.classification} | Relevance: {item.relevance_score.toFixed(2)}</small>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default WeatherDisplay;
