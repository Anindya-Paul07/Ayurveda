import { useState, useEffect } from 'react';
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
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  CompareArrows as CompareArrowsIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import api from '../../services/api';

const DoshaComparison = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();
  
  const [input, setInput] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [isComparing, setIsComparing] = useState(false);

  // Fetch comparison results
  const { data: comparisonData, isLoading, error } = useQuery({
    queryKey: ['doshaComparison'],
    queryFn: () => api.compareDoshaAnalysis(input, 'rag', 'agentic'),
    enabled: false, // Disable automatic fetch
  });

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
      enqueueSnackbar('Please enter symptoms or a question', { variant: 'warning' });
      return;
    }
    
    try {
      setIsComparing(true);
      const result = await queryClient.fetchQuery({
        queryKey: ['doshaComparison', input],
        queryFn: () => api.compareDoshaAnalysis(input, 'rag', 'agentic'),
      });
      setComparisonResult(result);
      setActiveTab(0);
    } catch (err) {
      enqueueSnackbar('Error comparing dosha analysis', { variant: 'error' });
      console.error('Error:', err);
    } finally {
      setIsComparing(false);
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    if (input) {
      handleSubmit({ preventDefault: () => {} });
    }
  };

  // Render result section
  const renderResult = () => {
    if (isComparing) {
      return (
        <Box display="flex" justifyContent="center" my={8}>
          <CircularProgress />
        </Box>
      );
    }

    if (!comparisonResult) {
      return (
        <Box textAlign="center" my={8}>
          <PsychologyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Enter symptoms or a question to compare RAG and Agentic approaches
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
            <ComparisonView 
              ragResult={comparisonResult.rag} 
              agenticResult={comparisonResult.agentic} 
            />
          )}
          {activeTab === 1 && (
            <AnalysisView 
              result={comparisonResult.rag} 
              type="RAG" 
              color="primary"
            />
          )}
          {activeTab === 2 && (
            <AnalysisView 
              result={comparisonResult.agentic} 
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
          Dosha Analysis Comparison
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Compare the results of RAG and Agentic approaches for dosha analysis
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
              label="Describe your symptoms or ask a question"
              value={input}
              onChange={handleInputChange}
              disabled={isComparing}
              helperText="Example: I often feel anxious, have dry skin, and experience constipation"
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Box display="flex" justifyContent={isMobile ? 'space-between' : 'flex-end'}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={isComparing || !input.trim()}
                fullWidth={isMobile}
                sx={{ mr: isMobile ? 1 : 0 }}
              >
                {isComparing ? 'Analyzing...' : 'Analyze'}
              </Button>
              <Tooltip title="Refresh">
                <IconButton 
                  onClick={handleRefresh}
                  disabled={isComparing || !comparisonResult}
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
          How does this comparison work?
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          This tool compares two different approaches to Ayurvedic dosha analysis:
        </Typography>
        <ul style={{ paddingLeft: 20, color: theme.palette.text.secondary }}>
          <li>
            <strong>RAG (Retrieval-Augmented Generation):</strong> Uses pre-computed knowledge from the database
            to provide quick responses based on existing information.
          </li>
          <li>
            <strong>Agentic:</strong> Uses a more advanced approach that can reason about symptoms and provide
            more personalized and contextual responses by understanding the relationships between different factors.
          </li>
        </ul>
      </Box>
    </Box>
  );
};

const ComparisonView = ({ ragResult, agenticResult }) => {
  const theme = useTheme();
  
  const renderDoshaComparison = () => {
    const ragDosha = ragResult?.dosha || {};
    const agenticDosha = agenticResult?.dosha || {};
    
    const doshas = ['vata', 'pitta', 'kapha'];
    
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Dosha Analysis Comparison
        </Typography>
        <Grid container spacing={2}>
          {doshas.map((dosha) => (
            <Grid item xs={12} key={dosha}>
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="subtitle2" textTransform="capitalize">
                    {dosha}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {ragDosha[dosha]}% vs {agenticDosha[dosha]}%
                  </Typography>
                </Box>
                <Box display="flex" width="100%" height={8} borderRadius={4} overflow="hidden">
                  <Box 
                    width={`${ragDosha[dosha] || 0}%`} 
                    bgcolor={`${theme.palette.primary.main}80`}
                    position="relative"
                  >
                    <Box 
                      position="absolute" 
                      right={0} 
                      top={0} 
                      bottom={0} 
                      width="2px" 
                      bgcolor="common.white"
                    />
                  </Box>
                  <Box 
                    width={`${agenticDosha[dosha] || 0}%`} 
                    bgcolor={`${theme.palette.secondary.main}80`}
                  />
                </Box>
              </Box>
            </Grid>
          ))}
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
                <Typography variant="body2" color="text.secondary">
                  {ragResult?.recommendations || 'No recommendations available'}
                </Typography>
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
                <Typography variant="body2" color="text.secondary">
                  {agenticResult?.recommendations || 'No recommendations available'}
                </Typography>
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
          <Typography variant="h6">Comparison Summary</Typography>
        </Box>
        <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
          <Typography variant="body2">
            {ragResult?.summary || 'No comparison summary available'}
          </Typography>
        </Paper>
      </Box>

      {renderDoshaComparison()}
      {renderRecommendationComparison()}

      <Box mt={4} p={2} bgcolor="action.hover" borderRadius={1}>
        <Box display="flex" alignItems="center" mb={1}>
          <InfoIcon color="info" sx={{ mr: 1 }} />
          <Typography variant="subtitle2">Key Differences</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          The Agentic approach may provide more personalized recommendations by considering
          the context and relationships between different symptoms and factors, while the
          RAG approach provides more standardized information based on existing knowledge.
        </Typography>
      </Box>
    </Box>
  );
};

const AnalysisView = ({ result, type, color }) => {
  const theme = useTheme();
  
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

      {result.dosha && (
        <Box mb={4}>
          <Typography variant="h6" gutterBottom>
            Dosha Assessment
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(result.dosha).map(([dosha, value]) => (
              <Grid item xs={12} sm={4} key={dosha}>
                <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="subtitle2" textTransform="capitalize">
                      {dosha}
                    </Typography>
                    <Chip 
                      label={`${value}%`} 
                      size="small" 
                      color={color} 
                      variant="outlined"
                    />
                  </Box>
                  <Box mt={1} width="100%" height={8} bgcolor="action.hover" borderRadius={4} overflow="hidden">
                    <Box 
                      width={`${value}%`} 
                      height="100%" 
                      bgcolor={`${theme.palette[color].main}80`}
                    />
                  </Box>
                </Paper>
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
          <Paper variant="outlined" sx={{ p: 2 }}>
            <Typography variant="body2" whiteSpace="pre-line">
              {result.recommendations}
            </Typography>
          </Paper>
        </Box>
      )}
    </Box>
  );
};

export default DoshaComparison;
