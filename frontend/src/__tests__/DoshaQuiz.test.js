import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DoshaQuiz from '../components/DoshaQuiz';
import { fetchDosha } from '../services/api';

jest.mock('../services/api', () => ({
  fetchDosha: jest.fn(),
}));


describe('DoshaQuiz Component', () => {
  beforeEach(() => {
    fetchDosha.mockClear();
    localStorage.clear();
  });

  test('renders all quiz questions', () => {
    render(<DoshaQuiz />);
    // Verify that all quiz questions are rendered
    expect(screen.getByText('What is your body frame?')).toBeInTheDocument();
    expect(screen.getByText('What is your skin type?')).toBeInTheDocument();
    expect(screen.getByText('What is your hair type?')).toBeInTheDocument();
    expect(screen.getByText('How would you describe your appetite?')).toBeInTheDocument();
    expect(screen.getByText('How is your digestion?')).toBeInTheDocument();
    expect(screen.getByText('What weather do you prefer?')).toBeInTheDocument();
    expect(screen.getByText('How would you describe your sleep pattern?')).toBeInTheDocument();
    expect(screen.getByText('How do you typically respond to stress?')).toBeInTheDocument();
    expect(screen.getByText('How would you describe your speech pattern?')).toBeInTheDocument();
    expect(screen.getByText('What is your typical activity level?')).toBeInTheDocument();
  });

  test('updates state when user selects an option', () => {
    render(<DoshaQuiz />);
    // Select an option for a question to verify state update
    const optionRadio = screen.getByLabelText('Thin and lean, difficulty gaining weight');
    fireEvent.click(optionRadio);
    expect(optionRadio).toBeChecked();
  });

  test('calls fetchDosha and displays result upon submission', async () => {
    // Setup the mock response for fetchDosha
    fetchDosha.mockResolvedValueOnce({ dosha: 'vata', message: 'Test message' });

    render(<DoshaQuiz />);

    // Selections mapping: key is question text option label, value is the expected value in the payload
    const selections = {
      'What is your body frame?': 'Thin and lean, difficulty gaining weight',
      'What is your skin type?': 'Dry, rough, or thin',
      'What is your hair type?': 'Dry, frizzy, or brittle',
      'How would you describe your appetite?': 'Variable, sometimes forget to eat',
      'How is your digestion?': 'Irregular, tendency to bloat',
      'What weather do you prefer?': 'Warm and humid, dislike cold',
      'How would you describe your sleep pattern?': 'Light, easily disturbed',
      'How do you typically respond to stress?': 'Become anxious or worried',
      'How would you describe your speech pattern?': 'Fast, sometimes jumps topics',
      'What is your typical activity level?': 'Hyperactive, restless'
    };

    // Simulate user selecting an option for each quiz question
    Object.values(selections).forEach(label => {
      const radio = screen.getByLabelText(label);
      fireEvent.click(radio);
      expect(radio).toBeChecked();
    });

    const submitButton = screen.getByRole('button', { name: /submit quiz/i });
    fireEvent.click(submitButton);

    await waitFor(() => expect(fetchDosha).toHaveBeenCalledTimes(1));
    // Verify that fetchDosha is called with the expected responses
    expect(fetchDosha).toHaveBeenCalledWith({
      body_frame: 'thin',
      skin_type: 'dry',
      hair_type: 'dry',
      appetite: 'variable',
      digestion: 'irregular',
      weather_preference: 'warm',
      sleep_pattern: 'light',
      stress_response: 'anxious',
      speech_pattern: 'fast',
      activity_level: 'hyperactive'
    });

    // Verify that the result is rendered
    await waitFor(() => {
      expect(screen.getByText(/your dosha:/i)).toBeInTheDocument();
      expect(screen.getByText(/vata/i)).toBeInTheDocument();
      expect(screen.getByText(/test message/i)).toBeInTheDocument();
    });

    // Verify that localStorage is updated with the dosha result
    const storedResult = localStorage.getItem('doshaResult');
    expect(storedResult).not.toBeNull();
    const parsedResult = JSON.parse(storedResult);
    expect(parsedResult.dosha).toBe('vata');
  });
});
