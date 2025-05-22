import { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  TextField,
  Button,
  Divider,
  Tabs,
  Tab,
  CircularProgress,
  useTheme,
  useMediaQuery,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Tooltip,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  CompareArrows as CompareArrowsIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  LocalHospital as HospitalIcon,
  Healing as HealingIcon,
  Restaurant as FoodIcon,
  SelfImprovement as YogaIcon,
  Spa as TreatmentIcon,
} from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import api from '../../services/api';

const DiseasePredictor = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();
  
  const [input, setInput] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [predictionResult, setPredictionResult] = useState(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [expandedDisease, setExpandedDisease] = useState(null);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Handle input change
  const handleInputChange = (event) => {
    setInput(event.target.value);
  };

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!input.trim()) {
      enqueueSnackbar('Please describe your symptoms', { variant: 'warning' });
      return;
    }
    
    try {
      setIsPredicting(true);
      const result = await queryClient.fetchQuery({
        queryKey: ['diseasePrediction', input],
        queryFn: () => api.post('/predict/disease', { symptoms: input }),
      });
      setPredictionResult(result);
      setActiveTab(0);
    } catch (err) {
      enqueueSnackbar('Error predicting disease', { variant: 'error' });
      console.error('Error:', err);
    } finally {
      setIsPredicting(false);
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    if (input) {
      handleSubmit({ preventDefault: () => {} });
    }
  };

  // Handle accordion expand/collapse
  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedDisease(isExpanded ? panel : null);
  };

  // Render result section
  const renderResult = () => {
    if (isPredicting) {
      return (
        <Box display="flex" justifyContent="center" my={8}>
          <CircularProgress />
        </Box>
      );
    }

    if (!predictionResult) {
      return (
        <Box textAlign="center" my={8}>
          <PsychologyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Describe your symptoms to predict potential Ayurvedic conditions
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
          <Tab label="Predictions" icon={<PsychologyIcon />} />
          <Tab label="Analysis" />
        </Tabs>

        <Paper sx={{ p: 3, mb: 4 }}>
          {activeTab === 0 && (
            <PredictionView 
              predictions={predictionResult.predictions} 
              onExpand={handleAccordionChange}
              expandedDisease={expandedDisease}
            />
          )}
          {activeTab === 1 && (
            <AnalysisView analysis={predictionResult.analysis} />
          )}
        </Paper>
      </Box>
    );
  };

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Disease Predictor
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Predict potential Ayurvedic conditions based on your symptoms
        </Typography>
      </Box>

      <Paper component="form" onSubmit={handleSubmit} sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12} md={10}>
            <TextField
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              label="Describe your symptoms"
              value={input}
              onChange={handleInputChange}
              disabled={isPredicting}
              helperText="Example: I have been experiencing fatigue, bloating, and irregular digestion"
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Box display="flex" justifyContent={isMobile ? 'space-between' : 'flex-end'}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={isPredicting || !input.trim()}
                fullWidth={isMobile}
                sx={{ mr: isMobile ? 1 : 0 }}
              >
                {isPredicting ? 'Analyzing...' : 'Analyze'}
              </Button>
              <Tooltip title="Refresh">
                <IconButton 
                  onClick={handleRefresh}
                  disabled={isPredicting || !predictionResult}
                  color="primary"
                  sx={{ ml: isMobile ? 1 : 2 }}
                >
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {renderResult()}

      <Box mt={6}>
        <Typography variant="h6" gutterBottom>
          How does disease prediction work?
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          This tool uses advanced AI to analyze your symptoms and predict potential
          Ayurvedic conditions based on traditional knowledge and modern data analysis.
        </Typography>
        <List dense>
          <ListItem>
            <ListItemIcon><InfoIcon color="info" /></ListItemIcon>
            <ListItemText 
              primary="Symptom Analysis" 
              secondary="Your symptoms are analyzed in the context of Ayurvedic principles" 
            />
          </ListItem>
          <ListItem>
            <ListItemIcon><HospitalIcon color="primary" /></ListItemIcon>
            <ListItemText 
              primary="Disease Matching" 
              secondary="Potential conditions are identified based on symptom patterns" 
            />
          </ListItem>
          <ListItem>
            <ListItemIcon><HealingIcon color="secondary" /></ListItemIcon>
            <ListItemText 
              primary="Personalized Insights" 
              secondary="Get tailored recommendations based on predicted conditions" 
            />
          </ListItem>
        </List>
      </Box>
    </Box>
  );
};

