import { useState } from 'react';
import { Box, Container, Tabs, Tab, useTheme } from '@mui/material';
import { Chat as ChatIcon, Spa as DoshaIcon, Favorite as RecommendationIcon } from '@mui/icons-material';
import ChatPage from '../pages/ChatPage';
import DoshaAnalysis from '../pages/DoshaAnalysis';
import PersonalRecommendations from '../pages/PersonalRecommendations';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`main-tabpanel-${index}`}
      aria-labelledby={`main-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `main-tab-${index}`,
    'aria-controls': `main-tabpanel-${index}`,
  };
}

export default function MainLayout() {
  const [value, setValue] = useState(0);
  const theme = useTheme();

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={value}
          onChange={handleChange}
          aria-label="main navigation tabs"
          variant="scrollable"
          scrollButtons="auto"
          textColor="primary"
          indicatorColor="primary"
        >
          <Tab 
            icon={<ChatIcon />} 
            label="Chat" 
            iconPosition="start" 
            {...a11yProps(0)} 
            sx={{ minHeight: 64 }}
          />
          <Tab 
            icon={<DoshaIcon />} 
            label="Dosha Analysis" 
            iconPosition="start" 
            {...a11yProps(1)} 
            sx={{ minHeight: 64 }}
          />
          <Tab 
            icon={<RecommendationIcon />} 
            label="Personal Recommendations" 
            iconPosition="start" 
            {...a11yProps(2)} 
            sx={{ minHeight: 64 }}
          />
        </Tabs>
      </Box>

      <TabPanel value={value} index={0}>
        <ChatPage />
      </TabPanel>
      <TabPanel value={value} index={1}>
        <DoshaAnalysis />
      </TabPanel>
      <TabPanel value={value} index={2}>
        <PersonalRecommendations />
      </TabPanel>
    </Container>
  );
}
