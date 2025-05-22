import { useState } from 'react';
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
  Chip,
  useTheme,
  useMediaQuery,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  LocalHospital as LocalHospitalIcon,
  CompareArrows as CompareArrowsIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import api from '../../services/api';

const SymptomAnalyzer = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();
  
  const [symptoms, setSymptoms] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [expanded, setExpanded] = useState('panel1');

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
    setSymptoms(event.target.value);
  };

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!symptoms.trim()) {
      enqueueSnackbar('Please describe your symptoms', { variant: 'warning' });
      return;
    }
    
    try {
      setIsAnalyzing(true);
      const result = await queryClient.fetchQuery({
        queryKey: ['symptomAnalysis', symptoms],
        queryFn: () => api.analyzeSymptoms(symptoms, 'rag', 'agentic'),
      });
      setAnalysisResult(result);
      setActiveTab(0);
    } catch (err) {
      enqueueSnackbar('Error analyzing symptoms', { variant: 'error' });
      console.error('Error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    if (symptoms) {
      handleSubmit({ preventDefault: () => {} });
    }
  };

  // Render result section
  const renderResult = () => {
    if (isAnalyzing) {
      return (
        <Box display="flex" justifyContent="center" my={8}>
          <CircularProgress />
        </Box>
      );
    }

    if (!analysisResult) {
      return (
        <Box textAlign="center" my={8}>
          <LocalHospitalIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Describe your symptoms to compare RAG and Agentic analysis
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
          <Tab label="Comparison" icon={<CompareArrowsIcon />} />
          <Tab label="RAG Analysis" />
          <Tab label="Agentic Analysis" />
        </Tabs>

        <Paper sx={{ p: 3, mb: 4 }}>
          {activeTab === 0 && (
            <SymptomComparisonView 
              ragResult={analysisResult.rag} 
              agenticResult={analysisResult.agentic} 
            />
          )}
          {activeTab === 1 && (
            <SymptomAnalysisView 
              result={analysisResult.rag} 
              type="RAG" 
              color="primary"
            />
          )}
          {activeTab === 2 && (
            <SymptomAnalysisView 
              result={analysisResult.agentic} 
              type="Agentic" 
              color="secondary"
            />
          )}
        </Paper>
      </Box>
    );
  };

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Symptom Analyzer
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Compare how RAG and Agentic approaches analyze and interpret symptoms
        </Typography>
      </Box>

      <Paper component="form" onSubmit={handleSubmit} sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Describe your symptoms in detail:
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              placeholder="Example: I've been experiencing headaches, fatigue, and digestive issues for the past week. I also feel more anxious than usual."
              value={symptoms}
              onChange={handleInputChange}
              disabled={isAnalyzing}
            />
          </Grid>
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Tooltip title="Clear form">
                  <Button 
                    onClick={() => setSymptoms('')} 
                    disabled={isAnalyzing || !symptoms}
                    color="inherit"
                  >
                    Clear
                  </Button>
                </Tooltip>
              </Box>
              <Box>
                <Tooltip title="Refresh analysis">
                  <span>
                    <IconButton 
                      onClick={handleRefresh}
                      disabled={isAnalyzing || !analysisResult}
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
                  disabled={isAnalyzing || !symptoms.trim()}
                  startIcon={isAnalyzing ? <CircularProgress size={20} color="inherit" /> : null}
                >
                  {isAnalyzing ? 'Analyzing...' : 'Analyze Symptoms'}
                </Button>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {renderResult()}

      <Box mt={6}>
        <Typography variant="h6" gutterBottom>
          Understanding the Analysis
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          This tool compares how different AI approaches analyze and interpret symptoms:
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
              The RAG approach retrieves relevant information from a knowledge base and generates 
              responses based on that information. It's fast and provides consistent results based 
              on existing knowledge.
            </Typography>
            <Box component="ul" pl={2} mb={2}>
              <li><strong>Strengths:</strong> Quick responses, consistent with established knowledge</li>
              <li><strong>Limitations:</strong> May miss nuanced or complex symptom relationships</li>
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
              The Agentic approach uses more advanced reasoning to understand the context and 
              relationships between symptoms. It can provide more personalized and nuanced 
              interpretations.
            </Typography>
            <Box component="ul" pl={2} mb={2}>
              <li><strong>Strengths:</strong> Better at understanding complex symptom relationships, more personalized</li>
              <li><strong>Limitations:</strong> May take slightly longer, more resource-intensive</li>
            </Box>
          </AccordionDetails>
        </Accordion>
      </Box>
    </Box>
  );
};

