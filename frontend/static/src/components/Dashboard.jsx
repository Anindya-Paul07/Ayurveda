import React, { useEffect, useState } from 'react';
import { fetchRecommendations } from '../services/api';

function Dashboard() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dosha, setDosha] = useState('Vata'); // Default dosha, could be obtained from context or props

  const fetchRecommendationsData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Use the API service function with parameters object
      const data = await fetchRecommendations({ dosha });
      setRecommendations(data.recommendations || []);
    } catch (err) {
      setError('Failed to fetch recommendations. Please try again later.');
      console.error('Recommendation fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendationsData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dosha]); // Re-fetch when dosha changes

  const handleDoshaChange = (e) => {
    setDosha(e.target.value);
  };

  const handleRefresh = () => {
    fetchRecommendationsData();
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-primary-800">Daily Ayurvedic Recommendations</h2>
        <div className="flex items-center space-x-4">
          <select 
            value={dosha} 
            onChange={handleDoshaChange}
            className="p-2 border rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="Vata">Vata</option>
            <option value="Pitta">Pitta</option>
            <option value="Kapha">Kapha</option>
          </select>
          <button 
            onClick={handleRefresh}
            className="px-4 py-2 bg-primary-600 text-white rounded shadow hover:bg-primary-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
      )}

      {!loading && recommendations.length === 0 && !error && (
        <div className="text-center py-8 text-gray-600">
          <p>No recommendations available for the selected dosha.</p>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {recommendations.map((rec, index) => (
          <div 
            key={index} 
            className="p-5 border rounded-lg shadow-md bg-white hover:shadow-lg transition-shadow"
          >
            <div className="flex justify-between items-start mb-3">
              <p className="font-semibold text-primary-700 uppercase tracking-wide">
                {rec.classification}
              </p>
              <span className="inline-block px-2 py-1 text-xs font-medium rounded-full bg-primary-100 text-primary-800">
                Score: {typeof rec.relevance_score === 'number' ? rec.relevance_score.toFixed(2) : rec.relevance_score}
              </span>
            </div>
            <p className="text-gray-700">{rec.content}</p>
            {rec.additional_info && (
              <p className="mt-2 text-sm text-gray-600 italic">{rec.additional_info}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
