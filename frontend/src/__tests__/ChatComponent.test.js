import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatComponent from '../components/ChatComponent';

// Mock the API call module
jest.mock('../services/api', () => ({
  fetchGeneralInfo: jest.fn(),
}));

import { fetchGeneralInfo } from '../services/api';

// Mock scrollIntoView to avoid jsdom errors
Element.prototype.scrollIntoView = jest.fn();

// Helper function to clear localStorage before each test
beforeEach(() => {
  localStorage.clear();
  jest.clearAllMocks();
});

describe('ChatComponent', () => {
  const setupComponent = (props = { isOpen: true }) => {
    return render(<ChatComponent {...props} />);
  };

  test('renders welcome message on mount', async () => {
    setupComponent();
    // The welcome message is rendered as HTML, so check for a unique part of it
    // Using text matcher without markdown chars
    const welcomeElement = await screen.findByText(/Welcome to AyurBot!/i);
    expect(welcomeElement).toBeInTheDocument();
  });

  test('handles user input and sends message successfully', async () => {
    // Mock successful response from fetchGeneralInfo
    fetchGeneralInfo.mockResolvedValueOnce({ response: 'Bot reply message' });

    setupComponent();
    
    // Wait for the welcome message to appear
    await screen.findByText(/Welcome to AyurBot!/i);

    const input = screen.getByPlaceholderText(/Type your message.../i);
    
    // Simulate user typing a message
    fireEvent.change(input, { target: { value: 'Hello AyurBot' } });
    expect(input.value).toBe('Hello AyurBot');

    // Simulate pressing Enter key
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

    // Verify user's message appears in chat
    const userMessage = await screen.findByText(/Hello AyurBot/i);
    expect(userMessage).toBeInTheDocument();

    // Wait for the API call and bot response
    const botResponse = await waitFor(() => screen.getByText(/Bot reply message/i), { timeout: 3000 });
    expect(botResponse).toBeInTheDocument();

    // Check that fetchGeneralInfo was called with the trimmed message
    expect(fetchGeneralInfo).toHaveBeenCalledWith('Hello AyurBot');

    // Verify that chat history is updated in localStorage
    const chatHistory = JSON.parse(localStorage.getItem('ayurvedaChatHistory'));
    expect(chatHistory).toBeTruthy();
    expect(chatHistory.find(entry => entry.userMessage === 'Hello AyurBot')).toBeTruthy();
  });

  test('displays error message when API call fails', async () => {
    // Mock API failure
    fetchGeneralInfo.mockRejectedValueOnce(new Error('API Error'));

    setupComponent();
    
    // Wait for the welcome message to appear
    await screen.findByText(/Welcome to AyurBot!/i);

    const input = screen.getByPlaceholderText(/Type your message.../i);
    
    // Simulate user sending a message
    fireEvent.change(input, { target: { value: 'Test error scenario' } });
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

    // Verify user's message appears
    const userMessage = await screen.findByText(/Test error scenario/i);
    expect(userMessage).toBeInTheDocument();

    // Wait for the API error to be handled and error message displayed
    const errorMessage = await waitFor(() => screen.getByText(/I apologize, but I encountered an issue while processing your request/i), { timeout: 3000 });
    expect(errorMessage).toBeInTheDocument();

    // Ensure fetchGeneralInfo was called
    expect(fetchGeneralInfo).toHaveBeenCalledWith('Test error scenario');
  });
});
