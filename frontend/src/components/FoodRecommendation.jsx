import React, { useState } from 'react';
import './FoodRecommendation.css';

const FoodRecommendation = () => {
  const [foodQuery, setFoodQuery] = useState('');
  const [selectedDosha, setSelectedDosha] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!foodQuery || !selectedDosha) {
      setError('Please enter a food query and select a dosha');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: foodQuery,
          dosha: selectedDosha
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError('Error fetching recommendations. Please try again.');
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="food-recommendation-container">
      <h2>Ayurvedic Food Recommendations</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="food-query">Food Query:</label>
          <input
            type="text"
            id="food-query"
            data-cy="food-query-input"
            value={foodQuery}
            onChange={(e) => setFoodQuery(e.target.value)}
            placeholder="Enter food or ingredient"
            className="food-input"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="dosha-select">Select Dosha:</label>
          <select
            id="dosha-select"
            data-cy="dosha-select"
            value={selectedDosha}
            onChange={(e) => setSelectedDosha(e.target.value)}
            className="dosha-select"
          >
            <option value="">Select a dosha</option>
            <option value="vata">Vata</option>
            <option value="pitta">Pitta</option>
            <option value="kapha">Kapha</option>
          </select>
        </div>
        
        <button 
          type="submit" 
          data-cy="submit-food-query" 
          className="submit-button"
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Get Recommendations'}
        </button>
      </form>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="results-container" data-cy="food-recommendations">
        {loading ? (
          <p>Loading recommendations...</p>
        ) : recommendations.length > 0 ? (
          <div>
            <h3>Recommended foods for {selectedDosha} dosha:</h3>
            <ul className="recommendations-list">
              {recommendations.map((recommendation, index) => (
                <li key={index}>{recommendation}</li>
              ))}
            </ul>
          </div>
        ) : !error && foodQuery && selectedDosha ? (
          <p>No recommendations found. Try a different query or dosha.</p>
        ) : null}
      </div>
    </div>
  );
};

export default FoodRecommendation;