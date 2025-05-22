import { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  Stepper, 
  Step, 
  StepLabel, 
  Button, 
  Radio, 
  RadioGroup, 
  FormControlLabel, 
  FormControl, 
  FormLabel, 
  Card, 
  CardContent, 
  CircularProgress,
  Divider,
  useTheme,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Chip
} from '@mui/material';
import { 
  Spa as SpaIcon, 
  Check as CheckIcon, 
  EmojiNature as VataIcon,
  Whatshot as PittaIcon,
  AcUnit as KaphaIcon,
  Favorite as HeartIcon,
  Restaurant as FoodIcon,
  SelfImprovement as YogaIcon,
  WbSunny as SunIcon,
  Nightlight as MoonIcon,
  LocalFlorist as HerbIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  borderRadius: theme.shape.borderRadius * 2,
  boxShadow: theme.shadows[3],
  height: '100%',
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: theme.shadows[6],
  },
}));

const DoshaCard = styled(Card)(({ theme, dosha }) => ({
  height: '100%',
  border: `2px solid ${
    dosha === 'vata' ? theme.palette.primary.main :
    dosha === 'pitta' ? theme.palette.warning.main :
    theme.palette.info.main
  }`,
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: theme.shadows[8],
  },
  transition: 'all 0.3s ease',
}));

const questions = [
  {
    id: 'body_frame',
    question: 'Which best describes your body frame?',
    options: [
      { value: 'thin', label: 'Thin, light build, difficulty gaining weight' },
      { value: 'medium', label: 'Medium, well-proportioned build' },
      { value: 'large', label: 'Large, solid, heavy build' }
    ]
  },
  {
    id: 'skin_type',
    question: 'How would you describe your skin type?',
    options: [
      { value: 'dry', label: 'Dry, rough, or flaky skin' },
      { value: 'sensitive', label: 'Sensitive, prone to rashes or inflammation' },
      { value: 'oily', label: 'Oily, smooth, or moist skin' }
    ]
  },
  {
    id: 'appetite',
    question: 'How would you describe your appetite?',
    options: [
      { value: 'variable', label: 'Variable, sometimes hungry, sometimes not' },
      { value: 'strong', label: 'Strong, get hungry if I miss a meal' },
      { value: 'steady', label: 'Steady, can easily skip meals' }
    ]
  },
  {
    id: 'energy',
    question: 'How is your energy level throughout the day?',
    options: [
      { value: 'variable', label: 'Variable, with bursts of energy' },
      { value: 'intense', label: 'Intense, high energy' },
      { value: 'steady', label: 'Steady, consistent energy' }
    ]
  },
  {
    id: 'sleep',
    question: 'How would you describe your sleep?',
    options: [
      { value: 'light', label: 'Light, easily disturbed' },
      { value: 'moderate', label: 'Moderate, but may wake up hot' },
      { value: 'heavy', label: 'Heavy, long, and sound' }
    ]
  }
];

