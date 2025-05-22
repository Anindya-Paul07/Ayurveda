import { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Box, 
  Tabs, 
  Tab, 
  Card, 
  CardContent,
  Divider,
  CircularProgress,
  useTheme
} from '@mui/material';
import { 
  Timeline, 
  TimelineItem, 
  TimelineSeparator, 
  TimelineConnector, 
  TimelineContent, 
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import { 
  Speed as SpeedIcon, 
  BarChart as BarChartIcon, 
  Timeline as TimelineIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { Line, Bar, Pie } from 'react-chartjs-2';
import 'chart.js/auto';

const MetricsDashboard = () => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [metrics, setMetrics] = useState({
    responseTimes: { rag: [], agent: [] },
    toolUsage: { rag: {}, agent: {} },
    errorRates: { rag: 0, agent: 0 },
    activeAlerts: [],
    systemHealth: { cpu: 0, memory: 0, uptime: 0 }
  });
  const [isLoading, setIsLoading] = useState(true);

  // Mock data - replace with actual API calls
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data - replace with actual API response
        setMetrics({
          responseTimes: {
            rag: [1200, 1450, 1320, 1180, 1250, 1400, 1300],
            agent: [1800, 1750, 1820, 1780, 1850, 1900, 1950]
          },
          toolUsage: {
            rag: {
              'Vector Store': 45,
              'Google Search': 30,
              'Other': 25
            },
            agent: {
              'Vector Store': 35,
              'Google Search': 25,
              'Dosha Analysis': 20,
              'Weather': 10,
              'Other': 10
            }
          },
          errorRates: {
            rag: 2.4,
            agent: 1.8
          },
          activeAlerts: [
            { id: 1, type: 'warning', message: 'High CPU usage (85%)', timestamp: new Date() },
            { id: 2, type: 'error', message: 'API timeout occurred', timestamp: new Date(Date.now() - 1000 * 60 * 5) }
          ],
          systemHealth: {
            cpu: 75,
            memory: 65,
            uptime: 1234567
          }
        });
      } catch (error) {
        console.error('Error fetching metrics:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetrics();
    // Set up polling every 30 seconds
    const interval = setInterval(fetchMetrics, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 0: // Performance
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Response Times (ms)
                  </Typography>
                  <Line
                    data={{
                      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                      datasets: [
                        {
                          label: 'RAG',
                          data: metrics.responseTimes.rag,
                          borderColor: theme.palette.primary.main,
                          backgroundColor: 'rgba(63, 81, 181, 0.1)',
                          tension: 0.3
                        },
                        {
                          label: 'Agent',
                          data: metrics.responseTimes.agent,
                          borderColor: theme.palette.secondary.main,
                          backgroundColor: 'rgba(255, 152, 0, 0.1)',
                          tension: 0.3
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: { position: 'top' },
                        tooltip: { mode: 'index', intersect: false }
                      },
                      hover: { mode: 'nearest', intersect: true },
                      scales: {
                        y: { beginAtZero: true }
                      }
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Error Rates (%)
                  </Typography>
                  <Bar
                    data={{
                      labels: ['RAG', 'Agent'],
                      datasets: [
                        {
                          label: 'Error Rate',
                          data: [metrics.errorRates.rag, metrics.errorRates.agent],
                          backgroundColor: [
                            theme.palette.primary.main,
                            theme.palette.secondary.main
                          ]
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      scales: {
                        y: { beginAtZero: true, max: 100 }
                      }
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );
      
      case 1: // Tool Usage
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    RAG Tool Usage
                  </Typography>
                  <Pie
                    data={{
                      labels: Object.keys(metrics.toolUsage.rag),
                      datasets: [{
                        data: Object.values(metrics.toolUsage.rag),
                        backgroundColor: [
                          theme.palette.primary.main,
                          theme.palette.secondary.main,
                          theme.palette.success.main,
                          theme.palette.warning.main,
                          theme.palette.error.main
                        ]
                      }]
                    }}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: { position: 'right' }
                      }
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Agent Tool Usage
                  </Typography>
                  <Pie
                    data={{
                      labels: Object.keys(metrics.toolUsage.agent),
                      datasets: [{
                        data: Object.values(metrics.toolUsage.agent),
                        backgroundColor: [
                          theme.palette.primary.main,
                          theme.palette.secondary.main,
                          theme.palette.success.main,
                          theme.palette.warning.main,
                          theme.palette.error.main
                        ]
                      }]
                    }}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: { position: 'right' }
                      }
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );
      
      case 2: // System Health
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    System Health
                  </Typography>
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography>CPU Usage</Typography>
                      <Typography>{metrics.systemHealth.cpu}%</Typography>
                    </Box>
                    <Box sx={{ width: '100%', height: 10, bgcolor: 'divider', borderRadius: 5, overflow: 'hidden' }}>
                      <Box 
                        sx={{
                          width: `${metrics.systemHealth.cpu}%`,
                          height: '100%',
                          bgcolor: metrics.systemHealth.cpu > 80 ? 'error.main' : 
                                  metrics.systemHealth.cpu > 60 ? 'warning.main' : 'primary.main',
                          transition: 'all 0.3s'
                        }}
                      />
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography>Memory Usage</Typography>
                      <Typography>{metrics.systemHealth.memory}%</Typography>
                    </Box>
                    <Box sx={{ width: '100%', height: 10, bgcolor: 'divider', borderRadius: 5, overflow: 'hidden' }}>
                      <Box 
                        sx={{
                          width: `${metrics.systemHealth.memory}%`,
                          height: '100%',
                          bgcolor: metrics.systemHealth.memory > 80 ? 'error.main' : 
                                  metrics.systemHealth.memory > 60 ? 'warning.main' : 'primary.main',
                          transition: 'all 0.3s'
                        }}
                      />
                    </Box>
                  </Box>
                  
                  <Box>
                    <Typography>Uptime: {formatUptime(metrics.systemHealth.uptime)}</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Active Alerts
                  </Typography>
                  <Timeline position="alternate">
                    {metrics.activeAlerts.length > 0 ? (
                      metrics.activeAlerts.map((alert) => (
                        <TimelineItem key={alert.id}>
                          <TimelineOppositeContent color="text.secondary">
                            {new Date(alert.timestamp).toLocaleTimeString()}
                          </TimelineOppositeContent>
                          <TimelineSeparator>
                            <TimelineDot color={
                              alert.type === 'error' ? 'error' : 
                              alert.type === 'warning' ? 'warning' : 'success'
                            }>
                              {alert.type === 'error' ? <ErrorIcon /> : 
                               alert.type === 'warning' ? <WarningIcon /> : <CheckCircleIcon />}
                            </TimelineDot>
                            <TimelineConnector />
                          </TimelineSeparator>
                          <TimelineContent>
                            <Typography>{alert.message}</Typography>
                          </TimelineContent>
                        </TimelineItem>
                      ))
                    ) : (
                      <Typography color="text.secondary" sx={{ p: 2 }}>
                        No active alerts
                      </Typography>
                    )}
                  </Timeline>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );
      
      default:
        return null;
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          System Metrics & Analytics
        </Typography>
        <Box>
          <Tabs 
            value={activeTab} 
            onChange={(_, newValue) => setActiveTab(newValue)}
            textColor="primary"
            indicatorColor="primary"
            sx={{ mb: -1 }}
          >
            <Tab label="Performance" icon={<SpeedIcon />} iconPosition="start" />
            <Tab label="Tool Usage" icon={<BarChartIcon />} iconPosition="start" />
            <Tab label="System Health" icon={<TimelineIcon />} iconPosition="start" />
          </Tabs>
        </Box>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
          <CircularProgress />
        </Box>
      ) : (
        renderTabContent()
      )}
    </Container>
  );
};

export default MetricsDashboard;
