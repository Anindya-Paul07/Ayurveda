import React, { useState, useRef, useEffect } from 'react';
import DOMPurify from 'dompurify';
import { fetchGeneralInfo, fetchRemedies } from '../services/api';
import logger from '../utils/logger';

const ChatComponent = ({ isOpen }) => {
  // State management
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [activeTab, setActiveTab] = useState('chat'); // Possible values: 'chat', 'history'
  const [isProcessing, setIsProcessing] = useState(false);
  const [remedies, setRemedies] = useState({});
  const messagesEndRef = useRef(null);
  const chatInputRef = useRef(null);
  const [chatHistory, setChatHistory] = useState([]);

  // Welcome message
  const WELCOME_MESSAGE = `
    **Welcome to AyurBot!**  
    I'm your Ayurvedic consultant. How can I help you today?  
    - Ask about Ayurvedic principles, remedies, or personalized recommendations
  `;

  // Scroll to bottom of messages when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chat is opened
  useEffect(() => {
    if (isOpen && chatInputRef.current) {
      chatInputRef.current.focus();
    }
  }, [isOpen]);

  // Add welcome message on component mount
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage = {
        id: Date.now(),
        text: WELCOME_MESSAGE,
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };
      setMessages([welcomeMessage]);
    }
  }, []);

  // Load chat history from localStorage when component mounts
  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem('ayurvedaChatHistory');
      if (savedHistory) {
        setChatHistory(JSON.parse(savedHistory));
      }
    } catch (error) {
      logger.error('Error loading chat history:', error);
    }
  }, []);

  // Save chat history to localStorage when it changes
  useEffect(() => {
    try {
      localStorage.setItem('ayurvedaChatHistory', JSON.stringify(chatHistory));
    } catch (error) {
      logger.error('Error saving chat history:', error);
    }
  }, [chatHistory]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  const handleInputChange = (e) => {
    setNewMessage(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const fetchRemediesFromAPI = async () => {
    try {
      const data = await fetchRemedies();
      if (data) {
        setRemedies(data);
      }
    } catch (error) {
      logger.error('Error fetching remedies:', error);
      logger.error('Error details:', error.message);
    }
  };

  const sendMessage = async () => {
    if (newMessage.trim() === '' || isProcessing) return;

    const userMessage = {
      id: Date.now(),
      text: newMessage,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    // Update messages state with user message
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // Save message to chat history
    const newChatEntry = {
      id: Date.now(),
      userMessage: newMessage,
      timestamp: new Date().toISOString()
    };
    setChatHistory(prevHistory => [...prevHistory, newChatEntry]);
    
    const messageToSend = newMessage.trim();
    setNewMessage('');
    setIsProcessing(true);

    try {
      logger.log('Sending message to Ayurvedic expert:', messageToSend);
      
      // Using the centralized API service for better maintainability
      const response = await fetchGeneralInfo(messageToSend);
      logger.log('API response received:', response);
      
      if (response && response.response) {
        const botResponse = {
          id: Date.now() + 1,
          text: response.response,
          sender: 'bot',
          timestamp: new Date().toISOString(),
        };
        
        // Update messages state with bot response
        setMessages(prevMessages => [...prevMessages, botResponse]);
        
        // If the response contains remedies data, update the remedies state
        if (response.remedies) {
          setRemedies(response.remedies);
        } else {
          // Otherwise fetch remedies separately
          fetchRemediesFromAPI();
        }
      } else {
        logger.error('Invalid response structure:', response);
        throw new Error('Invalid response from server: Missing response field');
      }
    } catch (error) {
      // Enhanced error logging
      logger.error('Error sending message:', error);
      logger.error('Error details:', error.response ? {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data
      } : error.message);
      
      // Create error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'I apologize, but I encountered an issue while processing your request. Please try again in a moment.',
        sender: 'system',
        timestamp: new Date().toISOString(),
      };
      
      // Update messages state with error message
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatMessage = (message) => {
    if (typeof message.text !== 'string') return message.text;
    const sanitizedText = DOMPurify.sanitize(message.text);
    return sanitizedText
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/(\d+)\./g, '<span class="list-number">$1.</span>')
      .replace(/- (.*?)(?:\n|$)/g, '<div class="bullet-point">• $1</div>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="text-blue-500 underline">$1</a>')
      .split('\n\n')
      .map(para => `<p class="mb-2">${para.replace(/\n/g, '<br>')}</p>`)
      .join('');
  };

  const renderMessages = () => {
    return messages.map((message) => (
      <div 
        key={message.id} 
        className={`mb-4 ${
          message.sender === 'user' 
            ? 'ml-auto bg-green-100 text-right' 
            : message.sender === 'system'
              ? 'mr-auto bg-yellow-100'
              : 'mr-auto bg-gray-100'
        } rounded-lg p-3 max-w-[80%] shadow-sm`}
        data-cy={message.sender === 'bot' ? "bot-response" : undefined}
      >
        <div className="text-sm font-medium">
          {message.sender === 'user' 
            ? 'You' 
            : message.sender === 'system' 
              ? 'System' 
              : 'Ayurvedic Expert'}
        </div>
        <div 
          className="mt-1"
          dangerouslySetInnerHTML={{ __html: formatMessage(message) }}
        />
        <div className="text-xs text-gray-500 mt-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    ));
  };

  const renderRemedies = () => {
    if (Object.keys(remedies).length === 0) {
      return (
        <div className="text-center text-gray-500 py-4">
          <p>No remedies tracked yet.</p>
        </div>
      );
    }

    return (
      <div className="mt-4 border-t pt-4">
        <h4 className="font-medium text-green-600 mb-2">Recommended Remedies</h4>
        <ul className="space-y-2">
          {Object.entries(remedies).map(([disease, remedyList]) => (
            <li key={disease} className="border-b pb-2">
              <h5 className="font-medium">{disease.charAt(0).toUpperCase() + disease.slice(1)}</h5>
              {remedyList.map((remedy, index) => (
                <p key={index} className="text-sm">{remedy}</p>
              ))}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  // Render chat history
  const renderChatHistory = () => {
    if (chatHistory.length === 0) {
      return (
        <div className="text-center text-gray-500 py-8">
          <p>No chat history available</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {chatHistory.map((entry) => (
          <div key={entry.id} className="border rounded-lg p-4 hover:bg-gray-50">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">Conversation</span>
              <span className="text-xs text-gray-500">
                {new Date(entry.timestamp).toLocaleString()}
              </span>
            </div>
            <div className="mb-2">
              <span className="text-sm font-medium">You: </span>
              <span className="text-sm">{entry.userMessage}</span>
            </div>
            {entry.botResponse && (
              <div>
                <span className="text-sm font-medium">AyurBot: </span>
                <span className="text-sm">{entry.botResponse}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <>
      {/* Chat Container */}
      <div 
        className={`rounded-lg shadow-xl z-50 flex flex-col transition-all duration-300 transform bg-transparent ${
          isOpen ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0 pointer-events-none'
        }`}
        style={{ maxHeight: '80vh', width: '100%', height: '100%' }}
      >
        {/* Chat Header */}
        <div className="bg-green-600 text-white p-4 rounded-t-lg flex justify-between items-center">
          <h3 className="font-medium">Ayurvedic Chat Support</h3>
        </div>

        {/* Chat Tabs */}
        <div className="flex border-b">
          <button
            className={`flex-1 py-2 px-4 text-center ${
              activeTab === 'chat' 
                ? 'border-b-2 border-green-600 text-green-600 font-medium' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => handleTabChange('chat')}
            data-cy="chat-tab"
          >
            Chat
          </button>
          <button
            className={`flex-1 py-2 px-4 text-center ${
              activeTab === 'history' 
                ? 'border-b-2 border-green-600 text-green-600 font-medium' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => handleTabChange('history')}
          >
            History
          </button>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 p-4 overflow-y-auto bg-transparent">
          {activeTab === 'chat' ? (
            messages.length > 0 ? (
              <div className="flex flex-col" data-cy="chat-messages">
                {renderMessages()}
                {Object.keys(remedies).length > 0 && renderRemedies()}
                <div ref={messagesEndRef} />
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p>Start a conversation with our Ayurvedic expert</p>
              </div>
            )
          ) : (
            <div className="text-center text-gray-500 py-8">
              {messages.length > 0 ? (
                <div className="flex flex-col">
                  <h3 className="font-medium mb-4">Chat History</h3>
                  {renderMessages()}
                </div>
              ) : (
                <p>Your chat history will appear here once you start a conversation</p>
              )}
            </div>
          )}
        </div>

        {/* Chat Input - Only show in chat tab */}
        {activeTab === 'chat' && (
          <div className="border-t p-4">
            <div className="flex">
              <input
                type="text"
                ref={chatInputRef}
                value={newMessage}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 border rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                disabled={isProcessing}
                aria-label="Chat message input"
                data-cy="chat-input"
              />
              <button
                onClick={sendMessage}
                disabled={newMessage.trim() === '' || isProcessing}
                className={`bg-green-600 text-white px-4 py-2 rounded-r-lg ${
                  newMessage.trim() === '' || isProcessing
                    ? 'opacity-50 cursor-not-allowed' 
                    : 'hover:bg-green-700'
                }`}
                aria-label="Send message"
                data-cy="send-button"
              >
                {isProcessing ? (
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
              </button>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Press Enter to send your message
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default ChatComponent;
