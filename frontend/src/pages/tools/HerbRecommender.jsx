import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Tabs,
  Tab,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Spa as SpaIcon,
  CompareArrows as CompareArrowsIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
} from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import api from '../../services/api';
import HerbComparisonView from '../../components/herbs/HerbComparisonView';
import HerbRecommendationView from '../../components/herbs/HerbRecommendationView';
import FavoriteHerbsView from '../../components/herbs/FavoriteHerbsView';

const HerbRecommender = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();
  
  const [query, setQuery] = useState('');
  const [activeTab, setActiveTab] = useState('comparison');
  const [recommendationResult, setRecommendationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expanded, setExpanded] = useState('panel1');
  const [favorites, setFavorites] = useState(() => {
    // Load favorites from localStorage
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('favoriteHerbs');
      return saved ? JSON.parse(saved) : [];
    }
    return [];
  });

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Handle accordion expansion
  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };

  // Handle input change
  const handleInputChange = (event) => {
    setQuery(event.target.value);
  };

  // Toggle favorite status of an herb
  const toggleFavorite = (herbName) => {
    setFavorites(prevFavorites => {
      const newFavorites = prevFavorites.includes(herbName)
        ? prevFavorites.filter(name => name !== herbName)
        : [...prevFavorites, herbName];
      
      // Save to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('favoriteHerbs', JSON.stringify(newFavorites));
      }
      
      return newFavorites;
    });
  };

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!query.trim()) {
      enqueueSnackbar('Please enter a condition, symptom, or question', { variant: 'warning' });
      return;
    }
    
    try {
      setIsLoading(true);
      const result = await queryClient.fetchQuery({
        queryKey: ['herbRecommendations', query],
        queryFn: () => api.getHerbRecommendations(query, 'rag', 'agentic'),
      });
      setRecommendationResult(result);
      setActiveTab('comparison');
    } catch (err) {
      enqueueSnackbar('Error getting herb recommendations', { variant: 'error' });
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    if (query) {
      handleSubmit({ preventDefault: () => {} });
    }
  };

  // Render result section
  const renderResult = () => {
    if (isLoading) {
      return (
        <Box display="flex" justifyContent="center" my={8}>
          <CircularProgress />
        </Box>
      );
    }

    if (!recommendationResult) {
      return (
        <Box textAlign="center" my={8}>
          <SpaIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Enter a condition, symptom, or question to compare herb recommendations
          </Typography>
        </Box>
      );
    }

    return (
      <Box mt={4}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant={isMobile ? 'scrollable' : 'standard'}
          scrollButtons="auto"
          sx={{ mb: 3 }}
        >
          <Tab label="Comparison" value="comparison" icon={<CompareArrowsIcon />} />
          <Tab label="RAG Recommendations" value="rag" />
          <Tab label="Agentic Recommendations" value="agentic" />
          <Tab 
            label={
              <Box display="flex" alignItems="center">
                <FavoriteIcon sx={{ color: 'error.main', mr: 0.5 }} />
                Favorites
                {favorites.length > 0 && (
                  <Box 
                    component="span" 
                    sx={{
                      ml: 1,
                      bgcolor: 'error.main',
                      color: 'white',
                      borderRadius: '10px',
                      px: 0.8,
                      py: 0.1,
                      fontSize: '0.75rem',
                    }}
                  >
                    {favorites.length}
                  </Box>
                )}
              </Box>
            } 
            value="favorites" 
          />
        </Tabs>

        {activeTab === 'comparison' && (
          <HerbComparisonView 
            ragResult={recommendationResult.rag} 
            agenticResult={recommendationResult.agentic}
            favorites={favorites}
            onToggleFavorite={toggleFavorite}
          />
        )}
        
        {activeTab === 'rag' && (
          <HerbRecommendationView 
            result={recommendationResult.rag} 
            type="RAG" 
            color="primary"
            favorites={favorites}
            onToggleFavorite={toggleFavorite}
          />
        )}
        
        {activeTab === 'agentic' && (
          <HerbRecommendationView 
            result={recommendationResult.agentic} 
            type="Agentic" 
            color="secondary"
            favorites={favorites}
            onToggleFavorite={toggleFavorite}
          />
        )}
        
        {activeTab === 'favorites' && (
          <FavoriteHerbsView 
            favorites={favorites}
            onToggleFavorite={toggleFavorite}
          />
        )}
      </Box>
    );
  };

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Herb Recommender
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Compare herb recommendations from RAG and Agentic approaches for various conditions
        </Typography>
      </Box>

      <Paper component="form" onSubmit={handleSubmit} sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              What condition or symptoms would you like herb recommendations for?
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={2}
              variant="outlined"
              placeholder="Example: I need herbs for stress relief and better sleep"
              value={query}
              onChange={handleInputChange}
              disabled={isLoading}
            />
          </Grid>
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Tooltip title="Clear form">
                  <Button 
                    onClick={() => setQuery('')} 
                    disabled={isLoading || !query}
                    color="inherit"
                  >
                    Clear
                  </Button>
                </Tooltip>
              </Box>
              <Box>
                <Tooltip title="Refresh recommendations">
                  <span>
                    <IconButton 
                      onClick={handleRefresh}
                      disabled={isLoading || !recommendationResult}
                      color="primary"
                      sx={{ mr: 1 }}
                    >
                      <RefreshIcon />
                    </IconButton>
                  </span>
                </Tooltip>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={isLoading || !query.trim()}
                  startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : null}
                >
                  {isLoading ? 'Searching...' : 'Get Recommendations'}
                </Button>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {renderResult()}

      <Box mt={6}>
        <Typography variant="h6" gutterBottom>
          About Herb Recommendations
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          This tool compares how different AI approaches recommend herbs for various conditions:
        </Typography>
        
        <Accordion 
          expanded={expanded === 'panel1'} 
          onChange={handleAccordionChange('panel1')}
          elevation={0}
          sx={{ bgcolor: 'transparent' }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>RAG (Retrieval-Augmented Generation) Approach</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary" paragraph>
              The RAG approach retrieves herb recommendations based on matching keywords and 
              pre-defined associations in the knowledge base. It's fast and provides consistent 
              results based on established herbal knowledge.
            </Typography>
            <Box component="ul" pl={2} mb={2}>
              <li><strong>Strengths:</strong> Quick responses, consistent with traditional knowledge</li>
              <li><strong>Limitations:</strong> May miss nuanced or personalized recommendations</li>
            </Box>
          </AccordionDetails>
        </Accordion>
        
        <Accordion 
          expanded={expanded === 'panel2'} 
          onChange={handleAccordionChange('panel2')}
          elevation={0}
          sx={{ bgcolor: 'transparent' }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Agentic Approach</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary" paragraph>
              The Agentic approach uses more advanced reasoning to understand the context of 
              your request and may provide more personalized herb recommendations. It can 
              consider multiple factors and suggest herb combinations.
            </Typography>
            <Box component="ul" pl={2} mb={2}>
              <li><strong>Strengths:</strong> More personalized, can suggest combinations, considers contraindications</li>
              <li><strong>Limitations:</strong> May take slightly longer, more resource-intensive</li>
            </Box>
          </AccordionDetails>
        </Accordion>

        <Box mt={3} p={2} bgcolor="info.light" borderRadius={1}>
          <Box display="flex" alignItems="center" mb={1}>
            <InfoIcon color="info" sx={{ mr: 1 }} />
            <Typography variant="subtitle2">Important Note</Typography>
          </Box>
          <Typography variant="body2">
            The information provided by this tool is for educational purposes only and is not 
            intended as medical advice. Always consult with a qualified healthcare provider 
            before starting any herbal treatment, especially if you are pregnant, nursing, 
            taking medications, or have a medical condition.
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default HerbRecommender;
