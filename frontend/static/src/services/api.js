/**
 * API service for the Ayurvedic Food & Lifestyle Recommender
 * Centralizes all API calls to backend endpoints
 */
import axios from 'axios';

/**
 * Submits quiz responses to determine user's dosha
 * @param {Array} responses - Array of quiz responses
 * @returns {Promise<Object>} - Dosha results
 */
export const fetchDosha = async (responses) => {
  try {
    const res = await axios.post('/api/dosha', { responses });
    return res.data;
  } catch (error) {
    console.error('Error fetching dosha results:', error);
    throw error;
  }
};

/**
 * Fetches weather data for a specific location
 * @param {string} city - City name
 * @param {string} [country] - Optional country code
 * @returns {Promise<Object>} - Weather data
 */
export const fetchWeather = async (city, country) => {
  try {
    const res = await axios.get('/api/weather', { params: { city, country } });
    return res.data;
  } catch (error) {
    console.error('Error fetching weather data:', error);
    throw error;
  }
};

/**
 * Fetches Ayurvedic recommendations based on provided parameters
 * @param {Object} params - Parameters for recommendations (dosha, season, weather, etc.)
 * @returns {Promise<Object>} - Personalized recommendations
 */
export const fetchRecommendations = async (params) => {
  try {
    const res = await axios.get('/api/recommendations', { params });
    return res.data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
};
