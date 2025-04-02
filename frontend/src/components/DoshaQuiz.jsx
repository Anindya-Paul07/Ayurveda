import React, { useState } from 'react';
import { fetchDosha } from '../services/api';

const quizQuestions = [
  { 
    id: 'body_frame', 
    question: 'What is your body frame?', 
    options: [
      { value: 'thin', label: 'Thin and lean, difficulty gaining weight' },
      { value: 'medium', label: 'Medium build, gains and loses weight easily' },
      { value: 'large', label: 'Larger build, gains weight easily, difficulty losing it' }
    ] 
  },
  { 
    id: 'skin_type', 
    question: 'What is your skin type?', 
    options: [
      { value: 'dry', label: 'Dry, rough, or thin' },
      { value: 'sensitive', label: 'Sensitive, warm, or reddish' },
      { value: 'oily', label: 'Oily, thick, or smooth' }
    ] 
  },
  { 
    id: 'hair_type', 
    question: 'What is your hair type?', 
    options: [
      { value: 'dry', label: 'Dry, frizzy, or brittle' },
      { value: 'fine', label: 'Fine, straight, or early graying' },
      { value: 'thick', label: 'Thick, oily, or wavy' }
    ] 
  },
  { 
    id: 'appetite', 
    question: 'How would you describe your appetite?', 
    options: [
      { value: 'variable', label: 'Variable, sometimes forget to eat' },
      { value: 'strong', label: 'Strong, irritable when hungry' },
      { value: 'steady', label: 'Steady, can skip meals without discomfort' }
    ] 
  },
  { 
    id: 'digestion', 
    question: 'How is your digestion?', 
    options: [
      { value: 'irregular', label: 'Irregular, tendency to bloat' },
      { value: 'quick', label: 'Quick, strong, sometimes get heartburn' },
      { value: 'slow', label: 'Slow but steady, rarely upset' }
    ] 
  },
  { 
    id: 'weather_preference', 
    question: 'What weather do you prefer?', 
    options: [
      { value: 'warm', label: 'Warm and humid, dislike cold' },
      { value: 'cool', label: 'Cool and dry, dislike heat' },
      { value: 'moderate', label: 'Moderate, adapt easily to changes' }
    ] 
  },
  { 
    id: 'sleep_pattern', 
    question: 'How would you describe your sleep pattern?', 
    options: [
      { value: 'light', label: 'Light, easily disturbed' },
      { value: 'moderate', label: 'Moderate but need less than 8 hours' },
      { value: 'heavy', label: 'Heavy, difficult to wake up' }
    ] 
  },
  { 
    id: 'stress_response', 
    question: 'How do you typically respond to stress?', 
    options: [
      { value: 'anxious', label: 'Become anxious or worried' },
      { value: 'irritable', label: 'Become irritable or aggressive' },
      { value: 'withdrawn', label: 'Become withdrawn or depressed' }
    ] 
  },
  { 
    id: 'speech_pattern', 
    question: 'How would you describe your speech pattern?', 
    options: [
      { value: 'fast', label: 'Fast, sometimes jumps topics' },
      { value: 'sharp', label: 'Sharp, precise, argumentative' },
      { value: 'slow', label: 'Slow, methodical, soothing' }
    ] 
  },
  { 
    id: 'activity_level', 
    question: 'What is your typical activity level?', 
    options: [
      { value: 'hyperactive', label: 'Hyperactive, restless' },
      { value: 'moderate', label: 'Moderate, purposeful' },
      { value: 'relaxed', label: 'Relaxed, prefer routine' }
    ] 
  }
];

function DoshaQuiz() {
  const [responses, setResponses] = useState({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (id, value) => {
    setResponses({ ...responses, [id]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Create a copy of the current responses
    const completeResponses = { ...responses };
    
    // Auto-fill any unanswered questions with the first option's value
    quizQuestions.forEach(question => {
      if (!completeResponses[question.id]) {
        completeResponses[question.id] = question.options[0].value;
      }
    });
    
    // Update the responses state with the complete set
    setResponses(completeResponses);
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const data = await fetchDosha(completeResponses);
      setResult(data);
      setError(null);
      
      // Validate that we have the expected data structure before storing
      if (data && data.dosha) {
        // Store dosha result in localStorage for use by WeatherDisplay component
        localStorage.setItem('doshaResult', JSON.stringify(data));
      } else {
        console.error('Invalid dosha result format:', data);
        setError('Received invalid dosha result format from server');
      }
    } catch (err) {
      console.error('Error fetching dosha:', err);
      // Clear any previous result from localStorage if there's an error
      localStorage.removeItem('doshaResult');
      
      // Handle different error scenarios
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setError(err.response.data?.error || `Server error: ${err.response.status}`);
      } else if (err.request) {
        // The request was made but no response was received
        setError('No response from server. Please check your connection and try again.');
      } else {
        // Something happened in setting up the request that triggered an Error
        setError(err.message || 'Failed to submit quiz. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const progressPercentage = Math.round((Object.keys(responses).length / quizQuestions.length) * 100);

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md" data-cy="dosha-quiz-container">
      <h2 className="text-3xl font-bold mb-6 text-center text-primary">Discover Your Dosha</h2>
      <p className="mb-6 text-gray-600 text-center">
        Answer the following questions to discover your Ayurvedic constitution (Dosha).
        This will help us provide personalized food and lifestyle recommendations.
      </p>
      
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-6">
        <div 
          className="bg-primary h-2.5 rounded-full transition-all duration-300" 
          style={{ width: `${progressPercentage}%` }}
        ></div>
      </div>
      <p className="text-sm text-gray-500 mb-6 text-right">{progressPercentage}% complete</p>
      
      <form onSubmit={handleSubmit} className="space-y-8">
        {quizQuestions.map((q, index) => (
          <div 
            key={q.id} 
            className="p-4 border border-gray-200 rounded-lg hover:border-primary transition-colors"
            data-cy={`question-${index+1}`}
          >
            <p className="font-semibold text-lg mb-3">{q.question}</p>
            <div className="space-y-2">
              {q.options.map((option) => (
                <label 
                  key={option.value} 
                  className={`block p-3 border rounded-lg cursor-pointer transition-all ${
                    responses[q.id] === option.value 
                      ? 'bg-primary-light border-primary' 
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                  data-cy={`option-${option.value}`}
                >
                  <div className="flex items-center">
                    <input
                      type="radio"
                      name={q.id}
                      value={option.value}
                      checked={responses[q.id] === option.value}
                      onChange={(e) => handleChange(q.id, e.target.value)}
                      className="form-radio text-primary mr-3"
                    />
                    <span>{option.label}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>
        ))}
        
        <button 
          type="submit" 
          className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-colors ${
            isSubmitting 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-primary hover:bg-primary-dark'
          }`}
          disabled={isSubmitting}
          data-cy="submit-quiz-button"
        >
          {isSubmitting ? 'Analyzing...' : 'Submit Quiz'}
        </button>
      </form>
      
      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {error}
        </div>
      )}
      
      {result && (
        <div className="mt-8 p-6 border-2 border-primary rounded-lg shadow-lg bg-primary-light" data-cy="dosha-result">
          <h3 className="text-2xl font-bold mb-3">Your Dosha: <span className="text-primary">{result.dosha}</span></h3>
          <p className="text-gray-700 leading-relaxed">{result.message}</p>
          
          <div className="mt-6 pt-4 border-t border-gray-200" data-cy="dosha-recommendations">
            <p className="font-medium text-gray-700">
              Your personalized food and lifestyle recommendations are now available on your dashboard.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default DoshaQuiz;