const SymptomComparisonView = ({ ragResult, agenticResult }) => {
  const theme = useTheme();
  
  const renderSymptomComparison = () => {
    const ragSymptoms = ragResult?.symptoms || [];
    const agenticSymptoms = agenticResult?.symptoms || [];
    
    const allSymptoms = [...new Set([...ragSymptoms, ...agenticSymptoms])];
    
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Identified Symptoms
        </Typography>
        <Box display="flex" flexWrap="wrap" gap={1} mb={3}>
          {allSymptoms.map((symptom) => {
            const ragHas = ragSymptoms.includes(symptom);
            const agenticHas = agenticSymptoms.includes(symptom);
            
            let chipColor = 'default';
            let chipVariant = 'outlined';
            
            if (ragHas && agenticHas) {
              chipColor = 'success';
            } else if (ragHas) {
              chipColor = 'primary';
              chipVariant = 'filled';
            } else if (agenticHas) {
              chipColor = 'secondary';
              chipVariant = 'filled';
            }
            
            return (
              <Chip 
                key={symptom}
                label={symptom}
                color={chipColor}
                variant={chipVariant}
                size="small"
                sx={{ textTransform: 'capitalize' }}
              />
            );
          })}
        </Box>
      </Box>
    );
  };

  const renderConditionComparison = () => {
    const ragConditions = ragResult?.possible_conditions || [];
    const agenticConditions = agenticResult?.possible_conditions || [];
    
    const allConditions = [...new Set([...ragConditions, ...agenticConditions])];
    
    return (
      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          Possible Conditions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardHeader 
                title="RAG Analysis" 
                titleTypographyProps={{ color: 'primary.main' }}
                subheader={`${ragConditions.length} conditions identified`}
              />
              <CardContent>
                {ragConditions.length > 0 ? (
                  <List dense>
                    {ragConditions.map((condition, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <CheckCircleIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={condition.name} 
                          secondary={`Confidence: ${Math.round(condition.confidence * 100)}%`}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No conditions identified
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardHeader 
                title="Agentic Analysis" 
                titleTypographyProps={{ color: 'secondary.main' }}
                subheader={`${agenticConditions.length} conditions identified`}
              />
              <CardContent>
                {agenticConditions.length > 0 ? (
                  <List dense>
                    {agenticConditions.map((condition, index) => {
                      const ragHas = ragConditions.some(c => c.name === condition.name);
                      return (
                        <ListItem key={index}>
                          <ListItemIcon>
                            {ragHas ? 
                              <CheckCircleIcon color="success" /> : 
                              <WarningIcon color="secondary" />
                            }
                          </ListItemIcon>
                          <ListItemText 
                            primary={
                              <Box display="flex" alignItems="center">
                                {condition.name}
                                {!ragHas && (
                                  <Chip 
                                    label="New" 
                                    size="small" 
                                    color="secondary" 
                                    sx={{ ml: 1 }}
                                  />
                                )}
                              </Box>
                            }
                            secondary={`Confidence: ${Math.round(condition.confidence * 100)}% ${ragHas ? '' : '(Not in RAG)'}`}
                          />
                        </ListItem>
                      );
                    })}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No conditions identified
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderRecommendationComparison = () => {
    return (
      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          Recommendations Comparison
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardHeader 
                title="RAG Recommendations" 
                titleTypographyProps={{ color: 'primary.main' }}
              />
              <CardContent>
                {ragResult?.recommendations ? (
                  <Box>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {ragResult.recommendations.summary}
                    </Typography>
                    {ragResult.recommendations.actions && (
                      <Box mt={2}>
                        <Typography variant="subtitle2" gutterBottom>
                          Suggested Actions:
                        </Typography>
                        <List dense>
                          {ragResult.recommendations.actions.map((action, i) => (
                            <ListItem key={i}>
                              <ListItemIcon>
                                <CheckCircleIcon color="primary" fontSize="small" />
                              </ListItemIcon>
                              <ListItemText primary={action} />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No recommendations available
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardHeader 
                title="Agentic Recommendations" 
                titleTypographyProps={{ color: 'secondary.main' }}
              />
              <CardContent>
                {agenticResult?.recommendations ? (
                  <Box>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {agenticResult.recommendations.summary}
                    </Typography>
                    {agenticResult.recommendations.actions && (
                      <Box mt={2}>
                        <Typography variant="subtitle2" gutterBottom>
                          Suggested Actions:
                        </Typography>
                        <List dense>
                          {agenticResult.recommendations.actions.map((action, i) => {
                            const ragHas = ragResult?.recommendations?.actions?.includes(action);
                            return (
                              <ListItem key={i}>
                                <ListItemIcon>
                                  {ragHas ? 
                                    <CheckCircleIcon color="primary" fontSize="small" /> : 
                                    <WarningIcon color="secondary" fontSize="small" />
                                  }
                                </ListItemIcon>
                                <ListItemText 
                                  primary={
                                    <Box display="flex" alignItems="center">
                                      {action}
                                      {!ragHas && (
                                        <Chip 
                                          label="New" 
                                          size="small" 
                                          color="secondary" 
                                          sx={{ ml: 1, height: 20 }}
                                        />
                                      )}
                                    </Box>
                                  }
                                />
                              </ListItem>
                            );
                          })}
                        </List>
                      </Box>
                    )}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No recommendations available
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  return (
    <Box>
      <Box mb={4}>
        <Box display="flex" alignItems="center" mb={2}>
          <CompareArrowsIcon color="action" sx={{ mr: 1 }} />
          <Typography variant="h6">Analysis Comparison</Typography>
        </Box>
        <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
          <Typography variant="body2">
            {ragResult?.summary || 'No comparison summary available'}
          </Typography>
        </Paper>
      </Box>

      {renderSymptomComparison()}
      {renderConditionComparison()}
      {renderRecommendationComparison()}

      <Box mt={4} p={2} bgcolor="action.hover" borderRadius={1}>
        <Box display="flex" alignItems="center" mb={1}>
          <InfoIcon color="info" sx={{ mr: 1 }} />
          <Typography variant="subtitle2">Key Differences</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          The Agentic approach may identify additional conditions and provide more 
          personalized recommendations by considering the context and relationships 
          between different symptoms, while the RAG approach provides more standardized 
          information based on existing knowledge.
        </Typography>
      </Box>
    </Box>
  );
};

const SymptomAnalysisView = ({ result, type, color }) => {
  if (!result) {
    return (
      <Box textAlign="center" py={4}>
        <Typography color="text.secondary">
          No {type.toLowerCase()} analysis available
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box mb={4}>
        <Typography variant="h6" gutterBottom color={`${color}.main`}>
          {type} Analysis
        </Typography>
        <Typography variant="body1" paragraph>
          {result.analysis || 'No analysis available'}
        </Typography>
      </Box>

      {result.symptoms && result.symptoms.length > 0 && (
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Identified Symptoms
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {result.symptoms.map((symptom, index) => (
              <Chip 
                key={index}
                label={symptom}
                color={color}
                variant="outlined"
                size="small"
                sx={{ textTransform: 'capitalize' }}
              />
            ))}
          </Box>
        </Box>
      )}

      {result.possible_conditions && result.possible_conditions.length > 0 && (
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Possible Conditions
          </Typography>
          <Grid container spacing={2}>
            {result.possible_conditions.map((condition, index) => (
              <Grid item xs={12} sm={6} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                      <Typography variant="subtitle1" gutterBottom>
                        {condition.name}
                      </Typography>
                      <Chip 
                        label={`${Math.round(condition.confidence * 100)}%`} 
                        size="small" 
                        color={color}
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {condition.description}
                    </Typography>
                    {condition.symptoms && (
                      <Box mt={1}>
                        <Typography variant="caption" color="text.secondary">
                          Related symptoms: {condition.symptoms.join(', ')}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {result.recommendations && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="body1" paragraph>
                {result.recommendations.summary}
              </Typography>
              
              {result.recommendations.actions && result.recommendations.actions.length > 0 && (
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Suggested Actions:
                  </Typography>
                  <List dense>
                    {result.recommendations.actions.map((action, i) => (
                      <ListItem key={i}>
                        <ListItemIcon>
                          <CheckCircleIcon color={color} fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={action} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
              
              {result.recommendations.when_to_seek_help && (
                <Box mt={3} p={2} bgcolor="warning.light" borderRadius={1}>
                  <Box display="flex" alignItems="center" mb={1}>
                    <WarningIcon color="warning" sx={{ mr: 1 }} />
                    <Typography variant="subtitle2">
                      When to Seek Medical Help
                    </Typography>
                  </Box>
                  <Typography variant="body2">
                    {result.recommendations.when_to_seek_help}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default SymptomAnalyzer;
