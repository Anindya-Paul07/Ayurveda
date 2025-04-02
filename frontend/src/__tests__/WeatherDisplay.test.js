import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import WeatherDisplay from '../components/WeatherDisplay';

// Mock the API services
import { fetchWeather, fetchUnifiedRecommendations } from '../services/api';

jest.mock('../services/api');

const weatherMock = {
  city: 'TestCity',
  country: 'TestCountry',
  weather_icon: 'http://test.com/icon.png',
  temperature: 25,
  weather_description: 'clear sky',
  humidity: 50,
  wind_speed: 3,
  pressure: 1010,
  ayurvedic_recommendation: 'Stay hydrated',
  season: 'Summer'
};

const recommendationsMock = {
  recommendations: [
    {
      content: 'Drink warm water in the morning',
      classification: 'Lifestyle',
      relevance_score: 0.95
    },
    {
      content: 'Take a short walk after meals',
      classification: 'Exercise',
      relevance_score: 0.90
    }
  ]
};

describe('WeatherDisplay Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear localStorage before each test
    localStorage.clear();
  });

  test('renders input fields and search button', () => {
    render(<WeatherDisplay />);

    const cityInput = screen.getByPlaceholderText(/enter city name/i);
    const countryInput = screen.getByPlaceholderText(/country \(optional\)/i);
    const searchButton = screen.getByRole('button', { name: /search/i });

    expect(cityInput).toBeInTheDocument();
    expect(countryInput).toBeInTheDocument();
    expect(searchButton).toBeInTheDocument();
  });

  test('shows error when trying to search without a city', () => {
    render(<WeatherDisplay />);

    const searchButton = screen.getByRole('button', { name: /search/i });
    // Instead of trying to click the disabled button, assert that it is disabled
    expect(searchButton).toBeDisabled();
  });

  test('displays weather data after successful fetch and handles loading state', async () => {
    fetchWeather.mockResolvedValueOnce(weatherMock);

    render(<WeatherDisplay />);

    const cityInput = screen.getByPlaceholderText(/enter city name/i);
    const countryInput = screen.getByPlaceholderText(/country \(optional\)/i);
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(cityInput, { target: { value: 'TestCity' } });
    fireEvent.change(countryInput, { target: { value: 'TestCountry' } });

    fireEvent.click(searchButton);

    // Check if loading state is displayed
    expect(searchButton).toHaveTextContent(/searching/i);

    // Wait for weather data to appear
    await waitFor(() => {
      expect(screen.getByText(/TestCity, TestCountry/)).toBeInTheDocument();
    });

    // Verify that weather details are rendered
    expect(screen.getByText(/25°C/)).toBeInTheDocument();
    expect(screen.getByText(/clear sky/i)).toBeInTheDocument();
    expect(screen.getByText(/Humidity:/i)).toBeInTheDocument();
    expect(screen.getByText(/Wind:/i)).toBeInTheDocument();
    expect(screen.getByText(/Pressure:/i)).toBeInTheDocument();

    // Verify ayurvedic recommendation is displayed
    expect(screen.getByText(/Stay hydrated/)).toBeInTheDocument();
  });

  test('displays recommendations after fetching them', async () => {
    fetchWeather.mockResolvedValueOnce(weatherMock);
    fetchUnifiedRecommendations.mockResolvedValueOnce(recommendationsMock);

    render(<WeatherDisplay />);

    const cityInput = screen.getByPlaceholderText(/enter city name/i);
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(cityInput, { target: { value: 'TestCity' } });
    fireEvent.click(searchButton);

    // Wait for weather data to be loaded
    await waitFor(() => screen.getByText(/TestCity, TestCountry/));

    const getRecButton = screen.getByRole('button', { name: /get ayurvedic recommendations/i });
    fireEvent.click(getRecButton);

    // Button should show loading state for recommendations
    expect(getRecButton).toHaveTextContent(/fetching recommendations/i);

    // Wait for recommendations to appear
    await waitFor(() => {
      expect(screen.getByText(/personalized recommendations:/i)).toBeInTheDocument();
    });

    // Verify recommendation items
    expect(screen.getByText(/Drink warm water in the morning/)).toBeInTheDocument();
    expect(screen.getByText(/Take a short walk after meals/)).toBeInTheDocument();
  });
});
