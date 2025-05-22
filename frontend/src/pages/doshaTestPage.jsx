import React, { useState } from 'react';
import { useAyurveda } from '../contexts/AyurvedaContext';
import {
  Container,
  Typography,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Paper,
  Box,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
  Alert,
} from '@mui/material';

const questions = [
  {
    id: 1,
    text: 'What is your body frame like?',
    options: [
      { value: 'vata', label: 'Thin, light, with prominent joints and veins' },
      { value: 'pitta', label: 'Medium build, well-proportioned' },
      { value: 'kapha', label: 'Solid, heavy, with a tendency to gain weight' },
    ],
  },
  {
    id: 2,
    text: 'How is your skin type?',
    options: [
      { value: 'vata', label: 'Dry, rough, thin, cool to touch' },
      { value: 'pitta', label: 'Soft, oily, warm, prone to rashes' },
      { value: 'kapha', label: 'Thick, oily, cool, smooth' },
    ],
  },
  // Add more questions as needed
];

const DoshaTestPage = () => {
  const { loading, error, analyzeDosha } = useAyurveda();
  const [activeStep, setActiveStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);

  const handleAnswer = (questionId, value) => {
    setAnswers({
      ...answers,
      [questionId]: value,
    });
  };

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = async () => {
    try {
      // Convert answers to the format expected by the API
      const responses = Object.entries(answers).map(([questionId, answer]) => ({
        questionId: parseInt(questionId),
        answer,
      }));

      const result = await analyzeDosha(responses);
      setResult(result);
    } catch (error) {
      console.error('Error analyzing dosha:', error);
    }
  };

  const currentQuestion = questions[activeStep];

  if (result) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom>
            Your Dosha Result
          </Typography>
          <Typography variant="h5" color="primary" gutterBottom>
            {result.primaryDosha.toUpperCase()} Type
          </Typography>
          <Typography variant="body1" paragraph>
            {result.description}
          </Typography>
          <Box mt={4}>
            <Typography variant="h6" gutterBottom>
              Recommendations:
            </Typography>
            <ul>
              {result.recommendations.map((rec, index) => (
                <li key={index}>
                  <Typography>{rec}</Typography>
                </li>
              ))}
            </ul>
          </Box>
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              setResult(null);
              setActiveStep(0);
              setAnswers({});
            }}
            sx={{ mt: 2 }}
          >
            Take Test Again
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {questions.map((question) => (
            <Step key={question.id}>
              <StepLabel>Question {question.id}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Typography variant="h6" gutterBottom>
          {currentQuestion.text}
        </Typography>

        <FormControl component="fieldset" sx={{ width: '100%', mt: 2 }}>
          <RadioGroup
            value={answers[currentQuestion.id] || ''}
            onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
          >
            {currentQuestion.options.map((option) => (
              <FormControlLabel
                key={option.value}
                value={option.value}
                control={<Radio />}
                label={option.label}
                sx={{ mb: 1 }}
              />
            ))}
          </RadioGroup>
        </FormControl>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
            sx={{ mr: 1 }}
          >
            Back
          </Button>
          <Box>
            {activeStep === questions.length - 1 ? (
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={!answers[currentQuestion.id] || loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Submit'}
              </Button>
            ) : (
              <Button
                variant="contained"
                color="primary"
                onClick={handleNext}
                disabled={!answers[currentQuestion.id]}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default DoshaTestPage;