const DoshaAnalysis = () => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const calculateDosha = async () => {
    setIsLoading(true);
    try {
      // In a real app, you would send the answers to your backend
      // const response = await fetch('/api/calculate-dosha', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(answers)
      // });
      // const data = await response.json();
      
      // Mock response for demonstration
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockResult = {
        primaryDosha: 'pitta',
        secondaryDosha: 'vata',
        scores: {
          vata: 35,
          pitta: 55,
          kapha: 10
        },
        analysis: {
          vata: 'You show some Vata characteristics like variability in energy and appetite.',
          pitta: 'Your primary dosha is Pitta, indicating strong digestion, ambition, and a tendency to get warm easily.',
          kapha: 'You have fewer Kapha characteristics, suggesting you may need to work on grounding and consistency.'
        },
        recommendations: [
          'Follow a Pitta-pacifying diet with cooling foods like cucumbers, melons, and mint.',
          'Engage in calming exercises like swimming or moon salutations.',
          'Practice mindfulness and meditation to balance intensity.',
          'Avoid excessive heat, both in environment and spicy foods.'
        ]
      };
      
      setResult(mockResult);
      setActiveStep(questions.length);
    } catch (error) {
      console.error('Error calculating dosha:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderQuestionStep = (step) => {
    const question = questions[step];
    const selectedValue = answers[question.id];

    return (
      <StyledPaper elevation={3}>
        <Typography variant="h5" component="h2" gutterBottom>
          {question.question}
        </Typography>
        <FormControl component="fieldset" sx={{ mt: 3, width: '100%' }}>
          <RadioGroup
            value={selectedValue || ''}
            onChange={(e) => handleAnswer(question.id, e.target.value)}
          >
            {question.options.map((option) => (
              <Paper 
                key={option.value} 
                elevation={selectedValue === option.value ? 3 : 1}
                sx={{
                  p: 2,
                  mb: 2,
                  borderRadius: 1,
                  border: selectedValue === option.value 
                    ? `2px solid ${theme.palette.primary.main}` 
                    : '1px solid rgba(0, 0, 0, 0.12)',
                  '&:hover': {
                    borderColor: theme.palette.primary.light,
                  },
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onClick={() => handleAnswer(question.id, option.value)}
              >
                <FormControlLabel
                  value={option.value}
                  control={<Radio />}
                  label={option.label}
                  sx={{ width: '100%', m: 0 }}
                />
              </Paper>
            ))}
          </RadioGroup>
        </FormControl>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button 
            disabled={step === 0} 
            onClick={handleBack}
            variant="outlined"
          >
            Back
          </Button>
          <Button 
            variant="contained" 
            onClick={handleNext}
            disabled={!selectedValue}
          >
            {step === questions.length - 1 ? 'See Results' : 'Next'}
          </Button>
        </Box>
      </StyledPaper>
    );
  };

  const renderResults = () => {
    if (!result) return null;
    
    const { primaryDosha, secondaryDosha, scores, analysis, recommendations } = result;
    
    const doshaData = [
      { 
        type: 'vata', 
        name: 'Vata', 
        score: scores.vata,
        icon: <VataIcon />,
        color: theme.palette.primary.main,
        element: 'Air + Ether',
        qualities: 'Light, cold, dry, mobile, subtle',
        time: '2-6 AM/PM',
        season: 'Fall/Early Winter'
      },
      { 
        type: 'pitta', 
        name: 'Pitta', 
        score: scores.pitta,
        icon: <PittaIcon />,
        color: theme.palette.warning.main,
        element: 'Fire + Water',
        qualities: 'Hot, sharp, light, oily, liquid',
        time: '10 AM-2 PM, 10 PM-2 AM',
        season: 'Summer'
      },
      { 
        type: 'kapha', 
        name: 'Kapha', 
        score: scores.kapha,
        icon: <KaphaIcon />,
        color: theme.palette.info.main,
        element: 'Earth + Water',
        qualities: 'Heavy, slow, cool, oily, smooth',
        time: '6-10 AM/PM',
        season: 'Late Winter/Spring'
      }
    ];

    return (
      <StyledPaper elevation={3}>
        <Box textAlign="center" mb={4}>
          <Typography variant="h4" component="h1" gutterBottom>
            Your Ayurvedic Constitution
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Based on your responses, your primary dosha is:
          </Typography>
          <Box sx={{ mt: 3, mb: 4 }}>
            <Chip 
              label={primaryDosha.toUpperCase()} 
              color={
                primaryDosha === 'vata' ? 'primary' :
                primaryDosha === 'pitta' ? 'warning' : 'info'
              }
              size="large"
              sx={{ 
                fontSize: '1.2rem',
                px: 3,
                py: 1,
                '& .MuiChip-label': { px: 2 }
              }}
            />
            <Typography variant="body1" sx={{ mt: 2 }}>
              with secondary {secondaryDosha} influence
            </Typography>
          </Box>
        </Box>

        <Grid container spacing={4} sx={{ mb: 4 }}>
          {doshaData.map((dosha) => (
            <Grid item xs={12} md={4} key={dosha.type}>
              <DoshaCard 
                dosha={dosha.type}
                sx={{
                  opacity: dosha.type === primaryDosha || dosha.type === secondaryDosha ? 1 : 0.7,
                  transform: dosha.type === primaryDosha ? 'scale(1.03)' : 'none',
                  zIndex: dosha.type === primaryDosha ? 1 : 0,
                }}
              >
                <CardContent sx={{ textAlign: 'center', p: 3 }}>
                  <Avatar 
                    sx={{ 
                      bgcolor: dosha.color + '20', 
                      color: dosha.color,
                      width: 60, 
                      height: 60,
                      mx: 'auto',
                      mb: 2
                    }}
                  >
                    {React.cloneElement(dosha.icon, { fontSize: 'large' })}
                  </Avatar>
                  <Typography variant="h5" component="h3" gutterBottom>
                    {dosha.name}
                  </Typography>
                  <Box sx={{ 
                    width: '100%', 
                    height: 10, 
                    bgcolor: 'divider', 
                    borderRadius: 5, 
                    mb: 2,
                    overflow: 'hidden'
                  }}>
                    <Box 
                      sx={{
                        width: `${dosha.score}%`,
                        height: '100%',
                        bgcolor: dosha.color,
                      }}
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {dosha.score}% {dosha.type === primaryDosha && '(Primary)'}
                    {dosha.type === secondaryDosha && '(Secondary)'}
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Box textAlign="left" sx={{ '& > *': { mb: 1 } }}>
                    <Typography variant="body2">
                      <strong>Element:</strong> {dosha.element}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Qualities:</strong> {dosha.qualities}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Peak Time:</strong> {dosha.time}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Season:</strong> {dosha.season}
                    </Typography>
                  </Box>
                </CardContent>
              </DoshaCard>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom>Your Analysis</Typography>
          <Paper variant="outlined" sx={{ p: 3, bgcolor: 'background.default' }}>
            <Typography paragraph>{analysis[primaryDosha]}</Typography>
            <Typography paragraph>{analysis[secondaryDosha]}</Typography>
            <Typography>{analysis.kapha}</Typography>
          </Paper>
        </Box>

        <Box>
          <Typography variant="h5" gutterBottom>Personalized Recommendations</Typography>
          <List>
            {recommendations.map((rec, index) => (
              <ListItem key={index} sx={{ alignItems: 'flex-start', mb: 1 }}>
                <ListItemAvatar>
                  <Avatar sx={{ 
                    bgcolor: 'primary.light', 
                    color: 'primary.contrastText',
                    width: 32,
                    height: 32
                  }}>
                    {index % 3 === 0 ? <FoodIcon fontSize="small" /> :
                     index % 3 === 1 ? <YogaIcon fontSize="small" /> : 
                     <HerbIcon fontSize="small" />}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText 
                  primary={rec} 
                  primaryTypographyProps={{ variant: 'body1' }}
                />
              </ListItem>
            ))}
          </List>
        </Box>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<SpaIcon />}
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            Start Over
          </Button>
        </Box>
      </StyledPaper>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
        {[...Array(questions.length + 1)].map((_, index) => (
          <Step key={index}>
            <StepLabel>{index < questions.length ? `Q${index + 1}` : 'Results'}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <Box textAlign="center">
            <CircularProgress size={60} thickness={4} sx={{ mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Analyzing your responses...
            </Typography>
          </Box>
        </Box>
      ) : activeStep < questions.length ? (
        renderQuestionStep(activeStep)
      ) : (
        renderResults()
      )}
    </Container>
  );
};

export default DoshaAnalysis;
