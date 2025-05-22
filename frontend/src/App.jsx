import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Providers
import { AppThemeProvider } from './providers/ThemeProvider';

// Layout
import Layout from './components/layout/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import ChatPage from './pages/ChatPage';
import MetricsDashboard from './pages/MetricsDashboard';
import DoshaAnalysis from './pages/DoshaAnalysis';
import DoshaComparison from './pages/tools/DoshaComparison';
import SymptomAnalyzer from './pages/tools/SymptomAnalyzer';
import HerbRecommender from './pages/tools/HerbRecommender';
import DiseasePredictor from './pages/tools/DiseasePredictor';
import NotFound from './pages/NotFound';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppThemeProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="chat" element={<ChatPage />} />
              <Route path="metrics" element={<MetricsDashboard />} />
              <Route path="dosha-analysis" element={<DoshaAnalysis />} />
              <Route path="tools">
                <Route path="dosha" element={<DoshaComparison />} />
                <Route path="symptoms" element={<SymptomAnalyzer />} />
                <Route path="herbs" element={<HerbRecommender />} />
                <Route path="disease-predictor" element={<DiseasePredictor />} />
              </Route>
              <Route path="404" element={<NotFound />} />
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Route>
          </Routes>
        </Router>
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} position="bottom-right" />
        )}
      </AppThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
