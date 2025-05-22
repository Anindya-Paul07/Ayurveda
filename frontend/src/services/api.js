import axios from 'axios';
import { io } from 'socket.io-client';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// WebSocket connection
let socket = null;
const getSocket = () => {
  if (!socket) {
    socket = io(API_BASE_URL, {
      path: '/ws',
      transports: ['websocket'],
      withCredentials: true,
    });
  }
  return socket;
};

/**
 * Article Services
 */
export const articleService = {
  // Discover articles from various sources
  discoverArticles: (query = 'Ayurveda', limit = 10) =>
    api.get('/api/articles/discover', { params: { query, limit } }),
  
  // Get paginated articles with filtering and sorting
  getArticles: (params = {}) => {
    const defaultParams = {
      limit: 9, // 3x3 grid
      offset: 0,
      sort: 'published_at',
      order: 'desc'
    };
    return api.get('/api/articles', { params: { ...defaultParams, ...params } });
  },
  
  // Get article by ID
  getArticle: (id) =>
    api.get(`/api/articles/${id}`),
  
  // Like/unlike an article
  toggleLike: (id) =>
    api.post(`/api/articles/${id}/like`),
  
  // Bookmark/unbookmark an article
  toggleBookmark: (id) =>
    api.post(`/api/articles/${id}/bookmark`),
  
  // Share an article
  shareArticle: (id) =>
    api.post(`/api/articles/${id}/share`),
  
  // Get article categories
  getCategories: () =>
    api.get('/api/articles/categories').then(res => {
      // Ensure 'all' is always the first category
      const categories = res.data.categories || [];
      if (!categories.includes('all')) {
        categories.unshift('all');
      }
      return { ...res, data: categories };
    }),
  
  // Get related articles
  getRelatedArticles: (articleId, limit = 3) =>
    api.get(`/api/articles/${articleId}/related`, { params: { limit } }),
  
  // Get trending articles
  getTrendingArticles: (limit = 5) =>
    api.get('/api/articles/trending', { params: { limit } }),
  
  // Search articles
  searchArticles: (query, params = {}) =>
    api.get('/api/articles/search', { params: { q: query, ...params } }),

  // Get user's saved articles
  getSavedArticles: (params = {}) =>
    api.get('/api/articles/saved', { params }),
  
  // Get user's liked articles
  getLikedArticles: (params = {}) =>
    api.get('/api/articles/liked', { params }),
    
  // Track article view
  trackView: (articleId) =>
    api.post(`/api/articles/${articleId}/view`)
};

/**
 * Dosha Analysis Services
 */
export const doshaService = {
  // Get dosha analysis
  getDoshaAnalysis: (responses) => api.post('/api/dosha', { responses }),
  
  // Get dosha information
  getDoshaInfo: () => api.get('/api/dosha/info'),
  
  // Get personalized recommendations based on dosha
  getDoshaRecommendations: (doshaType, params = {}) =>
    api.get(`/api/recommendations`, { params: { dosha: doshaType, ...params } }),
};

/**
 * Health & Recommendation Services
 */
export const healthService = {
  // Get health recommendations
  getRecommendations: (params = {}) =>
    api.get('/api/recommendations', { params }),
  
  // Analyze symptoms
  analyzeSymptoms: (symptoms) =>
    api.post('/api/symptoms/analyze', { symptoms }),
  
  // Get disease information
  getDiseaseInfo: (diseaseName) =>
    api.get(`/api/diseases/${encodeURIComponent(diseaseName)}`),
};

/**
 * Chat & AI Services
 */
export const chatService = {
  // Send chat message
  sendMessage: (message, context = {}) =>
    api.post('/api/chat', { message, context }),
  
  // Get chat history
  getHistory: () => api.get('/api/chat/history'),
  
  // Clear chat history
  clearHistory: () => api.delete('/api/chat/history'),
  
  // Get chat suggestions
  getSuggestions: () => api.get('/api/chat/suggestions'),
};

/**
 * Weather Services
 */
export const weatherService = {
  // Get current weather
  getCurrentWeather: (city, country = null) =>
    api.get('/api/weather/current', { params: { city, country } }),
  
  // Get weather forecast
  getForecast: (city, days = 5, country = null) =>
    api.get('/api/weather/forecast', { params: { city, days, country } }),
  
  // Get season based on location
  getSeason: (lat, lon) =>
    api.get('/api/weather/season', { params: { lat, lon } }),
};

// Export the API instance
export default api;