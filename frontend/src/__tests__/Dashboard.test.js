import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import Dashboard from '../components/Dashboard';
import * as api from '../services/api';

// Mock the fetchRecommendations API method
jest.mock('../services/api');

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('fetches and renders recommendations on initial load', async () => {
    const mockRecommendations = [
      { classification: 'Food', relevance_score: 0.85, content: 'Eat apples' },
      { classification: 'Lifestyle', relevance_score: 0.90, content: 'Morning walk' }
    ];
    api.fetchRecommendations.mockResolvedValueOnce({ recommendations: mockRecommendations });
    
    render(<Dashboard />);
    
    // Wait until recommendations appear
    for (let rec of mockRecommendations) {
      await waitFor(() => expect(screen.getByText(rec.content)).toBeInTheDocument());
    }
  });

  test('displays error message when fetchRecommendations fails', async () => {
    api.fetchRecommendations.mockRejectedValueOnce(new Error('Fetch error'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch recommendations/i)).toBeInTheDocument();
    });
  });

  test('refresh button triggers re-fetch of recommendations', async () => {
    const initialRecommendations = [
      { classification: 'Activity', relevance_score: 0.75, content: 'Yoga session' }
    ];
    api.fetchRecommendations.mockResolvedValueOnce({ recommendations: initialRecommendations });

    render(<Dashboard />);

    // Wait for initial recommendations
    await waitFor(() => {
      expect(screen.getByText(initialRecommendations[0].content)).toBeInTheDocument();
    });

    // Clear the previous mock call count and set up a new resolved value
    api.fetchRecommendations.mockClear();
    const refreshedRecommendations = [
      { classification: 'Diet', relevance_score: 0.80, content: 'Green smoothie' }
    ];
    api.fetchRecommendations.mockResolvedValueOnce({ recommendations: refreshedRecommendations });

    // Click the refresh button
    fireEvent.click(screen.getByRole('button', { name: /refresh/i }));

    // Verify that fetchRecommendations is called
    await waitFor(() => {
      expect(api.fetchRecommendations).toHaveBeenCalledTimes(1);
    });

    // Wait for new recommendations to appear
    await waitFor(() => {
      expect(screen.getByText(refreshedRecommendations[0].content)).toBeInTheDocument();
    });
  });

  test('changing dosha selection triggers a new fetch', async () => {
    const initialRecommendations = [
      { classification: 'Food', relevance_score: 0.80, content: 'Banana smoothie' }
    ];
    api.fetchRecommendations.mockResolvedValueOnce({ recommendations: initialRecommendations });

    render(<Dashboard />);

    // Wait for initial recommendations
    await waitFor(() => {
      expect(screen.getByText(initialRecommendations[0].content)).toBeInTheDocument();
    });

    // Set up the mock for dosha change fetch
    const newDoshaRecommendations = [
      { classification: 'Lifestyle', relevance_score: 0.95, content: 'Meditation session' }
    ];
    api.fetchRecommendations.mockResolvedValueOnce({ recommendations: newDoshaRecommendations });

    // Change dosha from default 'Vata' to 'Pitta'
    const dropdown = screen.getByRole('combobox');
    fireEvent.change(dropdown, { target: { value: 'Pitta' } });

    // Verify new recommendations appear after selection change
    await waitFor(() => {
      expect(screen.getByText(/Meditation session/i)).toBeInTheDocument();
    });
  });
});
