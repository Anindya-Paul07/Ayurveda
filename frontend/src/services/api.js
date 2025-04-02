/**
 * API service for the Ayurvedic Food & Lifestyle Recommender
 * Centralizes all API calls to backend endpoints
 */
import axios from 'axios';

const backendURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8080';
const apiClient = axios.create({ baseURL: backendURL });

/**
 * Submits quiz responses to determine user's dosha
 * @param {Array} responses - Array of quiz responses
 * @returns {Promise<Object>} - Dosha results
 */
export const fetchDosha = async (responses) => {
  try {
    const res = await apiClient.post('/api/dosha', { responses });
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
    const res = await apiClient.get('/api/weather', { params: { city, country } });
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
    const res = await apiClient.get('/api/recommendations', { params });
    return res.data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
};

/**
 * Fetches unified Ayurvedic recommendations based on provided parameters
 * using a POST request to the /api/unified_recommendations endpoint.
 * @param {Object} payload - Parameters including dosha, quiz_responses, query, season, time_of_day, health_concern, city, country, and limit
 * @returns {Promise<Object>} - The response containing recommendations and other contextual data
 */
export const fetchUnifiedRecommendations = async (payload) => {
  try {
    const res = await apiClient.post('/api/unified_recommendations', payload);
    return res.data;
  } catch (error) {
    console.error('Error fetching unified recommendations:', error);
    throw error;
  }
};

/**
 * Sends a message to the general Ayurvedic chatbot
 * @param {string} message - User's message
 * @returns {Promise<Object>} - Bot's response
 */
export const fetchGeneralInfo = async (message) => {
  try {
    const res = await apiClient.post('/api/general', { message });
    return res.data;
  } catch (error) {
    console.error('Error sending message to chatbot:', error);
    throw error;
  }
};

/**
 * Fetches tracked remedies from the backend.
 * @returns {Promise<Object>} - Remedies data as JSON
 */
export const fetchRemedies = async () => {
  try {
    const res = await apiClient.get('/api/remedies');
    return res.data;
  } catch (error) {
    console.error('Error fetching remedies:', error);
    throw error;
  }
};