const PredictionView = ({ predictions, onExpand, expandedDisease }) => {
  if (!predictions || predictions.length === 0) {
    return (
      <Typography color="text.secondary">
        No disease predictions available. Please try with more specific symptoms.
      </Typography>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Possible Conditions
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Based on your symptoms, you might be experiencing one of these conditions:
      </Typography>
      
      {predictions.map((disease, index) => (
        <Accordion 
          key={index} 
          expanded={expandedDisease === `disease-${index}`}
          onChange={onExpand(`disease-${index}`)}
          elevation={2}
          sx={{ mb: 2 }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls={`disease-${index}-content`}
            id={`disease-${index}-header`}
          >
            <Box width="100%" display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="subtitle1">
                {disease.name} 
                <Chip 
                  label={`${(disease.probability * 100).toFixed(1)}%`} 
                  size="small" 
                  color={disease.severity === 'high' ? 'error' : disease.severity === 'medium' ? 'warning' : 'primary'}
                  sx={{ ml: 1 }}
                />
              </Typography>
              <Chip 
                label={disease.dosha.join(', ')} 
                size="small" 
                variant="outlined"
                sx={{ textTransform: 'capitalize' }}
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Description:
              </Typography>
              <Typography variant="body2" paragraph>
                {disease.description}
              </Typography>
              
              {disease.treatments && (
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Recommended Treatments:
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Card variant="outlined">
                        <CardHeader 
                          avatar={<HealingIcon color="primary" />}
                          title="Herbal Remedies"
                          titleTypographyProps={{ variant: 'subtitle2' }}
                        />
                        <CardContent>
                          <List dense>
                            {disease.treatments.herbs.map((herb, i) => (
                              <ListItem key={i}>
                                <ListItemText 
                                  primary={herb.name} 
                                  secondary={herb.usage} 
                                />
                              </ListItem>
                            ))}
                          </List>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Card variant="outlined">
                        <CardHeader 
                          avatar={<RestaurantIcon color="secondary" />}
                          title="Dietary Recommendations"
                          titleTypographyProps={{ variant: 'subtitle2' }}
                        />
                        <CardContent>
                          <List dense>
                            <ListItem>
                              <ListItemText 
                                primary="Favor" 
                                secondary={disease.treatments.diet.favor.join(', ')} 
                              />
                            </ListItem>
                            <ListItem>
                              <ListItemText 
                                primary="Avoid" 
                                secondary={disease.treatments.diet.avoid.join(', ')} 
                              />
                            </ListItem>
                          </List>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={12}>
                      <Card variant="outlined">
                        <CardHeader 
                          avatar={<YogaIcon color="action" />}
                          title="Lifestyle Changes"
                          titleTypographyProps={{ variant: 'subtitle2' }}
                        />
                        <CardContent>
                          <List dense>
                            {disease.treatments.lifestyle.map((item, i) => (
                              <ListItem key={i}>
                                <ListItemText primary={item} />
                              </ListItem>
                            ))}
                          </List>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
              )}
              
              {disease.when_to_see_doctor && (
                <Box mt={2} p={2} bgcolor="error.light" borderRadius={1}>
                  <Typography variant="subtitle2" color="error.contrastText">
                    When to see a doctor:
                  </Typography>
                  <Typography variant="body2" color="error.contrastText">
                    {disease.when_to_see_doctor}
                  </Typography>
                </Box>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

const AnalysisView = ({ analysis }) => {
  if (!analysis) {
    return (
      <Typography color="text.secondary">
        No analysis available. Please submit symptoms to see the analysis.
      </Typography>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Symptom Analysis
      </Typography>
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography variant="body2" whiteSpace="pre-line">
          {analysis}
        </Typography>
      </Paper>
      
      <Box mt={4} p={2} bgcolor="action.hover" borderRadius={1}>
        <Box display="flex" alignItems="center" mb={1}>
          <InfoIcon color="info" sx={{ mr: 1 }} />
          <Typography variant="subtitle2">Important Note</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          This tool is for informational purposes only and is not a substitute for professional medical advice, 
          diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider 
          with any questions you may have regarding a medical condition.
        </Typography>
      </Box>
    </Box>
  );
};

export default DiseasePredictor;
