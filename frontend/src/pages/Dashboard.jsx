import { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  useTheme, 
  useMediaQuery,
  Divider,
  Paper,
  LinearProgress,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  LocalHospital as LocalHospitalIcon,
  Spa as SpaIcon,
  BarChart as BarChartIcon,
  Speed as SpeedIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { styled } from '@mui/material/styles';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s, box-shadow 0.2s',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[4],
  },
}));

const StatCard = ({ title, value, icon, color, onClick }) => {
  const theme = useTheme();
  
  return (
    <Item 
      onClick={onClick}
      sx={{ 
        cursor: 'pointer',
        borderLeft: `4px solid ${theme.palette[color].main}`,
      }}
    >
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
        <Typography variant="subtitle2" color="text.secondary">
          {title}
        </Typography>
        <Box
          sx={{
            p: 1,
            borderRadius: '50%',
            backgroundColor: `${theme.palette[color].light}30`,
            color: theme.palette[color].main,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </Box>
      </Box>
      <Typography variant="h5" component="div" sx={{ fontWeight: 600, mt: 1 }}>
        {value}
      </Typography>
    </Item>
  );
};

const Dashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  
  // Mock data - replace with actual API calls
  const [stats, setStats] = useState({
    totalSessions: 0,
    activeUsers: 0,
    avgResponseTime: 0,
    accuracy: 0,
  });

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setStats({
        totalSessions: 1245,
        activeUsers: 243,
        avgResponseTime: 1.2,
        accuracy: 87.5,
      });
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  // Chart data
  const responseTimeData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'RAG',
        data: [2.5, 2.3, 2.1, 1.9, 1.7, 1.5],
        borderColor: theme.palette.primary.main,
        backgroundColor: `${theme.palette.primary.main}20`,
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Agentic',
        data: [1.8, 1.6, 1.5, 1.4, 1.3, 1.2],
        borderColor: theme.palette.secondary.main,
        backgroundColor: `${theme.palette.secondary.main}20`,
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const accuracyData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'RAG',
        data: [75, 77, 79, 81, 83, 85],
        backgroundColor: `${theme.palette.primary.main}80`,
      },
      {
        label: 'Agentic',
        data: [82, 83, 84, 85, 86, 87.5],
        backgroundColor: `${theme.palette.secondary.main}80`,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
    maintainAspectRatio: false,
  };

  const barOptions = {
    ...chartOptions,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value) => `${value}%`,
        },
      },
    },
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Compare the performance of RAG and Agentic approaches in Ayurvedic analysis
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Sessions"
            value={stats.totalSessions.toLocaleString()}
            icon={<TrendingUpIcon />}
            color="primary"
            onClick={() => navigate('/metrics')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Users"
            value={stats.activeUsers}
            icon={<SpeedIcon />}
            color="secondary"
            onClick={() => navigate('/users')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg. Response Time"
            value={`${stats.avgResponseTime}s`}
            icon={<TrendingUpIcon />}
            color="success"
            onClick={() => navigate('/metrics/performance')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Accuracy"
            value={`${stats.accuracy}%`}
            icon={<BarChartIcon />}
            color="info"
            onClick={() => navigate('/metrics/accuracy')}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Item>
            <Typography variant="h6" gutterBottom>
              Response Time (seconds)
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box sx={{ height: 300 }}>
              <Line data={responseTimeData} options={chartOptions} />
            </Box>
          </Item>
        </Grid>
        <Grid item xs={12} md={6}>
          <Item>
            <Typography variant="h6" gutterBottom>
              Accuracy Comparison (%)
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box sx={{ height: 300 }}>
              <Bar data={accuracyData} options={barOptions} />
            </Box>
          </Item>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Item 
            onClick={() => navigate('/tools/dosha')}
            sx={{ 
              cursor: 'pointer',
              '&:hover': {
                borderLeft: `4px solid ${theme.palette.primary.main}`,
              },
            }}
          >
            <Box display="flex" alignItems="center" mb={2}>
              <PsychologyIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Dosha Analysis
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" paragraph>
              Compare RAG and Agentic approaches for dosha analysis
            </Typography>
            <Box display="flex" alignItems="center" mt={1}>
              <Box width="100%" mr={1}>
                <LinearProgress 
                  variant="determinate" 
                  value={75} 
                  sx={{ height: 8, borderRadius: 5 }} 
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                75%
              </Typography>
            </Box>
          </Item>
        </Grid>

        <Grid item xs={12} md={4}>
          <Item 
            onClick={() => navigate('/tools/symptoms')}
            sx={{ 
              cursor: 'pointer',
              '&:hover': {
                borderLeft: `4px solid ${theme.palette.secondary.main}`,
              },
            }}
          >
            <Box display="flex" alignItems="center" mb={2}>
              <LocalHospitalIcon color="secondary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Symptom Analyzer
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" paragraph>
              Analyze symptoms using both approaches
            </Typography>
            <Box display="flex" alignItems="center" mt={1}>
              <Box width="100%" mr={1}>
                <LinearProgress 
                  variant="determinate" 
                  value={82} 
                  color="secondary"
                  sx={{ height: 8, borderRadius: 5 }} 
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                82%
              </Typography>
            </Box>
          </Item>
        </Grid>

        <Grid item xs={12} md={4}>
          <Item 
            onClick={() => navigate('/tools/herbs')}
            sx={{ 
              cursor: 'pointer',
              '&:hover': {
                borderLeft: `4px solid ${theme.palette.success.main}`,
              },
            }}
          >
            <Box display="flex" alignItems="center" mb={2}>
              <SpaIcon color="success" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Herb Recommender
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" paragraph>
              Get herb recommendations with comparison
            </Typography>
            <Box display="flex" alignItems="center" mt={1}>
              <Box width="100%" mr={1}>
                <LinearProgress 
                  variant="determinate" 
                  value={68} 
                  color="success"
                  sx={{ height: 8, borderRadius: 5 }} 
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                68%
              </Typography>
            </Box>
          </Item>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
