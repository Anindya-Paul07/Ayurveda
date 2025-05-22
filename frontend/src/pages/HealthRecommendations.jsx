import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Divider, 
  Chip, 
  CircularProgress, 
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  useTheme,
  Collapse,
  IconButton
} from '@mui/material';
import { 
  ExpandMore as ExpandMoreIcon,
  Restaurant as FoodIcon,
  SelfImprovement as YogaIcon,
  Spa as HerbIcon,
  WbSunny as WeatherIcon,
  LocalHospital as HealthIcon,
  EmojiPeople as DoshaIcon,
  Chat as ChatIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { format } from 'date-fns';
import api from '../services/api';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s, box-shadow 0.2s',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
  },
}));

const RecommendationCard = ({ title, icon, description, action, onAction, expanded, onToggle }) => {
  const theme = useTheme();
  
  return (
    <StyledCard>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar sx={{ bgcolor: theme.palette.primary.light, mr: 2 }}>
            {icon}
          </Avatar>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          <IconButton
            onClick={onToggle}
            aria-expanded={expanded}
            aria-label="show more"
            sx={{ ml: 'auto' }}
          >
            <ExpandMoreIcon />
          </IconButton>
        </Box>
        
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Typography variant="body2" color="text.secondary" paragraph>
            {description}
          </Typography>
          {action && (
            <Button 
              variant="outlined" 
              size="small" 
              onClick={onAction}
              sx={{ mt: 1 }}
            >
              {action}
            </Button>
          )}
        </Collapse>
      </CardContent>
    </StyledCard>
  );
};

const HealthRecommendations = ({ userData }) => {
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [expanded, setExpanded] = useState({});
  const theme = useTheme();

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API call
        // const response = await api.get('/api/recommendations', {
        //   params: { userId: userData?.id }
        // });
        
        // Mock data for now
        setTimeout(() => {
          setRecommendations([
            {
              id: 'diet',
              title: 'Personalized Diet Plan',
              icon: <FoodIcon />,
              description: 'Based on your Vata-Pitta dosha, we recommend warm, cooked foods with mild spices. Include more sweet fruits and dairy to balance your constitution.',
              action: 'View Full Plan'
            },
            {
              id: 'yoga',
              title: 'Yoga & Exercise',
              icon: <YogaIcon />,
              description: 'Gentle yoga asanas like Surya Namaskar and Pranayama will help balance your energy levels. Recommended duration: 30 minutes daily.',
              action: 'View Routine'
            },
            {
              id: 'herbs',
              title: 'Herbal Supplements',
              icon: <HerbIcon />,
              description: 'Consider taking Ashwagandha in the morning and Brahmi at night to support your nervous system and improve sleep quality.',
              action: 'Learn More'
            },
            {
              id: 'lifestyle',
              title: 'Daily Routine',
              icon: <WeatherIcon />,
              description: 'Maintain a regular sleep schedule. Oil massage (Abhyanga) with warm sesame oil before shower will be beneficial.',
              action: 'View Schedule'
            }
          ]);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [userData]);

  const handleToggle = (id) => {
    setExpanded(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleAction = (id) => {
    // Handle action based on recommendation type
    console.log('Action triggered for:', id);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ open: false, severity: 'success', message: '' });
  };

  const getIcon = (type) => {
    switch (type) {
      case 'diet':
        return <FoodIcon />;
      case 'yoga':
        return <YogaIcon />;
      case 'herbs':
        return <HerbIcon />;
      case 'lifestyle':
        return <WeatherIcon />;
      default:
        return <HealthIcon />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Your Personalized Health Recommendations
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" paragraph>
          Tailored suggestions based on your dosha, health profile, and preferences
        </Typography>
        
        {recommendations.length === 0 ? (
          <Paper elevation={0} sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No recommendations available
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
              Complete your health profile and dosha test to receive personalized recommendations.
            </Typography>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={() => navigate('/dosha-test')}
              startIcon={<DoshaIcon />}
              sx={{ mt: 2 }}
            >
              Take Dosha Test
            </Button>
          </Paper>
        ) : (
          <Grid container spacing={3} sx={{ mt: 2 }}>
            {recommendations.map((rec) => (
              <Grid item xs={12} sm={6} md={4} key={rec.id}>
                <RecommendationCard 
                  title={rec.title}
                  icon={getIcon(rec.type)}
                  description={rec.description}
                  action={rec.ctaText}
                  onAction={() => handleAction(rec.actionType, rec.id)}
                  expanded={!!expanded[rec.id]}
                  onToggle={() => handleToggleExpand(rec.id)}
                />
              </Grid>
            ))}
          </Grid>
        )}

        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleCloseSnackbar} 
            severity={snackbar.severity}
            sx={{ width: '100%' }}
            iconMapping={{
              error: <ErrorIcon fontSize="inherit" />,
              success: <CheckCircleIcon fontSize="inherit" />,
            }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          Your Health Summary
        </Typography>
        <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
          {/* TODO: Add dynamic health summary based on user data */}
          <Typography paragraph>
            Based on your recent interactions and dosha analysis, you have a Vata-Pitta constitution. 
            Your current health metrics indicate good balance, with some signs of stress and digestive sensitivity.
          </Typography>
          <Button variant="contained" color="primary" startIcon={<ChatIcon />}>
            Chat with Health Advisor
          </Button>
        </Paper>
      </Box>
    </Box>
  );
};

export default HealthRecommendations;
