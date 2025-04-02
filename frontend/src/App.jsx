import React, { useState } from 'react';
import DoshaQuiz from './components/DoshaQuiz';
import WeatherDisplay from './components/WeatherDisplay';
import Dashboard from './components/Dashboard';
import ChatComponent from './components/ChatComponent';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Featured articles data
  const featuredArticles = [
    {
      id: 1,
      title: 'Understanding Your Dosha Type',
      excerpt: 'Learn how your unique constitution affects your health and wellness journey.',
      imageUrl: '/static/images/dosha-types.jpg',
    },
    {
      id: 2,
      title: 'Seasonal Ayurvedic Practices',
      excerpt: 'Adapt your lifestyle to the changing seasons for optimal health.',
      imageUrl: '/static/images/seasonal-practices.jpg',
    },
    {
      id: 3,
      title: 'Ayurvedic Herbs for Immunity',
      excerpt: 'Discover powerful herbs that can boost your natural defenses.',
      imageUrl: '/static/images/immunity-herbs.jpg',
    },
    {
      id: 4,
      title: 'Yoga for Dosha Balance',
      excerpt: 'Customize your yoga routine based on your dosha for a balanced body and mind.',
      imageUrl: '/static/images/yoga-dosha.jpg',
    },
    {
      id: 5,
      title: 'Detox with Panchakarma',
      excerpt: 'Explore the ancient detox methods of Panchakarma for renewed energy.',
      imageUrl: '/static/images/panchakarma.jpg',
    },
    {
      id: 6,
      title: 'Herbal Teas & Tisanes',
      excerpt: 'Savor the healing benefits of Ayurvedic herbal teas.',
      imageUrl: '/static/images/herbal-teas.jpg',
    },
    {
      id: 7,
      title: 'Ayurvedic Daily Routine',
      excerpt: 'Establish a balanced daily routine following Ayurvedic principles for optimal health.',
      imageUrl: '/static/images/daily-routine.jpg',
    },
    {
      id: 8,
      title: 'Meditation Techniques',
      excerpt: 'Discover meditation practices that complement your dosha type and promote mental clarity.',
      imageUrl: '/static/images/meditation.jpg',
    },
    {
      id: 9,
      title: 'Ayurvedic Cooking Basics',
      excerpt: 'Learn how to prepare meals that balance your doshas and enhance digestion.',
      imageUrl: '/static/images/ayurvedic-cooking.jpg',
    }
  ];

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  return (
    <div className="min-h-screen bg-light text-dark relative">
      {/* Header with Navigation Tabs */}
      <header className="p-4 bg-primary text-text-light sticky top-0 z-10">
        <h1 className="text-3xl font-bold">Ayurvedic Wellness Hub</h1>
        <nav className="mt-4">
          <button 
            onClick={() => setActiveTab('home')} 
            className={`mr-4 px-4 py-2 rounded transition-colors ${activeTab === 'home' ? 'bg-secondary text-white' : 'bg-light text-dark hover:bg-secondary hover:text-white'}`}
          >
            Home
          </button>
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
        {activeTab === 'home' && (
          <section className="py-8">
            <h2 className="text-3xl font-bold mb-8 text-center">Welcome to Ayurvedic Wellness Hub</h2>
            <p className="text-lg text-center mb-8">
              Discover personalized Ayurvedic recommendations based on your unique constitution and current weather conditions.
            </p>
            <div className="flex flex-col md:flex-row gap-6 justify-center mb-12">
              <button 
                onClick={() => setActiveTab('quiz')} 
                className="bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-opacity-90 transition-colors"
              >
                Take the Dosha Quiz
              </button>
              <button 
                onClick={() => setActiveTab('weather')} 
                className="bg-secondary text-white px-6 py-3 rounded-lg font-medium hover:bg-opacity-90 transition-colors"
              >
                Check Weather Recommendations
              </button>
            </div>
            
            {/* Featured Articles Section */}
            <div className="mt-12">
              <h3 className="text-2xl font-bold mb-6 text-center">Featured Articles</h3>
              <div className="max-h-[600px] overflow-y-auto pr-2">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {featuredArticles.map((article) => {
                    const placeholderImage = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='200' viewBox='0 0 300 200'%3E%3Crect width='300' height='200' fill='%23e0e0e0'/%3E%3Ctext x='50%25' y='50%25' font-family='Arial' font-size='16' text-anchor='middle' dominant-baseline='middle' fill='%23757575'%3EImage not found%3C/text%3E%3C/svg%3E";
                    
                    return (
                      <div key={article.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                        <img 
                          src={`https://picsum.photos/seed/${article.id}/300/200`} 
                          alt={article.title} 
                          onError={(e) => { e.target.src = placeholderImage; }} 
                          className="w-full h-48 object-cover rounded-t-lg"
                        />
                        <div className="p-4">
                          <h4 className="text-xl font-semibold mb-2">{article.title}</h4>
                          <p className="text-gray-600">{article.excerpt}</p>
                          <button className="mt-4 text-primary font-medium hover:underline">Read more</button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </section>
        )}
        {activeTab === 'quiz' && <DoshaQuiz />}
        {activeTab === 'weather' && <WeatherDisplay />}
        {activeTab === 'dashboard' && <Dashboard />}
      </main>

      <footer className="p-4 bg-primary text-text-light text-center">
        <p>© 2025 Ayurvedic Wellness Hub - Balance your life with Ayurveda</p>
      </footer>

      <section className="p-4 bg-secondary text-text-light text-center">
        <p>Developer Anindya - developed for a university project for KIIT. Email: 2275073@kiit.ac.in</p>
      </section>

      {/* Floating Chat Button */}
      <button 
        onClick={toggleChat} 
        className="fixed bottom-6 right-6 bg-secondary text-white w-16 h-16 rounded-full shadow-lg flex items-center justify-center hover:bg-opacity-90 transition-colors z-20"
        aria-label="Open chat"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </button>

      {/* Chat Component */}
      <div className={`fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm z-30 transition-opacity ${isChatOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`} onClick={toggleChat}></div>
      {isChatOpen && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-11/12 md:w-4/5 lg:w-3/4 h-4/5 z-40 overflow-hidden flex items-center justify-center transition-all duration-300 scale-100 opacity-100">
          <ChatComponent isOpen={isChatOpen} />
        </div>
      )}
    </div>
  );
}

export default App;
