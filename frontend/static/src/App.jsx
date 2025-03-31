import React, { useState } from 'react';
import DoshaQuiz from './components/DoshaQuiz';
import WeatherDisplay from './components/WeatherDisplay';
import Dashboard from './components/Dashboard';

function App() {
  const [activeTab, setActiveTab] = useState('quiz');

  return (
    <div className="min-h-screen bg-light text-dark">
      <header className="p-4 bg-primary text-text-light">
        <h1 className="text-3xl font-bold">Ayurvedic Wellness Hub</h1>
        <nav className="mt-4">
          <button 
            onClick={() => setActiveTab('quiz')} 
            className={`mr-4 px-4 py-2 rounded transition-colors ${activeTab === 'quiz' ? 'bg-secondary text-white' : 'bg-light text-dark hover:bg-secondary hover:text-white'}`}
          >
            Dosha Quiz
          </button>
          <button 
            onClick={() => setActiveTab('weather')} 
            className={`mr-4 px-4 py-2 rounded transition-colors ${activeTab === 'weather' ? 'bg-secondary text-white' : 'bg-light text-dark hover:bg-secondary hover:text-white'}`}
          >
            Weather
          </button>
          <button 
            onClick={() => setActiveTab('dashboard')} 
            className={`px-4 py-2 rounded transition-colors ${activeTab === 'dashboard' ? 'bg-secondary text-white' : 'bg-light text-dark hover:bg-secondary hover:text-white'}`}
          >
            Recommendations
          </button>
        </nav>
      </header>
      <main className="p-4 container mx-auto">
        {activeTab === 'quiz' && <DoshaQuiz />}
        {activeTab === 'weather' && <WeatherDisplay />}
        {activeTab === 'dashboard' && <Dashboard />}
      </main>
      <footer className="p-4 bg-primary text-text-light text-center">
        <p>© 2023 Ayurvedic Wellness Hub - Balance your life with Ayurveda</p>
      </footer>
    </div>
  );
}

export default App;