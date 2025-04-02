import React, { useState } from 'react';
import ChatComponent from './ChatComponent';
import DoshaQuiz from './DoshaQuiz';
import WeatherDisplay from './WeatherDisplay';
import FoodRecommendation from './FoodRecommendation';
import Dashboard from './Dashboard';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Ayurveda Health Assistant</h1>
        <nav className="app-navigation">
          <button 
            className={activeTab === 'chat' ? 'active' : ''} 
            onClick={() => setActiveTab('chat')}
            data-cy="chat-tab"
          >
            Chat
          </button>
          <button 
            className={activeTab === 'dosha' ? 'active' : ''} 
            onClick={() => setActiveTab('dosha')}
            data-cy="dosha-quiz-tab"
          >
            Dosha Quiz
          </button>
          <button 
            className={activeTab === 'weather' ? 'active' : ''} 
            onClick={() => setActiveTab('weather')}
            data-cy="weather-tab"
          >
            Weather
          </button>
          <button 
            className={activeTab === 'food' ? 'active' : ''} 
            onClick={() => setActiveTab('food')}
            data-cy="food-recommendation-tab"
          >
            Food Recommendation
          </button>
        </nav>
      </header>
      
      <main className="app-content">
        {activeTab === 'chat' && <ChatComponent />}
        {activeTab === 'dosha' && <DoshaQuiz />}
        {activeTab === 'weather' && <WeatherDisplay />}
        {activeTab === 'food' && <Dashboard />}
      </main>
      
      <footer className="app-footer">
        <p>© 2025 Ayurveda Health Assistant</p>
      </footer>
      
      <div className="app-about text-center p-2">
        <p>Developer Anindya - developed for a university project for KIIT. Email: 2275073@kiit.ac.in</p>
      </div>
    </div>
  );
}

export default App;
